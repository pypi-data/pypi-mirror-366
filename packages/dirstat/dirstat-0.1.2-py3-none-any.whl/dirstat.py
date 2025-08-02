#!/usr/bin/env python3
"""
A single-file no-dependency Python program (also usable as a library module) to efficiently gather directory statistics.
"""
from __future__ import annotations

import csv
import logging
import os
import re
import stat
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from time import time_ns
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable, Literal, TextIO

__prog__ = 'dirstat'

__version_tuple__ = (0, 1, 2)
__version__ = f'{__version_tuple__[0]}.{__version_tuple__[1]}.{__version_tuple__[2]}' + ('-' + '-'.join(str(part) for part in __version_tuple__[3:]) if len(__version_tuple__) > 3 else '') # type: ignore


def _add_arguments(parser: ArgumentParser):
    parser.add_argument('root_dir', nargs='?', type=Path, help="Root directory (default: %(default)s).")
    parser.add_argument('--no-recurse', action='store_true', help="Analyze only the root directory (not its children).")
    parser.add_argument('-x', '--one-file-system', action='store_true', help="Don't cross filesystem boundaries.")
    parser.add_argument('-o', '--out', help="Output file (CSV).") #ROADMAP: or SQLite
    
    group = parser.add_argument_group(title='command options')
    group.add_argument('--extensions', action='store_true', help="Group by extensions instead of path.")
    
    group = parser.add_argument_group(title='display options')
    group.add_argument('--max-depth', type=int, help="Maximum depth to export.")
    group.add_argument('--sort', choices=['size', 'mtime', 'files', 'dirs', 'path'], default=None, help="Sort by the given column.")
    group.add_argument('--bytes', action='store_true', help="Display sizes in bytes.")

    group = parser.add_argument_group(title='type filtering options')
    mutex = group.add_mutually_exclusive_group()
    mutex.add_argument('-a', '--all', action='store_const', dest='list_path_types', const='all')
    mutex.add_argument('-f', '--file', action='store_const', dest='list_path_types', const='file')
    mutex.add_argument('-d', '--dir', action='store_const', dest='list_path_types', const='dir')
    mutex.add_argument('--issue', action='store_const', dest='list_path_types', const='issue')
    mutex.add_argument('--recall', action='store_const', dest='list_path_types', const='recall')
    mutex.add_argument('--no-recall', action='store_const', dest='list_path_types', const='no-recall')

    group = parser.add_argument_group(title='other filtering options')
    group.add_argument('-i', '--include', nargs='*', help="Inclusion pattern(s). Start with \".\" for an extension, with \"^\" for a regexp.") #ROADMAP
    group.add_argument('-e', '--exclude', nargs='*', help="Exlusion pattern(s). Start with \".\" for an extension, with \"^\" for a regexp.") #ROADMAP


def _handle(root_dir: str|os.PathLike|None = None, **kwargs):
    additional_kwargs = {}
    if paths_type := kwargs.get('list_path_types'):
        op_class = ListPathsOperation
        additional_kwargs['paths_type'] = paths_type
    elif kwargs.get('extensions'):
        op_class = GroupContentOperation
        additional_kwargs['group_by'] = 'extension'
    else:
        op_class = DirStatOperation
    
    with op_class(root_dir, recurse=True if kwargs.get('no_recurse') else None, one_file_system=kwargs.get('one_file_system'), max_depth=kwargs.get('max_depth'), sort_column=kwargs.get('sort'), human=False if kwargs.get('bytes') else True, terminal=False if Color.NO_COLORS else True, out=kwargs.get('.out'), **additional_kwargs) as op:
        op.run()

setattr(_handle, 'add_arguments', _add_arguments)


