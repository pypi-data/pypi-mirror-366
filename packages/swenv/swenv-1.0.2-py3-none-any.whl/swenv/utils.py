from __future__ import annotations

import atexit
import logging
import logging.config
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import zipfile
from argparse import ArgumentParser, RawTextHelpFormatter, _SubParsersAction
from contextlib import closing
from datetime import datetime
from functools import cached_property
from http.client import HTTPResponse
from importlib import import_module
from ipaddress import ip_address
from pkgutil import iter_modules
from signal import Signals
from tempfile import mktemp
from textwrap import dedent
from threading import Thread
from time import sleep, time
from traceback import format_exception
from types import ModuleType, TracebackType
from typing import (TYPE_CHECKING, Any, Callable, Literal, Mapping, Sequence,
                    overload)
from urllib.error import ContentTooShortError, HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

if TYPE_CHECKING:
    from swenv.env import Env

_logger = logging.getLogger(__name__)


def download(url: str, target: str|os.PathLike, *, env: Env|None = None):
    if env:
        open_func = env.urlopener.open
    else:
        open_func = urlopen

    with closing(open_func(url)) as fp:
        headers = fp.info()

        with open(target, 'wb') as tfp:
            result = str(target), headers
            bs = 1024*8
            size = -1
            read = 0
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            while block := fp.read(bs):
                read += len(block)
                tfp.write(block)

    if size >= 0 and read < size:
        raise ContentTooShortError("retrieval incomplete: got only %i out of %i bytes" % (read, size), result)

    return result


def ensure_file(target: str|os.PathLike, content: str|None, *, dry_run = False, sudo = False, encoding = 'utf-8', backup: str|os.PathLike|None = None):
    if content is not None:
        if os.path.exists(target):
            with open(target, 'r', encoding=encoding) as fp:
                current_content = fp.read()
        else:
            parent = os.path.dirname(target)
            if parent:
                os.makedirs(parent, exist_ok=True)
            current_content = None

        if content != current_content:
            if dry_run:
                if backup and not os.path.exists(backup) and current_content is not None:
                    _logger.info(f"{Color.YELLOW}Would{Color.RESET} update {Color.CYAN}%s{Color.RESET} (backup existing as {Color.GRAY}%s{Color.RESET})", target, backup)
                else:
                    _logger.info(f"{Color.YELLOW}Would{Color.RESET} %s {Color.CYAN}%s{Color.RESET}", 'update' if current_content is not None else 'create', target)
            else:
                if backup and not os.path.exists(backup) and current_content is not None:
                    _logger.info(f"Update {Color.CYAN}%s{Color.RESET} (backup existing as {Color.GRAY}%s{Color.RESET})", target, backup)
                    if sudo:
                        run_process(['mv', target, backup], sudo=True)
                    else:
                        os.rename(target, backup)
                else:
                    _logger.info(f"%s {Color.CYAN}%s{Color.RESET}", 'Update' if current_content is not None else 'Create', target)
                if sudo:
                    write_text(target, content, encoding=encoding, sudo=True)
                else:
                    with open(target, 'w', encoding=encoding) as fp:
                        fp.write(content)
            return True
        else:
            return False # no change

    else: # conent is None: delete or backup file
        if os.path.exists(target):
            if backup and not os.path.exists(backup):
                if dry_run:
                    _logger.info(f"{Color.YELLOW}Would{Color.RESET} delete {Color.GRAY}%s{Color.RESET} (backup as {Color.GRAY}%s{Color.RESET})", target, backup)
                else:
                    _logger.info(f"Delete {Color.GRAY}%s{Color.RESET} (backup as {Color.GRAY}%s{Color.RESET})", target, backup)
                    if sudo:
                        run_process(['mv', target, backup], sudo=True)
                    else:
                        os.rename(target, backup)
            else:
                if dry_run:
                    _logger.info(f"{Color.YELLOW}Would{Color.RESET} delete {Color.GRAY}%s{Color.RESET}", target)
                else:
                    _logger.info(f"Delete {Color.GRAY}%s{Color.RESET}", target)
                    if sudo:
                        run_process(['rm', target], sudo=True)
                    else:
                        os.unlink(target)

            return True
        else:
            return False # no change


#region From: zut

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
            if isinstance(_, str) and _[0] != '_' and _ not in ['DISABLED']:
                locals()[_] = ''

    # Set Windows console in VT mode
    if not NO_COLORS and sys.platform == 'win32':
        import ctypes
        _kernel32 = ctypes.windll.kernel32
        _kernel32.SetConsoleMode(_kernel32.GetStdHandle(-11), 7)
        del _kernel32


class SimpleError(ValueError):
    """
    An error that should result to only an error message being printed on the console, without a stack trace.
    """
    def __init__(self, msg: str, *args, **kwargs):
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        super().__init__(msg)


