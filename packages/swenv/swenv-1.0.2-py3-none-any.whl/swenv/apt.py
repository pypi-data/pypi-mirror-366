from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, Any, Iterable
from urllib.parse import urlparse

from swenv.settings import DATA_DIR
from swenv.utils import Color, ensure_file, run_process, write_text

if TYPE_CHECKING:
    from swenv.env import Env

_logger = logging.getLogger(__name__)


def update_apt(env: Env, *, dry_run = False):
    apt_sources_dir = Path('/etc/apt/sources.list.d')
    if not apt_sources_dir.exists():
        _logger.debug('Directory %s not found', apt_sources_dir)
        return
    
    _logger.info("Configure apt")

    # Sources
    change = False
    for file in apt_sources_dir.glob('*.list'):
        current = file.read_text(encoding='utf-8')
        target = translate_apt_repository_specs(current, env)

        if strip_lines(target) != strip_lines(current):
            if dry_run:
                _logger.info(f"{Color.YELLOW}Would{Color.RESET} update {Color.CYAN}%s{Color.RESET}", file)
            else:
                _logger.info(f"Update {Color.CYAN}%s{Color.RESET}:\n{Color.GRAY}%s{Color.RESET}", file, target.strip())
                write_text(file, target, encoding='utf-8', sudo=True)
            change = True

    # Proxy
    target = Path('/etc/apt/apt.conf.d/proxy.conf')
    backup = Path('/etc/apt/apt.conf.d/proxy.conf~')
    if env.proxy_url:
        content = f'Acquire::http::Proxy "{env.proxy_url}";\n'
        if env.apt_repository:
            for host in env.apt_repository.private_hostnames:
                content += f'Acquire::http::Proxy::{host} "DIRECT";\n'
    else:
        content = None
    ensure_file(target, content, dry_run=dry_run, backup=backup, sudo=True)

    # Update
    if change:
        if dry_run:
            _logger.info(f"{Color.YELLOW}Would{Color.RESET} run {Color.CYAN}apt update{Color.RESET}")
        else:
            _logger.info(f"Run {Color.CYAN}apt update{Color.RESET}")
            if run_process(['apt', 'update'], sudo=True).returncode != 0:
                _logger.error("Could not run apt update")


def strip_lines(content: str|None):
    if content is None:
        return None
    return re.sub(r'\s*\n\s*', '\n', content)


def configure_apt(*, dry_run = False):
    if not which('apt'):
        _logger.debug("Skip installing APT conf files: apt is not available")
        return
    
    configure_apt_dir(DATA_DIR.joinpath('apt', 'sources.list.d'), {'.list'}, dry_run=dry_run)
    configure_apt_dir(DATA_DIR.joinpath('apt', 'trusted.gpg.d'), {'.asc', '.gpg'}, dry_run=dry_run)
    configure_apt_dir(DATA_DIR.joinpath('apt', 'preferences.d'), {'.pref'}, dry_run=dry_run)


def configure_apt_dir(src_dir: Path, extensions: set[str], *, dry_run = False):
    if not src_dir.exists():
        return
    
    for src in sorted(src_dir.iterdir()):
        if src.is_dir() or not src.suffix in extensions:
            continue
        configure_apt_file(src, dry_run=dry_run)


def configure_apt_file(src: Path, *, dry_run = False):    
    if (dst := Path(f'/etc/apt/{src.parent.name}/{src.name}')).exists():
        _logger.debug("apt config file already installed: %s", dst)
        return
   
    if (alt_dst := Path(f'/etc/apt/{src.parent.name}/{src.name}~')).exists():
        _logger.debug("apt config file already installed: %s", alt_dst)
        return
    

    if dry_run:
        _logger.info(f"{Color.YELLOW}Would{Color.RESET} install apt config file: {Color.CYAN}%s{Color.RESET}", dst)
        return

    _logger.info(f"Install apt config file: {Color.CYAN}%s{Color.RESET}", dst)
    run_process(['cp', src, dst], sudo=True, check=True)


def translate_apt_repository_specs(current: str, env: Env):
    target = ''
    for line in current.splitlines(keepends=True):
        if m := re.match(r'^\s*(?P<type>deb|deb-src)(?P<params>\s+\[[^\[\]]+\])?\s+(?P<url>[^\s\[\]]+)\s+(?P<distribution>[a-z0-9\-]+)\s+(?P<components>[a-z0-9][a-z0-9\- ]+[a-z0-9])\s*$', line):
            if env.apt_repository:
                url = env.apt_repository.get_private_url(m['url'], m['distribution']) or m['url']
            else:
                url = AptRepositoryDescription.get_public_url(m['url'], m['distribution']) or m['url']
            target += m['type'] + (m['params'] if m['params'] else '') + ' ' + url + ' ' + m['distribution'] + ' ' + m['components'] + '\n'
        else:
            target += line
    return target