def _main():
    # Configure logging
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', '').upper() or 'INFO', format=f'%(levelname)s {Color.GRAY}[%(name)s]{Color.RESET} %(message)s')
    logging.addLevelName(logging.CRITICAL, f"{Color.BG_RED}CRITICAL{Color.RESET}")
    logging.addLevelName(logging.ERROR, f"{Color.RED}ERROR{Color.RESET}")
    logging.addLevelName(logging.WARNING, f"{Color.YELLOW}WARNING{Color.RESET}")
    logging.addLevelName(logging.INFO, f"{Color.CYAN}INFO{Color.RESET}")
    logging.addLevelName(logging.DEBUG, f"{Color.GRAY}DEBUG{Color.RESET}")

    # Define command line application
    parser = ArgumentParser(prog=__prog__, description=dedent(__doc__ or ''), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=f"{parser.prog} {__version__}")
    _add_arguments(parser)

    # Parse and run command line application
    args = parser.parse_args()        
    _handle(**vars(args))      


class DirStatOperation:
    #region Lifecycle
    def __init__(self, root_dir: str|os.PathLike|None = None, *, recurse: bool|None = None, one_file_system: bool|None = None, max_depth: int|None = None, sort_column: str|None = None, human: bool|None = None, terminal: bool|None = None, out: str|os.PathLike|TextIO|None = None):
        if not root_dir:
            root_dir = Path.cwd()
        elif not isinstance(root_dir, Path):
            root_dir = Path(root_dir)
        else:
            root_dir = root_dir

        if sys.platform == 'win32' and re.match(r'^[^"]+"$', str(root_dir)): # Fix path passed by Powershell and ending with a backslash
            root_dir = root_dir.with_name(root_dir.name[:-1])
        self.root_dir = root_dir

        self.recurse: bool = False
        if recurse is None or recurse:
            self.recurse = True

        self.dev: int|None = None
        if one_file_system:
            self.dev = os.stat(self.root_dir).st_dev
        
        if max_depth is None:
            max_depth = 1
        self.max_depth = max_depth

        self.sort_column = sort_column
        self.human = human
        self.terminal = terminal
        self.out = out

        self._logger = logging.getLogger(f'{__name__}.{self.__class__.__qualname__}')
        self._exporter: Exporter|None = None

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type = None, exc = None, exc_tb = None):
        self.close()

    def close(self):
        if self._exporter is not None:
            self._exporter.close()
            self._exporter = None

    #endregion

    #region Designed to be overriden

    def get_headers(self, *, path_length_indication: int|None):
        headers = [
            Header('path', path_length_indication if path_length_indication is not None and path_length_indication > 40 else 40),
            HeaderSeparator,
            Header('nature', display='nat', length=3),
            HeaderSeparator,
            Header('files', length=7, format='{0:,.0f}', right_aligned=True),
            Header('dirs', length=7, format='{0:,.0f}', right_aligned=True),
            Header('size', length=10, format=self.size_format, right_aligned=True),
            Header('mtime', length=10, format=self.mtime_format, right_aligned=True),
        ]
        if sys.platform == 'win32':
            headers += [
                HeaderSeparator,
                Header('recalls', length=7, format='{0:,.0f}', right_aligned=True),
                Header('recalls_size', display='(size)', length=10, format=self.size_format, right_aligned=True),
            ]
        headers += [
            HeaderSeparator,
            Header('issues', format=self.issues_format),
        ]
        return headers
    
    def is_match(self, item: PathInfo) -> bool:
        return True
    
    def get_match_row(self, item: PathInfo) -> dict[str,Any]|None:
        return {
            'path': item.path,
            'nature': item.nature.value + ('R' if item.total_recall_count > 0 else '-'),    
            **self._get_common_data(item)
        }
    
    def get_total_row(self, item: PathCounter) -> dict[str,Any]|None:
        return {
            'path': "Total (NO RECURSE)" if not self.recurse else "Total",
            'nature': '',    
            **self._get_common_data(item)
        }
    
    def _get_common_data(self, item: PathInfo|PathCounter) -> dict[str,Any]:
        total_file_count = item.total_count - item.total_dir_count

        data = { 
            'files': total_file_count,
            'dirs': item.total_dir_count,
            'size': item.total_size,
            'mtime': item.last_mtime,
            'issues': item.total_issues,
        }

        if sys.platform == 'win32':
            data = {
                **data,
                'recalls': item.total_recall_count,
                'recalls_size': item.total_recall_size,
            }

        return data

    #endregion

    #region Common behaviour

    @cached_property
    def size_format(self) -> str|Callable[[Any],str]|None:
        return human_bytes if self.human else '{0:,.0f}'

    def mtime_format(self, timestamp: int):
        if timestamp == 0:
            return ''
        if not self.human:
            return timestamp
        dt = datetime.fromtimestamp(timestamp)
        if dt.date() != datetime.now():
            return dt.strftime('%Y-%m-%d')
        else:
            return dt.strftime('%H-%M-%S')

    def issues_format(self, issues: dict[str,str]):
        return ', '.join(f'{key}: {issues[key]}' for key in sorted(issues.keys()))
    
    @property
    def exporter(self) -> Exporter:
        if self._exporter is None:
            raise ValueError("Exporter not built")
        return self._exporter
    
    def build_exporter(self, paths: list[Path]):
        path_length_indication = max(len(path.name) for path in paths)
        headers = self.get_headers(path_length_indication=path_length_indication)
        if self.out and not self.out in {sys.stdout, sys.stderr}:
            exporter_class = CsvExporter
        else:
            exporter_class = Exporter
        return exporter_class(headers, out=self.out, sort_column=self.sort_column, sort_reverse=self.sort_column in {'size', 'mtime', 'files'}, normalize_paths=self.root_dir)

    def run(self) -> PathCounter:
        paths = sorted(self.root_dir.iterdir())
        self._exporter = self.build_exporter(paths)
        self._exporter.export_headers()
        self._exporter.export_separator()
    
        try:
            counter = self.analyze_directory(self.root_dir, depth=1, dir_paths=paths)
        finally:
            erase_transient(stdout=True)

        total_row = self.get_total_row(counter)
        if total_row is not None:
            self._exporter.export_separator()
            if not self._exporter.export_total(total_row):
                message = "Total: " + (', '.join(f"{key}={value}" for key, value in total_row.items() if not isinstance(value, str) or not value.startswith('Total')))
                self._logger.info(message)
        
        return counter
    
    def analyze_directory(self, dir: Path, *, depth: int, dir_paths: Iterable[Path]|None = None) -> PathCounter:
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Analyze directory: %s (depth: %d)", dir, depth)
        else:
            if self.terminal:
                write_transient(f"{Color.GRAY}Analyze {dir} …{Color.RESET}\n", delay=1.0)
               
        counter = PathCounter()

        if dir_paths is None:
            dir_paths = sorted(dir.iterdir())

        for path in dir_paths:
            info = self.analyze_path(path)

            if self.recurse and info.is_dir:
                if self.dev and info.dev and info.dev != self.dev:
                    # Other file system (display for information)
                    row = self.get_match_row(info)
                    if row is not None and (self.max_depth == -1 or depth <= self.max_depth):
                        erase_transient()
                        self.exporter.append_row({**row, 'dev': info.dev})
                    continue                  
                else:
                    try:
                        info.dir_counter = self.analyze_directory(path, depth=depth + 1)
                        counter.append(info.dir_counter)
                    except Exception as err:
                        info.issues.append(f"{type(err).__name__}: {str(err)}")

            info.is_match = self.is_match(info)

            if info.is_match:
                row = self.get_match_row(info)
                if row is not None and (self.max_depth == -1 or depth <= self.max_depth):
                    erase_transient()
                    self.exporter.append_row(row)

            counter.append(info)
        
        return counter
    
    def analyze_path(self, path: Path) -> PathInfo:
        info = PathInfo(path)   

        try:
            # Nature and size   
            st = path.lstat()
            if stat.S_ISLNK(st.st_mode):
                info.nature = PathNature.SYMLINK
                info.issues.append(f"link: {os.readlink(path)}")
                info.mtime = int(st.st_mtime)
            elif stat.S_ISDIR(st.st_mode):
                info.nature = PathNature.DIRECTORY
            elif stat.S_ISREG(st.st_mode):
                info.nature = PathNature.REGULAR_FILE
                info.size = st.st_size
                info.mtime = int(st.st_mtime)
            else:
                info.nature = PathNature.OTHER
                info.size = st.st_size
                info.mtime = int(st.st_mtime)
                info.issues.append(f"type: {hex(st.st_mode)}")

            # Determine filesystem
            if self.dev:
                info.dev = st.st_dev
                if info.dev and info.dev != self.dev:
                    info.nature = PathNature.OTHER # Other file system
                    info.issues.append(f"other-fs: {hex(info.dev)}")

            # Platform specific
            if sys.platform == 'win32':
                info.is_recall = False
                if info.nature != PathNature.DIRECTORY:
                    attrs = get_win32_file_attributes(info.path)
                    if attrs & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS:
                        info.is_recall = True
        
        except Exception as err:
            info.issues.append(f"{type(err).__name__}: {str(err)}")
            
        return info
    
    #endregion