_sudo_available: bool|None = None

def is_sudo_available() -> bool:
    global _sudo_available
    if _sudo_available is None:
        if not shutil.which('sudo'):
            _sudo_available = False
        else:
            try:
                return_code = subprocess.call(['sudo', 'sh', '-c', 'id -u > /dev/null'])
                _sudo_available = return_code == 0
            except BaseException: # e.g. SIGINT / CTRL+C
                _sudo_available = False
    return _sudo_available


class SudoNotAvailable(subprocess.SubprocessError):
    def __init__(self):
        super().__init__("Sudo is not available")

#endregion


#region From: zut.commands

def add_commands(subparsers: _SubParsersAction[ArgumentParser], package: ModuleType|str):
    """
    Add all sub modules of the given package as commands.
    """
    if isinstance(package, str):
        package = import_module(package)
    elif not isinstance(package, ModuleType):
        raise TypeError(f"Invalid argument 'package': not a module")

    package_path = getattr(package, '__path__', None)
    if not package_path:
        raise TypeError(f"Invalid argument 'package': not a package")

    for module_info in iter_modules(package_path):
        if module_info.name.startswith('_'):
            continue # skip

        add_command(subparsers, f'{package.__name__}.{module_info.name}')

    
def add_command(subparsers: _SubParsersAction[ArgumentParser], handle: Callable|ModuleType|str, *, name: str|None = None, doc: str|None = None, help: str|None = None, add_arguments: Callable[[ArgumentParser]]|None = None, parents: ArgumentParser|Sequence[ArgumentParser]|None = None, **defaults):
    """
    Add the given function or module as a command.
    """
    if isinstance(handle, str):
        handle = import_module(handle)

    if isinstance(handle, ModuleType):
        module = handle        
        command_class = getattr(module, 'Command', None)
        if command_class:
            handle = command_class # will be treated later
        else:    
            handle = getattr(module, 'handle', None) # type: ignore
            if not handle:
                handle = getattr(module, '_handle', None) # type: ignore
                if not handle:
                    handle_name = name if name else module.__name__.split('.')[-1]
                    handle = getattr(module, handle_name, None) # type: ignore
                    if not handle:
                        raise ValueError(f"Cannot use module {module.__name__} as a command: no attribute named \"Command\", \"handle\" , \"_handle\" or \"{handle_name}\"")
    elif callable(handle):
        module = None
    else:
        raise TypeError(f"Invalid argument 'handle': not a module or a callable")
    
    if isinstance(handle, type): # Command class (e.g. Django management command)
        command_class = handle.__name__.lower()
        command_instance = handle()
        handle = getattr(command_instance, 'handle')
        if not name:
            if command_class.endswith('subcommand') and command_class != 'subcommand':
                name = command_class.removesuffix('subcommand')
            elif command_class.endswith('command') and command_class != 'command':
                name = command_class.removesuffix('command')  
        if not add_arguments:
            add_arguments = getattr(command_instance, 'add_arguments', None)
        if not help:
            help = getattr(command_instance, 'help', None)
        if not doc:
            doc = command_instance.__doc__

    if not name:
        name = getattr(handle, 'name', None)
        if not name:
            if module:
                name = module.__name__.split('.')[-1]
            else:
                name = handle.__name__ # type: ignore

    if not doc:
        doc = getattr(handle, 'doc', None)
        if doc:
            if callable(doc):
                doc = doc()
        else:
            doc = handle.__doc__
            if not doc:
                if module:
                    doc = module.__doc__
                if not doc:
                    doc = help

    if not help:
        help = getattr(handle, 'help', doc)
    
    if not add_arguments:
        add_arguments = getattr(handle, 'add_arguments', None)
        if not add_arguments and module:
            add_arguments = getattr(module, 'add_arguments', None)

    if parents is None:
        parents = []
    elif isinstance(parents, ArgumentParser):
        parents = [parents]

    cmdparser = subparsers.add_parser(name, help=get_help_text(help), description=get_description_text(doc), formatter_class=RawTextHelpFormatter, parents=parents)

    if add_arguments:
        add_arguments(cmdparser)

    cmdparser.set_defaults(handle=handle, **defaults)

    return cmdparser


def get_help_text(doc: str|None):
    if doc is None:
        return None
    
    doc = doc.strip()
    try:
        return doc[0:doc.index('\n')].strip()
    except:
        return doc
    

def get_description_text(doc: str|None):
    if doc is None:
        return None
    
    return dedent(doc)


def get_exit_code(code: Any) -> int:
    if not isinstance(code, int):
        code = 0 if code is None or code is True else 1
    return code


