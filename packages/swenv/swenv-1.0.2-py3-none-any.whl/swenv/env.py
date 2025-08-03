from __future__ import annotations

import json
import logging
import ssl
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable
from urllib.request import HTTPSHandler, ProxyHandler, build_opener

from swenv.settings import DATA_DIR

if TYPE_CHECKING:
    from swenv.apt import AptRepositoryDescription

_logger = logging.getLogger(__name__)

class Env:
    def __init__(self, path_or_name: Path|str):
        self.name: str
        self.path: Path|None = None

        self.domain: str|None = None
        self.dns_servers: list[str]|None = None

        self.proxy_host: str|None = None
        self.proxy_port: int|None = None
        self.proxy_cafile: Path|None = None
        self.no_proxy: str|None = None

        self.apt_repository: AptRepositoryDescription|None = None
        self.git_repositories: list[str]|None = None
        self.pip_repository: str|None = None
        self.npm_repository: str|None = None

        self.shell_env: bool|None = None
        """ Indicate whether shell environment variables (HTTP_PROXY, etc) are managed. """
        
        if isinstance(path_or_name, Path):
            self.path = path_or_name
            self.name = self.path.stem            
            self._load(self.path)

            if not self.domain:
                self.domain = self.name

        else:
            self.name = path_or_name

        self._urlopener = None

    def _load(self, path: Path):
        with open(path, 'r', encoding='utf-8') as fp:
            data: dict = json.load(fp)

        for key, expected_type in {
            'domain': str,
            'proxy_host': str,
            'proxy_port': int,
            'proxy_cafile': str,
            'no_proxy': str,
            'pip_repository': str,
            'npm_repository': str,
            'shell_env': bool,
        }.items():
            value = data.pop(key, None)
            if value is not None:
                if not isinstance(value, expected_type):
                    raise TypeError(f'{path.name}: invalid {key} type: {type(value).__name__}, expected {expected_type.__name__}')
                if key == 'proxy_cafile':
                    value = DATA_DIR.joinpath(value)
            setattr(self, key, value)
        
        for key, alt_keys in {'dns_servers': ['dns_server'], 'git_repositories': ['git_repository']}.items(): # lists or strings
            value = _get_value(data, key, alt_keys, prefix=f'{path.name}: ')
            if value is not None:
                if not isinstance(value, list):
                    value = [value]
                for i, elem in enumerate(value):
                    if not isinstance(elem, str):
                        raise TypeError(f'{path.name}: invalid {key}[{i}] type: {type(elem).__name__}, expected str')
            setattr(self, key, value)
        
        for key, alt_keys in {'apt_repository': ['apt_repositories']}.items(): # other synonymous
            value = _get_value(data, key, alt_keys, prefix=f'{path.name}: ')
            setattr(self, key, value)

        if (value := getattr(self, 'apt_repository')) is not None:
            from swenv.apt import AptRepositoryDescription
            self.apt_repository = AptRepositoryDescription(value, origin=path)
        
        if self.proxy_host:
            if not self.proxy_port:
                raise ValueError(f"{path.name}: has proxy_host without proxy_port")
            if not self.no_proxy:
                raise ValueError(f"{path.name}: has proxy_host without no_proxy")

        if data:
            _logger.warning("Unexpected configuration settings in %s: %s", path, ', '.join(f'"{key}"' for key in data))


    def __str__(self):
        return self.name
    
    @cached_property
    def proxy_url(self):
        if self.proxy_host:
            return f"http://{self.proxy_host}:{self.proxy_port}"
        else:
            return None
    
    @property
    def urlopener(self):
        if self._urlopener is None:
            handlers = []

            if self.proxy_url:
                handlers.append(ProxyHandler({'http': self.proxy_url, 'https': self.proxy_url}))

                if self.proxy_cafile:
                    ssl_context = ssl.create_default_context()
                    ssl_context.verify_flags &= ~ssl.VERIFY_X509_STRICT
                    ssl_context.set_default_verify_paths()
                    ssl_context.load_verify_locations(cafile=self.proxy_cafile)
                    handlers.append(HTTPSHandler(context=ssl_context))

            self._urlopener = build_opener(*handlers)
        
        return self._urlopener
    

def _get_value(data: dict[str, Any], key: str, alt_keys: Iterable[str], *, prefix = ''):
    value = data.pop(key, None)
    actual_key = key
    for alt_key in alt_keys:
        alt_value = data.pop(alt_key, None)
        if alt_value is not None:
            if value is not None:
                raise ValueError(f'{prefix}unexpected "{alt_key}": "{actual_key}" already provided')
            value = alt_value
            actual_key = alt_key
    return value



def load_envs():
    envs: dict[str,Env] = {}

    for file in sorted(DATA_DIR.glob('*.json')):
        env = Env(file)
        envs[env.name] = env

    return envs


ENVS = load_envs()

DIRECT_ENV = ENVS['direct'] if 'direct' in ENVS else Env('direct')