class GroupContentOperation(DirStatOperation):
    def __init__(self, root_dir: str|os.PathLike|None = None, *, group_by: Literal['extension'] = 'extension', recurse: bool|None = None, one_file_system: bool|None = None, max_depth: int|None = None, sort_column: str|None = None, **options):
        self.group_by = group_by        
        if sort_column is None:
            sort_column = self.group_by
        super().__init__(root_dir, recurse=recurse, one_file_system=one_file_system, max_depth=max_depth, sort_column=sort_column, **options)
        self._counters: dict[str, PathCounter] = {}

    def get_headers(self, *, path_length_indication: int|None):
        headers = super().get_headers(path_length_indication=path_length_indication)
        return [Header(self.group_by, 20), *headers[3:]] # replace path, remove nature

    def get_match_row(self, item: PathInfo):
        group = getattr(item, self.group_by)
        if not (counter := self._counters.get(group)):
            counter = PathCounter()
            self._counters[group] = counter
        counter.append(item)
        return None
    
    def get_total_row(self, item: PathCounter):
        for group, counter in self._counters.items():
            self.exporter.append_row({
                self.group_by: group,
                **self._get_common_data(counter)
            })
        
        return {
            self.group_by: "Total (NO RECURSE)" if not self.recurse else "Total",
            **self._get_common_data(item)
        }