def create_command_parser(prog: str|None = None, *, version: str|None = None, doc: str|None = None, keep_default_help = False) -> ArgumentParser:
    parser = (ArgumentParser if keep_default_help else ExtendedArgumentParser)(prog=prog, description=get_description_text(doc) if doc else None, formatter_class=RawTextHelpFormatter)
 
    if version is not None:
        parser.add_argument('--version', action='version', version=f"{parser.prog} {version}", help=None if keep_default_help else "Show program's version number and exit.")
    
    return parser


class ExtendedArgumentParser(ArgumentParser):
    def __init__(self, *arg, help_help = "Show this help message and exit.", **kwargs):
        super().__init__(*arg, **kwargs)
        self.help_help = help_help

        for action in self._actions:
            if action.dest == 'help':
                action.help = self.help_help
                break


def run_command(parser: ArgumentParser, *, default: str|None = None):
    """
    Run a command.
    """
    args = {}
    argv = sys.argv[1:]
    
    remaining_argv = []
    known_args, remaining_argv = parser.parse_known_args(argv)
    known_args = vars(known_args)
    args = {**args, **known_args}
    handle_func: Callable|None = args.pop('handle', None)

    logger = logging.getLogger(__name__)
    
    if not handle_func:
        if default and parser:
            known_args = vars(parser.parse_args([default, *argv]))
            args = {**args, **known_args}
            handle_func = args.pop('handle', None)
            if not handle_func:
                logger.error("Default command handle not found")
                return 1                
        else:
            logger.error("Missing command")
            return 1
    elif remaining_argv:
        logger.error(f"Unrecognized arguments: {', '.join(remaining_argv)}")
        return 1

    try:
        r = handle_func(**args)
        return get_exit_code(r)
    except SimpleError as err:
        logger.error(str(err))
        return 1
    except KeyboardInterrupt:
        logger.error("Interrupted")
        return 1
    except BaseException as err:
        message = str(err)
        logger.exception(f"{type(err).__name__}{f': {message}' if message else ''}")
        return 1


def exec_command(handle: ArgumentParser, *, default: str|None = None):
    r = run_command(handle, default=default)
    sys.exit(r)

#endregion


#region From: zut.config

def configure_logging(level: str|int|None = None, *, file_level: str|int|None = None, verbose_level: str|int|None = None, verbose_loggers: Sequence[str]|None = None, print_logger_names = True, count = True, exit_handler = True):
    config = get_logging_config(level=level, file_level=file_level, verbose_level=verbose_level, verbose_loggers=verbose_loggers, print_logger_names=print_logger_names, count=count, exit_handler=exit_handler)
    logging.config.dictConfig(config)