class AptRepositoryDescription:
    _root: str|None
    """ Root URL for the private repositories. E.g. http://nexus/repository """
    
    _translations_by_public_url: dict[str,_AptRepositoryTranslation]
    """ List of available translations: associate public repository URLs (e.g. http://deb.debian.org/debian) and distribution names (e.g. bookworm) to private repository URLs (absolute or relative to root, e.g. /debian-bullseye). """

    _public_specs_by_private_url: dict[str,_AptPublicUrlWithDistribution]
    """ Reverse """

    _instances: list[AptRepositoryDescription] = []

    def __init__(self, data: dict[str,Any], *, origin: Path):
        if not isinstance(data, dict):
            raise TypeError(f'{origin.name}: invalid apt_repository type: {type(value).__name__}, expected dict')
        
        self._root = data.pop('root', None)
        if self._root is not None:
            if not isinstance(self._root, str):
                raise TypeError(f'{origin.name}: invalid apt_repository["root"] type: {type(self._root).__name__}, expected str')
            if not self._root.endswith('/'):
                self._root += '/'
        
        self._translations_by_public_url = {}
        for public_url, value in data.items():
            if not isinstance(public_url, str):
                raise TypeError(f'{origin.name}: invalid apt_repository key type (public URL): {type(public_url).__name__}, expected str')
            if not isinstance(value, dict):
                raise TypeError(f'{origin.name}: invalid apt_repository["{public_url}"] type: {type(value).__name__}, expected dict')
            
            private_urls_by_distribution = {}
            for distribution, private_url in value.items():
                if not isinstance(distribution, str):
                    raise TypeError(f'{origin.name}: invalid apt_repository["{public_url}"] subkey type (distribution name): {type(distribution).__name__}, expected str')
                if not isinstance(private_url, str):
                    raise TypeError(f'{origin.name}: invalid apt_repository["{public_url}"]["{distribution}"] type (private URL): {type(private_url).__name__}, expected str')
                if not '://' in private_url:
                    if self._root:
                        private_url = self._root + private_url.removeprefix('/')
                    else:
                        raise TypeError(f'{origin.name}: invalid apt_repository["{public_url}"]["{distribution}"] value "{private_url}": expected a URL')
                private_urls_by_distribution[distribution] = private_url

            self._translations_by_public_url[public_url] = _AptRepositoryTranslation(public_url, private_urls_by_distribution)
        
        # Build reverse
        self._public_specs_by_private_url = {}
        for public_url, translation in self._translations_by_public_url.items():
            for distribution, private_url in translation.private_urls_by_distribution.items():
                if not private_url in self._public_specs_by_private_url:
                    self._public_specs_by_private_url[private_url] = _AptPublicUrlWithDistribution(public_url, distribution)

        # Add duplicates to match http instead of https and trailing slash instead of no trailing slash
        for public_url, translation in list(self._translations_by_public_url.items()):
            for alt_public_url in self._iter_alt_urls(public_url, current_urls=self._translations_by_public_url.keys()):
                self._translations_by_public_url[alt_public_url] = translation
        
        for private_url, public_spec in list(self._public_specs_by_private_url.items()):
            for alt_private_url in self._iter_alt_urls(private_url, current_urls=self._translations_by_public_url.keys()):
                self._public_specs_by_private_url[alt_private_url] = public_spec

        self.__class__._instances.append(self)

    @cached_property
    def private_hostnames(self) -> list[str]:
        hosts = []

        def iter_urls():
            if self._root:
                yield self._root

            for translations in self._translations_by_public_url.values():
                yield from translations.private_urls_by_distribution.values()
                    
        for url in iter_urls():
            r = urlparse(url)
            if r.hostname and not r.hostname in hosts:
                hosts.append(r.hostname)

        return hosts
    
    def get_private_url(self, public_url: str, distribution: str) -> str|None:
        translation = self._translations_by_public_url.get(public_url)
        if translation:
            return translation.private_urls_by_distribution.get(distribution)
  
    @classmethod
    def get_public_url(cls, private_url: str, distribution: str) -> str|None:
        for instance in cls._instances:
            if public_spec := instance._public_specs_by_private_url.get(private_url):
                if public_spec.distribution == distribution:
                    return public_spec.public_url
        
    @classmethod
    def _iter_alt_urls(cls, url: str, *, current_urls: Iterable[str]):
        def invert_trailing(url: str):
            alt_url = None
            if url.endswith('/'):
                alt_url = url.removesuffix('/')
            else:
                alt_url = url + '/'
            if alt_url and not alt_url in current_urls:
                return alt_url
        
        # https / http
        alt_url = None
        if url.startswith('http://'):
            alt_url = url.removeprefix('http://') + 'https://'
        elif url.startswith('https://'):
            alt_url = url.removeprefix('https://') + 'http://'
        if alt_url and not alt_url in current_urls:
            yield alt_url
            if alt_url := invert_trailing(alt_url):
                yield alt_url
    
        # trailing slash / no trailing slash
        if alt_url := invert_trailing(url):
            yield alt_url

@dataclass
class _AptRepositoryTranslation:
    public_url: str
    private_urls_by_distribution: dict[str, str]

@dataclass
class _AptPublicUrlWithDistribution:
    public_url: str
    distribution: str