class ListPathsOperation(DirStatOperation):
    def __init__(self, root_dir: str|os.PathLike|None = None, *, paths_type: Literal['all','file','dir','issue','recall','no-recall'], recurse: bool|None = None, one_file_system: bool|None = None, max_depth: int|None = None, sort_column: str|None = None, **options):
        if max_depth is None:
            max_depth = -1
        super().__init__(root_dir, recurse=recurse, one_file_system=one_file_system, max_depth=max_depth, sort_column=sort_column, **options)
        self.paths_type = paths_type

    def get_headers(self, *, path_length_indication: int|None):
        return [
            Header('path', path_length_indication if path_length_indication is not None and path_length_indication > 60 else 60),
            HeaderSeparator,
            Header('nature', display='nat', length=3),
            HeaderSeparator,
            Header('size', length=12, format=self.size_format, right_aligned=True),
            Header('mtime', length=10, format=self.mtime_format, right_aligned=True),
            HeaderSeparator,
            Header('issues', format=self.issues_format),
        ]
    
    def is_match(self, item: PathInfo) -> bool:
        if self.paths_type == 'file':
            return item.nature == PathNature.REGULAR_FILE
        elif self.paths_type == 'dir':
            return item.nature == PathNature.DIRECTORY
        elif self.paths_type == 'issue':
            return any(item.total_issues)
        elif self.paths_type == 'recall':
            return item.is_recall or False
        elif self.paths_type == 'no-recall':
            return not item.is_recall and not item.is_dir
        else:
            return True

    def get_match_row(self, item: PathInfo):
        return {
            'path': item.path,
            'nature': item.nature.value + ('R' if item.total_recall_count > 0 else '-'),
            **self._get_common_data(item)
        }
    
    def get_total_row(self, item: PathCounter):
        return {
            'path': ("Total (NO RECURSE)" if not self.recurse else "Total") + f" - {item.total_match_count:,} matching elements",
            'nature': '',
            **self._get_common_data(item)
        }
    
    def _get_common_data(self, item: PathInfo|PathCounter) -> dict[str,Any]:
        return { 
            'size': item.total_match_size,
            'mtime': item.last_match_mtime,
            'issues': item.total_issues,
        }