def get_logging_config(level: str|int|None = None, *, file_level: str|int|None = None, verbose_level: str|int|None = None, verbose_loggers: Sequence[str]|None = None, print_logger_names = True, count = True, exit_handler = True):
    if not isinstance(level, str):
        if isinstance(level, int):
            level = logging.getLevelName(level)
        else:
            level = os.environ.get('LOG_LEVEL', '').upper() or 'INFO'
    
    # Ensure specific verbose subsystems do not send DEBUG messages, even if LOG_LEVEL is DEBUG, except if we explicitely request it
    if not isinstance(verbose_level, str):
        if isinstance(verbose_level, int):
            verbose_level = logging.getLevelName(verbose_level)
        else:
            verbose_level = os.environ.get('LOG_VERBOSE_LEVEL', '').upper()
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(levelname)-8s [%(name)s] %(message)s' if print_logger_names else '%(levelname)s: %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'default',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': level,
        },
        'loggers': {
            'django': { 'level': verbose_level or 'INFO', 'propagate': False },
            'daphne': { 'level': verbose_level or 'INFO', 'propagate': False },
            'asyncio': { 'level': verbose_level or 'INFO', 'propagate': False },
            'urllib3': { 'level': verbose_level or 'INFO', 'propagate': False },
            'botocore': { 'level': verbose_level or 'INFO', 'propagate': False },
            'boto3': { 'level': verbose_level or 'INFO', 'propagate': False },
            's3transfer': { 'level': verbose_level or 'INFO', 'propagate': False },
            'PIL': { 'level': verbose_level or 'INFO', 'propagate': False },
            'celery.utils.functional': { 'level': verbose_level or 'INFO', 'propagate': False },
            'smbprotocol': { 'level': verbose_level or 'WARNING', 'propagate': False },
        },
    }

    if verbose_loggers:
        for name in verbose_loggers:
            config['loggers'][name] = { 'level': verbose_level or 'INFO', 'propagate': False }

    if not Color.NO_COLORS:
        config['formatters']['colored'] = {
            '()': ColoredFormatter.__module__ + '.' + ColoredFormatter.__qualname__,
            'format': '%(log_color)s%(levelname)-8s%(reset)s %(light_black)s[%(name)s]%(reset)s %(message)s' if print_logger_names else '%(log_color)s%(levelname)s%(reset)s: %(message)s',
        }

        config['handlers']['console']['formatter'] = 'colored'

    file = os.environ.get('LOG_FILE')
    if file:
        if not isinstance(file_level, str):
            if isinstance(file_level, int):
                file_level = logging.getLevelName(file_level)
            else:
                file_level = os.environ.get('LOG_FILE_LEVEL', '').upper() or level

        log_dir = os.path.dirname(file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        config['formatters']['file'] = {
            'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s',
        }
        config['handlers']['file'] = {
            'class': 'logging.FileHandler',
            'level': file_level,
            'formatter': 'file',
            'filename': file,
            'encoding': 'utf-8',
        }

        config['root']['handlers'].append('file')
    
        file_intlevel = logging.getLevelName(file_level)
        intlevel = logging.getLevelName(level)
        if file_intlevel < intlevel:
            config['root']['level'] = file_level
    
    if count or exit_handler:
        config['handlers']['counter'] = {
            'class': LogCounter.__module__ + '.' + LogCounter.__qualname__,
            'level': 'WARNING',
            'exit_handler': exit_handler,
        }

        config['root']['handlers'].append('counter')

    return config


def get_app_data_dir(base_name: str, base_dir: Path|None = None) -> Path:
    if _value := os.environ.get(f'{base_name.upper()}_DATA_DIR'):
        return Path(_value)
    elif _value := os.environ.get('DATA_DIR'):
        return Path(_value).joinpath(base_name.lower())
    elif base_dir and (_value := base_dir.joinpath('data')).exists():
        return _value
    else:
        return Path(os.environ.get('APPDATA', '~\\AppData\\Roaming' if sys.platform == 'win32' else '~/.local/share')).expanduser().joinpath(base_name.lower())


class ColoredRecord:
    LOG_COLORS = {
        logging.DEBUG:     Color.GRAY,
        logging.INFO:      Color.CYAN,
        logging.WARNING:   Color.YELLOW,
        logging.ERROR:     Color.RED,
        logging.CRITICAL:  Color.BG_RED,
    }

    def __init__(self, record: logging.LogRecord):
        # The internal dict is used by Python logging library when formatting the message.
        # (inspired from library "colorlog").
        self.__dict__.update(record.__dict__)
        
        self.log_color = self.LOG_COLORS.get(record.levelno, '')

        for attname, value in Color.__dict__.items():
            if attname == 'NO_COLORS' or attname.startswith('_'):
                continue
            setattr(self, attname.lower(), value)


class ColoredFormatter(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format a message from a record object."""
        wrapper = ColoredRecord(record)
        message = super().formatMessage(wrapper) # type: ignore
        return message


class LogCounter(logging.Handler):
    """
    A logging handler that counts warnings and errors.
    
    If warnings and errors occured during the program execution, display counts at exit
    and set exit code (if it was not explicitely set with `sys.exit` function).
    """
    counts: dict[int, int]

    error_exit_code = 199
    warning_exit_code = 198

    
    _detected_exception: tuple[type[BaseException], BaseException, TracebackType|None]|None = None
    _detected_exit_code = 0
    _original_exit: Callable[[int],None] = sys.exit
    _original_excepthook = sys.excepthook

    _registered = False
    _logger: logging.Logger

    def __init__(self, *, level = logging.WARNING, exit_handler = False):
        if not hasattr(self.__class__, 'counts'):
            self.__class__.counts = {}
        
        if exit_handler and not self.__class__._registered:
            sys.exit = self.__class__._exit
            sys.excepthook = self.__class__._excepthook
            atexit.register(self.__class__._exit_handler)
            self.__class__._logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__qualname__}')
            self.__class__._registered = True
        
        super().__init__(level=level)

    def emit(self, record: logging.LogRecord):        
        if not record.levelno in self.__class__.counts:
            self.__class__.counts[record.levelno] = 1
        else:
            self.__class__.counts[record.levelno] += 1
    
    @classmethod
    def _exit(cls, code: int = 0):
        cls._detected_exit_code = code
        cls._original_exit(code)
    
    @classmethod
    def _excepthook(cls, exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType|None):
        cls._detected_exception = exc_type, exc_value, exc_traceback
        cls._original_exit(1)

    @classmethod
    def _exit_handler(cls):
        if cls._detected_exception:
            exc_type, exc_value, exc_traceback = cls._detected_exception

            msg = 'An unhandled exception occured\n'
            msg += ''.join(format_exception(exc_type, exc_value, exc_traceback)).strip()
            cls._logger.critical(msg)

        else:
            error_count = 0
            warning_count = 0
            for level, count in cls.counts.items():
                if level >= logging.ERROR:
                    error_count += count
                elif level >= logging.WARNING:
                    warning_count += count
            
            msg = ''
            if error_count > 0:
                msg += (', ' if msg else 'Logged ') + f"{error_count:,} error{'s' if error_count > 1 else ''}"
            if warning_count > 0:
                msg += (', ' if msg else 'Logged ') + f"{warning_count:,} warning{'s' if warning_count > 1 else ''}"
            
            if msg:
                cls._logger.log(logging.ERROR if error_count > 0 else logging.WARNING, msg)                             
                # Change exit code if it was not originally set explicitely to another value using `sys.exit()`
                if cls._detected_exit_code == 0:
                    os._exit(cls.error_exit_code if error_count > 0 else cls.warning_exit_code)

#endregion


#region From: zut.process

@overload
def run_process(cmd: str|os.PathLike|Sequence[str|os.PathLike], *, encoding: Literal['bytes'], capture_output: bool|Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, sudo = False, shell = False, env: Mapping[str,Any]|None = None, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, input: str|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess[bytes]:
    ...

@overload
def run_process(cmd: str|os.PathLike|Sequence[str|os.PathLike], *, encoding: Literal['utf-8', 'cp1252', 'unknown']|None = None, capture_output: bool|Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, sudo = False, shell = False, env: Mapping[str,Any]|None = None, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, input: str|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess[str]:
    ...

def run_process(cmd: str|os.PathLike|Sequence[str|os.PathLike], *, encoding: str|Literal['unknown','bytes']|None = None, capture_output: bool|Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, sudo = False, shell = False, env: Mapping[str,Any]|None = None, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, input: str|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess:
    if sudo:
        if not is_sudo_available():
            raise SudoNotAvailable()
        if isinstance(cmd, str):
            cmd = f'sudo {cmd}'
        elif isinstance(cmd, (os.PathLike,bytes)):
            cmd = ['sudo', cmd]
        else:
            cmd = ['sudo', *cmd] # type: ignore

    if capture_output is None:
        capture_output = (stdout and stdout != 'disable') or (stderr and stderr != 'disable')

    cp = subprocess.run(cmd,
                        capture_output=True if capture_output else False,
                        text=encoding not in {'unknown', 'bytes'},
                        encoding=encoding if encoding not in {'unknown', 'bytes'} else None,
                        shell=shell,
                        env=env,
                        stdout=subprocess.DEVNULL if stdout == 'disable' else None,
                        stderr=subprocess.DEVNULL if stderr == 'disable' else None,
                        input=input)
    
    if encoding == 'unknown':
        def parse_unknown_encoding(output: bytes):
            if output is None:
                return None
            try:
                return output.decode('utf-8')
            except UnicodeDecodeError:
                return output.decode('cp1252')
        
        cp.stdout = parse_unknown_encoding(cp.stdout)
        cp.stderr = parse_unknown_encoding(cp.stderr)
    
    return verify_run_process(cp, strip=capture_output if capture_output is True or isinstance(capture_output, str) else None, check=check, stdout=stdout, stderr=stderr, logger=logger)


def verify_run_process(cp: subprocess.CompletedProcess, *, strip: Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess:
    if strip:
        cp.stdout = _strip_data(cp.stdout, strip)
        cp.stderr = _strip_data(cp.stderr, strip)
    
    invalid_returncode = False
    if check:
        if check is True:
            check = 0
        invalid_returncode = not (cp.returncode in check if not isinstance(check, int) else cp.returncode == check)

    invalid_stdout = stdout == 'raise' and cp.stdout
    invalid_stderr = stderr == 'raise' and cp.stderr

    if cp.stdout:
        level = None
        if stdout == 'warning':
            level = logging.WARNING
        elif stdout == 'error':
            level = logging.ERROR
        if level:
            (logger or logging.getLogger(__name__)).log(level, f"{Color.PURPLE}[stdout]{Color.RESET} %s", stdout)
            
    if cp.stderr:
        level = None
        if stderr == 'warning':
            level = logging.WARNING
        elif stderr == 'error':
            level = logging.ERROR
        if level:
            (logger or logging.getLogger(__name__)).log(level, f"{Color.PURPLE}[stderr]{Color.RESET} %s", stderr)

    if invalid_returncode or invalid_stdout or invalid_stderr:
        raise RunProcessError(cp.returncode, cp.args, cp.stdout, cp.stderr)    
    return cp

def _strip_data(data, strip: Literal['rstrip-newline','strip',True]|None):
    if not strip:
        return data
    
    if isinstance(data, str):
        if strip == 'rstrip-newline':
            return data.rstrip('\r\n')
        elif strip == 'rstrip':
            return data.rstrip()
        else:
            return data.strip()
    else:
        raise TypeError(f"Cannot strip data of type {type(data).__name__}")         

class RunProcessError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, stdout, stderr):
        super().__init__(returncode, cmd, stdout, stderr)
        self.maxlen: int|None = 200
        self._message = None

    def with_maxlen(self, maxlen: int|None):
        self.maxlen = maxlen
        return self

    @property
    def message(self):
        if self._message is None:
            self._message = ''

            if self.returncode and self.returncode < 0:
                try:
                    self._message += "died with %r" % Signals(-self.returncode)
                except ValueError:
                    self._message += "died with unknown signal %d" % -self.returncode
            else:
                self._message += "returned exit code %d" % self.returncode

            if self.output:
                info = self.output[0:self.maxlen] + '…' if self.maxlen is not None and len(self.output) > self.maxlen else self.stdout
                self._message += ('\n' if self._message else '') + f"[stdout] {info}"

            if self.stderr:
                info = self.stderr[0:self.maxlen] + '…' if self.maxlen is not None and len(self.stderr) > self.maxlen else self.stderr
                self._message += ('\n' if self._message else '') + f"[stderr] {info}"

            self._message = f"Command '{self.cmd}' {self._message}"

        return self._message

    def __str__(self):
        return self.message

#endregion


#region From: zut.net


def resolve_host(host: str, *, timeout: float|None = None, ip_version: int|None = None) -> list[str]:
    """
    Make a DNS resolution with a timeout.
    """
    try:
        # If host is already an ip address, return it
        ip = ip_address(host)
        if not ip_version or ip.version == ip_version:
            return [ip.compressed]
    except ValueError:
        pass
    
    if ip_version is None:
        family = 0
    elif ip_version == 4:
        family = socket.AddressFamily.AF_INET
    elif ip_version == 6:
        family = socket.AddressFamily.AF_INET6
    else:
        raise ValueError(f"Invalid ip version: {ip_version}")

    addresses = []
    exception = None

    def target():
        nonlocal addresses, exception
        try:
            for af, socktype, proto, canonname, sa in socket.getaddrinfo(host, port=0, family=family):
                addresses.append(sa[0])
        except BaseException as err:
            exception = err

    if timeout is not None:
        thread = Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        if thread.is_alive():
            raise TimeoutError(f"Name resolution for host \"{host}\" timed out")

    else:
        target()

    if exception:
        err = NameError(str(exception))
        err.name = host
        raise err
        
    return addresses

def check_port(hostport: str|tuple[str,int]|list[str|tuple[str,int]], port: int|None = None, *, timeout: float|None = None) -> tuple[str,int]|None:
    """
    Check whether at least one of the given host and port is open.

    If yes, return the first open (host, port). Otherwise return None.
    """
    if port is not None:
        if not isinstance(port, int):
            raise TypeError(f"port: {type(port).__name__}")
        
    def normalize_hostport(value) -> tuple[str, int]:
        if isinstance(value, str):
            if m := re.match(r'^(.+):(\d+)$', value):
                return (m[1], int(m[2]))
            elif port is not None:
                return (value, port)
            else:
                raise TypeError(f"Port required for host {host}")
        elif isinstance(value, tuple):
            return value
        else:
            raise TypeError(f"hostport: {type(value).__name__}")

    if isinstance(hostport, (str,tuple)):
        hostports = [normalize_hostport(hostport)]
    elif isinstance(hostport, list):
        hostports = [normalize_hostport(value) for value in hostport]
    else:
        raise TypeError(f"hostport: {type(hostport).__name__}")

    open_list: list[tuple[str,int]] = []

    def target(host: str, port: int):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            if result == 0:
                _logger.debug("Host %s, port %s: open", host, port)
                open_list.append((host, port))
            else:
                _logger.debug("Host %s, port %s: not open", host, port)
        except Exception as err:
            _logger.debug("Host %s, port %s: %s", host, port, err)
        finally:
            if sock:
                sock.close()

    threads: list[Thread] = []
    for host, port in hostports:
        thread = Thread(target=target, args=[host, port], daemon=True)
        thread.start()
        threads.append(thread)

    # Wait for all threads
    if timeout is not None:
        stop_time = time() + timeout
        while time() < stop_time:
            if any(t.is_alive() for t in threads):
                sleep(0.1)
            else:
                break
    else:
        for thread in threads:
            thread.join()

    # Return
    if open_list:
        return open_list[0]
    else:
        return None

def get_wpad_proxy_url(*, timeout: float = 1.0) -> str|None:
    wpad = get_wpad_config(timeout=timeout)
    return wpad.proxy_url if wpad else None


_default_wpad: WPADConfig|None = None
_default_wpad_requested = False

def get_wpad_config(host: str = 'wpad', *, timeout: float = 1.0) -> WPADConfig|None:
    global _default_wpad, _default_wpad_requested
    if host == 'wpad' and _default_wpad_requested:
        return _default_wpad

    # Determine actual URL and host
    if '://' in host:
        url = host
        parts = urlparse(url)
        if not parts.hostname:
            raise ValueError(f"Invalid URL: {url}")
        host = parts.hostname
    else:
        url = f"http://{host}/wpad.dat"

    # Try to connect to WPAD (allow to avoid unavalability of timeout when resolving hostname)
    if not check_port(host, 80, timeout=timeout):
        if host == 'wpad':
            _default_wpad_requested = True
        return None

    # Request WPAD url    
    request = Request(url)
    response: HTTPResponse
    try:
        with urlopen(request, timeout=timeout) as response:
            _logger.debug("WPAD response: %s %s - Content-Type: %s", response.status, response.reason, response.headers.get('Content-Type'))
            body = response.read().decode('utf-8')
    except HTTPError as err:
        _logger.error(f"Cannot retrieve WPAD: HTTP {err.status} {err.reason}")
        if host == 'wpad':
            _default_wpad_requested = True
        return None
    except URLError as err:
        _logger.log(logging.DEBUG if err.errno == 5 else logging.ERROR,f"Cannot retrieve WPAD: {err.reason}")
        if host == 'wpad':
            _default_wpad_requested = True
        return None
    
    no_proxy = []

    def append_domain(domain: str):
        no_proxy.append(domain)

    def append_urlpattern(pattern: str):
        if m := re.match(r'^https?://([^/]+)/\*$', pattern):
            append_domain(m[1])
        else:
            _logger.warning(f"Ignore unknown URL pattern \"{pattern}\" in WPAD response")
    
    def append_net(network: str, mask: str):
        if network == '127.0.0.1':
            no_proxy.append('127.*')
            return
        
        if network == '172.16.0.0' and mask == '255.240.0.0':
            for i in range(16, 32):
                no_proxy.append(f'172.{i}.*')
            return
        
        if mask == '255.255.255.255':
            no_proxy.append(network)
            return
        
        asterisk_start = None
        if mask == '255.0.0.0':
            asterisk_start = 1
        elif mask == '255.255.0.0':
            asterisk_start = 2
        elif mask == '255.255.255.0':
            asterisk_start = 3

        if asterisk_start is not None:
            parts = network.split('.')
            if len(parts) == 4:
                no_proxy.append('.'.join(parts[0:asterisk_start]) + '.*')
                return

        _logger.warning(f"Ignore network with specific mask \"{network}/{mask}\" in WPAD response")
    
    proxy_host = None
    proxy_port = None
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith('//') or line in {'{', '}', 'function FindProxyForURL(url, host)'}:
            continue
        elif m := re.match(r'^return "PROXY\s*([^\s"\:]+)\:(\d+)";$', line, re.IGNORECASE):
            proxy_host = m[1]
            proxy_port = int(m[2])
        elif m := re.match(r'^if \(isInNet\(host, "(?P<network>[^"]+)", "(?P<mask>[^"]+)"\)\) \{return "DIRECT";\}$', line, re.IGNORECASE):
            append_net(m['network'], m['mask'])
        elif m := re.match(r'^if \((?P<function>[a-z]+)\((?:host|url), "(?P<value>[^"]+)"\)\) \{return "DIRECT";\}$', line, re.IGNORECASE):
            if m['function'] == 'dnsDomainIs':
                append_domain(m['value'])
            elif m['function'] == 'shExpMatch':
                append_urlpattern(m['value'])
            else:
                _logger.warning(f"Ignore line with unknown function \"{m['function']}\" in WPAD response: {line}")
        else:
            _logger.warning(f"Ignore unexpected line in WPAD response: {line}")

    wpad = WPADConfig(proxy_host, proxy_port, ','.join(no_proxy))
    if host == 'wpad':
        _default_wpad = wpad
        _default_wpad_requested = True
    return wpad


class WPADConfig:
    def __init__(self, proxy_host: str|None = None, proxy_port: int|None = None, noproxy: str|None = None):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.no_proxy = noproxy

    @cached_property
    def proxy_url(self) -> str|None:
        if not self.proxy_host:
            return None
        return f"http://{self.proxy_host}:{self.proxy_port}"

    @cached_property
    def proxy_domain(self) -> str|None:
        if not self.proxy_host:
            return None

        if m := re.match(r'^[^\.]+\.(.+)$', self.proxy_host):
            return m[1]
        else:
            return None

#endregion


#region From: zut.files (adapted for simplicity)

def write_text(path: str|os.PathLike, data: str, *, encoding: str|None = None, errors: str|None = None, newline: str|None = None, sudo: bool = False) -> None:
    """
    Open the file in text mode, write to it, and close the file.
    """
    if sudo and not os.access(path, os.W_OK):
        temp_path = None
        try:
            temp_path = mktemp()
            with open(temp_path, 'w', encoding=encoding, errors=errors, newline=newline) as temp_fp:
                temp_fp.write(data)

            run_process(['cp', temp_path, path], check=True, sudo=True)
        finally:
            if temp_path:
                os.remove(temp_path)
    else:
        with open(path, 'w', encoding=encoding, errors=errors, newline=newline) as fp:
            fp.write(data)


def unzip(path: str|os.PathLike|zipfile.Path, target: str|os.PathLike, *, existing: Literal['ignore','update','replace','warn'] = 'warn', omit_single_dir: bool|str|re.Pattern = False, password: str|bytes|None = None, mkdir = False, insecure = False):
    """
    Unzip an archive file in a target directory.

    :param existing: If 'ignore', entries that already exist in the target are ignored. If 'update', they are replaced only if the archive entry are newer. If 'replace', they are always replaced. If 'warn' (the default), a warning is issued and the file is ignored.
    :param omit_single_dir: If there is a single dir and it matches the given pattern (if any), the directory is omitted when extracting to the target.
    """
    if mkdir:
        os.makedirs(target, exist_ok=True)
    
    password = get_zip_password_bytes(password)

    def recurse(path: zipfile.Path, target: str|os.PathLike, *, mkdir = False):
        dir_mtime = None
        if mkdir:
            if not os.path.exists(target):
                dir_mtime = get_zip_mtime_timestamp(path.root, path.at)
                os.mkdir(target)
        
        for entry in path.iterdir():
            if '..' in entry.name or '/' in entry.name or '\\' in entry.name:
                if not insecure:
                    raise ValueError(f'Insecure zip entry name "{entry.name}" (at {path})')                
            entry_target = os.path.join(target, entry.name)

            if entry.is_dir():
                recurse(entry, entry_target, mkdir=True)
            else:
                entry_mtime: float|None = None

                extract = True
                if existing != 'replace':
                    if os.path.exists(entry_target):
                        if existing == 'update':
                            entry_mtime = get_zip_mtime_timestamp(entry.root, entry.at)
                            target_mtime = os.stat(entry_target).st_mtime
                            if target_mtime >= entry_mtime:
                                extract = False
                                _logger.debug("Ignore extraction from %s to newer existing file: %s", entry.root.filename, entry_target)
                        else:
                            extract = False
                            _logger.log(logging.DEBUG if existing == 'ignore' else logging.WARNING, "Ignore extraction from %s to existing file: %s", entry.root.filename, entry_target)
                
                if extract:
                    _logger.debug("Extract from %s to %s", entry.root.filename, entry_target)
                    with entry.root.open(entry.at, pwd=password) as src_fp, open(entry_target, "wb") as dst_fp:
                        shutil.copyfileobj(src_fp, dst_fp)

                    if entry_mtime is None:
                        entry_mtime = get_zip_mtime_timestamp(entry.root, entry.at)
                    os.utime(entry_target, (entry_mtime, entry_mtime))
        
        if dir_mtime:
            os.utime(target, (dir_mtime, dir_mtime))

    root_to_close = None
    try:
        if not isinstance(path, zipfile.Path):
            path = zipfile.Path(path)
            root_to_close = path.root

        dir_to_omit = None
        if omit_single_dir:
            dirs = [entry for entry in path.iterdir() if entry.is_dir()]
            if len(dirs) == 1:
                if isinstance(omit_single_dir, (str,re.Pattern)):
                    if re.match(omit_single_dir, dirs[0].name):
                        dir_to_omit = dirs[0]
                else:
                    dir_to_omit = dirs[0]

        if dir_to_omit:
            recurse(dir_to_omit, target)
        else:
            recurse(path, target)
    finally:
        if root_to_close:
            root_to_close.close()


def get_zip_mtime_timestamp(zipfile: zipfile.ZipFile, entry: str) -> float:
    y, m, d, hour, min, sec = zipfile.getinfo(entry).date_time
    # Inside zip files, dates and times are stored in local time in 16 bits, not UTC (Coordinated Universal Time/Temps Universel Coordonné) as is conventional, using an ancient MS DOS format.
    # Bit 0 is the least signifiant bit. The format is little-endian. There was not room in 16 bit to accurately represent time even to the second, so the seconds field contains the seconds divided by two, giving accuracy only to the even second.
    return datetime(y, m, d, hour, min, sec).timestamp()


def get_zip_password_bytes(password: str|bytes|None, *, encoding = 'utf-8') -> bytes|None:
    if not isinstance(password, str) and isinstance(password, Sequence):
        return password
    else:
        return password.encode(encoding) if password is not None else None


#endregion