class PathInfo:
    def __init__(self, path: Path):
        self.path: Path = path
        self.dir_counter: PathCounter|None = None
        
        self.nature: PathNature = PathNature.UNKNOWN
        self.size = 0
        self.mtime = 0
        self.dev: int|None = None
   
        self.is_recall: bool|None = None
        self.is_match = False

        self.issues: list[str] = []

    @classmethod
    def split_issue(cls, issue: str) -> tuple[str,str]:
        if (pos := issue.find(':')) >= 0:
            return issue[:pos].strip(), issue[pos+1:].strip()
        else:
            return issue.strip(), ''
    
    @property
    def is_dir(self):
        return self.nature == PathNature.DIRECTORY

    @cached_property
    def extension(self):
        return get_normalized_extension(self.path)
    
    @property
    def total_count(self):
        return 1 + (self.dir_counter.total_count if self.dir_counter is not None else 0)
    
    @property
    def total_size(self):
        return self.size + (self.dir_counter.total_size if self.dir_counter is not None else 0)
    
    @property
    def last_mtime(self):
        mtime = self.mtime
        if self.dir_counter is not None:
            if mtime < self.dir_counter.last_mtime:
                mtime = self.dir_counter.last_mtime
        return mtime
    
    @property
    def total_dir_count(self):
        return (1 if self.nature == PathNature.DIRECTORY else 0) + (self.dir_counter.total_dir_count if self.dir_counter is not None else 0)
    
    @property
    def total_recall_count(self):
        return (1 if self.is_recall else 0) + (self.dir_counter.total_recall_count if self.dir_counter is not None else 0)
    
    @property
    def total_recall_size(self):
        return (self.size if self.is_recall else 0) + (self.dir_counter.total_recall_size if self.dir_counter is not None else 0)
    
    @property
    def total_match_count(self):
        return (1 if self.is_match else 0) + (self.dir_counter.total_match_count if self.dir_counter is not None else 0)
    
    @property
    def total_match_size(self):
        return (self.size if self.is_match else 0) + (self.dir_counter.total_match_size if self.dir_counter is not None else 0)
    
    @property
    def last_match_mtime(self):
        mtime = self.mtime if self.is_match else 0
        if self.dir_counter is not None:
            if mtime < self.dir_counter.last_match_mtime:
                mtime = self.dir_counter.last_match_mtime
        return mtime
    
    @property
    def total_issues(self) -> dict[str,str|int]:
        issues: dict[str,str|int] = {}
        for issue in self.issues:
            key, value = self.split_issue(issue)
            if not key in issues:
                issues[key] = value
            else:
                issues[key] = f"{issues[key]}|{value}"

        if self.dir_counter is not None:
            for key, count in self.dir_counter.total_issues.items():
                if not key in issues:
                    issues[key] = count
                else:
                    issues[key] = 1 + count
        
        return issues


class PathCounter:
    def __init__(self):
        self.total_count = 0
        self.total_size = 0
        self.last_mtime = 0
        
        self.total_dir_count = 0
        self.total_recall_count = 0
        self.total_recall_size = 0

        self.total_match_count = 0
        self.total_match_size = 0
        self.last_match_mtime = 0

        self.total_issues: dict[str, int] = {}

    def append(self, item: PathInfo|PathCounter):
        if isinstance(item, PathInfo):
            self.total_count += 1
            self.total_size += item.size
            if self.last_mtime < item.mtime:
                self.last_mtime = item.mtime
            
            if item.nature == PathNature.DIRECTORY:
                self.total_dir_count += 1

            if item.is_recall:
                self.total_recall_count += 1
                self.total_recall_size += item.size
            
            if item.is_match:
                self.total_match_count += 1
                self.total_match_size += item.size
                if self.last_match_mtime < item.mtime:
                    self.last_match_mtime = item.mtime

            for issue in item.issues:
                key, _ = item.split_issue(issue)
                if not key in self.total_issues:
                    self.total_issues[key] = 1
                else:
                    self.total_issues[key] += 1
        else:
            self.total_count += item.total_count
            self.total_size += item.total_size
            if self.last_mtime < item.last_mtime:
                self.last_mtime = item.last_mtime
            
            self.total_dir_count += item.total_dir_count
            
            self.total_recall_count += item.total_recall_count
            self.total_recall_size += item.total_recall_size

            self.total_match_count += item.total_match_count
            self.total_match_size += item.total_match_size
            if self.last_match_mtime < item.last_match_mtime:
                self.last_match_mtime = item.last_match_mtime

            for name, count in item.total_issues.items():
                if not name in self.total_issues:
                    self.total_issues[name] = count
                else:
                    self.total_issues[name] += count

    @property
    def total_file_count(self):
        return self.total_count - self.total_dir_count


class PathNature(Enum):
    DIRECTORY = 'd'
    SYMLINK = 'l'
    REGULAR_FILE = 'f'
    OTHER = 'o'
    UNKNOWN = '?'


class Exporter:
    def __init__(self, headers: list[Header|HeaderSeparator|type[HeaderSeparator]], *, out: str|os.PathLike|TextIO|None = None, encoding = 'utf-8', newline = None, sort_column: str|None = None, sort_reverse = False, normalize_paths: bool|Path = False):
        self.headers = headers
        self.sort_column = sort_column
        self.sort_reverse = sort_reverse
        self.normalize_paths = normalize_paths
        
        self._logger = logging.getLogger(f'{__name__}.{self.__class__.__qualname__}')

        if not out:
            out = sys.stdout

        self.out_name: str
        self.out_file: TextIO
        if isinstance(out, (str,os.PathLike)):            
            parent = os.path.dirname(out)
            if parent and not os.path.exists(parent):
                os.makedirs(parent)

            self.out_name = str(out) if not isinstance(out, str) else out
            self.out_file = open(out, 'w', encoding=encoding, newline=newline)
            self._must_close_out = True
        else:
            self.out_name = f"<{getattr(out, 'name', None) or str(out)}>"
            self.out_file = out # type: ignore
            self._must_close_out = False

        if not self.out_file in {sys.stdout, sys.stderr}:
            self._logger.info("Export to %s …", self.out_name)

        self._delayed_normalized_data: list[dict[str,Any]] = []

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type = None, exc = None, exc_tb = None):
        self.close()

    def close(self):
        self.flush()
        if self._must_close_out:
            if not self.out_file.closed:
                self.out_file.close()
            self._must_close_out = False

    def export_headers(self) -> bool:
        return self.export_row('headers') # type: ignore

    def export_separator(self, char = '-') -> bool:
        return self.export_row(char) # type: ignore

    def export_total(self, data: dict[Any,Any]) -> bool:
        return self.export_row(data, rowtype='total')

    def export_row(self, data: dict[Any,Any], *, rowtype: str|None = None) -> bool:
        self.flush()
        if not isinstance(data, str):
            data = self._normalize_data(data)
        exported = self._write(data, rowtype=rowtype)
        self.out_file.flush()
        return exported

    def append_row(self, data: dict[Any,Any]):
        normalized_data = self._normalize_data(data)
        if self.sort_column:
            self._delayed_normalized_data.append(normalized_data)
        else:
            self.export_row(data)

    def flush(self):
        if not self._delayed_normalized_data:
            return
        
        if self.sort_column:
            sort_column = self.sort_column
            sort_reverse = self.sort_reverse
            self._delayed_normalized_data.sort(key=lambda data: data[sort_column], reverse=sort_reverse)

        for delayed in self._delayed_normalized_data:
            self._write(delayed)
        
        self._delayed_normalized_data.clear()
        self.out_file.flush()

    def _write(self, data: dict[str,Any]|str, *, rowtype: str|None = None) -> bool:        
        str_row = self._get_str_row(data)
        self.out_file.write(str_row)
        return True
    
    def _normalize_data(self, data: dict[Any,Any]) -> dict[str,Any]:
        """
        Normalize the data directory to allow sorting.
        """
        normalized_data = {}
        for key, value in data.items():
            if not isinstance(key, str):
                key = str(key)
            
            if self.normalize_paths and isinstance(value, Path):
                if isinstance(self.normalize_paths, Path):
                    try:
                        value = value.relative_to(self.normalize_paths)
                    except ValueError:
                        value = value.absolute()
                    value = value.as_posix()

            normalized_data[key] = value
        return normalized_data

    def _get_str_row(self, data: dict[str,Any]|str) -> str:
        result = ''
        last_was_separator: bool|None = None
        excess_length = 0

        used_keys: set[str] = set()
        for header in self.headers:
            if isinstance(header, HeaderSeparator) or (isinstance(header, type) and issubclass(header, HeaderSeparator)):
                result += header.display
                last_was_separator = True
            else:
                value = ''
                if data  == 'headers':
                    value = header.display if header.display is not None else header.name
                elif isinstance(data, str):
                    value = data[0] * (header.length if header.length is not None else 5)
                else:
                    if header.name in data:
                        used_keys.add(header.name)
                        value = data[header.name]
                        if value is not None:
                            if header.format is not None:
                                if isinstance(header.format, str):
                                    value = header.format.format(value)
                                else:
                                    value = header.format(value)
                            if not isinstance(value, str):
                                value = str(value)
                
                if header.length is not None:
                    if len(value) < header.length:
                        add_length = (header.length - len(value))
                        if excess_length > 0:
                            if excess_length >= add_length:
                                excess_length -= add_length
                                add_length = 0
                            else:
                                add_length -= excess_length
                                excess_length = 0

                        if header.right_aligned:
                            value = (' ' * add_length) + value
                        else:
                            value = value + (' ' * add_length)

                    elif len(value) > header.length:
                        excess_length += len(value) - header.length

                if last_was_separator is not None:
                    if last_was_separator:
                        result += ''
                    else:
                        result += '  '

                result += value
                last_was_separator = False

        if not isinstance(data, str):
            for key, value in data.items():
                if not key in used_keys:
                    result += f' {key}={value}'

        return result.rstrip() + '\n'
    

class CsvExporter(Exporter):
    def __init__(self, headers: list[Header|HeaderSeparator|type[HeaderSeparator]], *, out: str|os.PathLike|TextIO|None = None, delimiter: str|None = None, encoding = 'utf-8-sig', sort_column: str|None = None, sort_reverse = False, normalize_paths: bool|Path = False):
        super().__init__(headers, out=out, encoding=encoding, newline='', sort_column=sort_column, sort_reverse=sort_reverse, normalize_paths=normalize_paths)
        if delimiter is None:
            delimiter = os.environ.get('CSV_DELIMITER', '') or ','
        self.writer = csv.writer(self.out_file, delimiter=delimiter)

    def _write(self, data: dict[str,Any]|str, *, rowtype: str|None = None) -> bool:
        if rowtype == 'total':
            return False # ignore
        elif data == 'headers':
            row = [header.name for header in self.headers if isinstance(header, Header)]
        elif isinstance(data, str):
            return False # ignore (separator)
        else:
            row = [data.get(header.name) for header in self.headers if isinstance(header, Header)]
            
        self.writer.writerow(row)
        return True


@dataclass
class Header:
    name: str
    length: int|None = None
    display: str|None = None
    right_aligned: bool = False
    format: str|Callable|None = None


@dataclass
class HeaderSeparator:
    display: str = ' | '


#region Win32 helpers

if sys.platform == 'win32':
    from ctypes import WinDLL, WinError, get_last_error

    INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
    
    FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x00400000

    _kernel32 = WinDLL('kernel32', use_last_error=True)

    def get_win32_file_attributes(path: str|os.PathLike):
        path = '\\\\?\\' + os.path.abspath(os.path.normpath(path))

        attrs = _kernel32.GetFileAttributesW(path)
        if attrs < 0:
            attrs += 2**32
        if attrs == INVALID_FILE_ATTRIBUTES:
            raise WinError(get_last_error())
        return attrs

#endregion


#region General helpers

def get_normalized_extension(path: Path):
    if path.is_dir():
        return ''

    lower = os.path.basename(path if isinstance(path, str) else str(path)).lower().strip()
    if lower.endswith('.tar.gz'):
        return '.tar.gz'
    
    remaining, ext = os.path.splitext(lower)
    if re.match(r'^\.[0-9]{3}$', ext):
        if m := re.match(r'^.+(\.[0-9]{2,3})$', remaining):
            return m[1]

    return ext


def human_bytes(value: int, *, unit: str = 'iB', divider: int = 1024, decimals: int = 1, max_multiple: str|None = None) -> str:
    """
    Get a human-readable representation of a number of bytes.
    
    :param max_multiple: may be `K`, `M`, `G` or `T`.
    """
    return human_number(value, unit=unit, divider=divider, decimals=decimals, max_multiple=max_multiple)


def human_number(value: int, *, unit: str = '', divider: int = 1000, decimals: int = 1, max_multiple: str|None = None) -> str:
    """
    Get a human-readable representation of a number.

    :param max_multiple: may be `K`, `M`, `G` or `T`.
    """
    if value is None:
        return None

    suffixes = []

    # Append non-multiple suffix (bytes)
    # (if unit is 'iB' we dont display the 'i' as it makes more sens to display "123 B" than "123 iB")
    if unit:
        suffixes.append(' ' + (unit[1:] if len(unit) >= 2 and unit[0] == 'i' else unit))
    else:
        suffixes.append('')

    # Append multiple suffixes
    for multiple in ['K', 'M', 'G', 'T']:
        suffixes.append(f' {multiple}{unit}')
        if max_multiple and max_multiple.upper() == multiple:
            break

    i = 0
    suffix = suffixes[i]
    divided_value = value

    while divided_value > 1000 and i < len(suffixes) - 1:
        divided_value /= divider
        i += 1
        suffix = suffixes[i]

    # Format value
    formatted_value = ('{0:,.'+('0' if i == 0 else str(decimals))+'f}').format(divided_value)
    
    # Display formatted value with suffix
    return f'{formatted_value}{suffix}'


_transient_to_erase: dict[bool, list[int]] = {False: [], True: []}
_last_transient:  dict[bool, float|None] = {False: None, True: None}

def write_transient(text: str, *, stdout = False, newline=False, delay: float|int|None = None):
    """
    Write text to the terminal, keeping track of what was written, so that it can be erased later.

    Text lines are stripped to terminal column length.
    """    
    t = time_ns()
    if delay is not None:
        t0 = _last_transient[stdout]
        if t0 is not None and (t - t0) / 1E9 < delay:
            return

    file = sys.stdout if stdout else sys.stderr
    if not sys.stderr.isatty(): # Ignore if we're not on a terminal
        return
    
    erase_transient(stdout=stdout)
    columns, _ = os.get_terminal_size()

    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.rstrip()
        
        nb_chars = len(line)
        if nb_chars > columns:
            line = line[:columns-1] + '…'
            nb_chars = columns

        _transient_to_erase[stdout].insert(0, nb_chars)

        file.write(line)
        if newline or i < len(lines) - 1:
            file.write('\n')

    if newline:
        _transient_to_erase[stdout].insert(0, 0)
    
    file.flush()
    _last_transient[stdout] = t


def erase_transient(*, stdout = False):
    """
    Erase text written using :func:`write_transient`.

    Text lines are stripped to terminal column length.
    """
    if not _transient_to_erase[stdout]:
        return
    
    file = sys.stdout if stdout else sys.stderr
    for i, nb_chars in enumerate(_transient_to_erase[stdout]):
        if i == 0:
            file.write('\r') # move to beginning of line
        else:
            file.write('\033[F') # move to beginning of previous line
        file.write(' ' * nb_chars)
    file.write('\r')

    _transient_to_erase[stdout].clear()
    _last_transient[stdout] = None


class Color:
    RESET = '\033[0m'

    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    GRAY = LIGHT_BLACK = '\033[0;90m'
    BG_RED = '\033[0;41m'

    # Disable coloring if environment variable NO_COLORS is set to 1 or if stderr is piped/redirected
    NO_COLORS = False
    if os.environ.get('NO_COLORS', '').lower() in {'1', 'yes', 'true', 'on'} or not sys.stderr.isatty():
        NO_COLORS = True
        for _ in dir():
            if isinstance(_, str) and _[0] != '_' and _ not in ['NO_COLORS']:
                locals()[_] = ''

    # Set Windows console in VT mode
    if not NO_COLORS and sys.platform == 'win32':
        _kernel32.SetConsoleMode(_kernel32.GetStdHandle(-11), 7)

#endregion


if __name__ == '__main__':
    _main()
