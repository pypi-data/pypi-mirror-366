from __future__ import annotations

import logging
import os
import re
import sys
from contextlib import nullcontext
from pathlib import Path
from shutil import which
from tempfile import mktemp
from typing import TYPE_CHECKING, TextIO

from swenv.settings import DATA_DIR
from swenv.utils import Color, ensure_file, is_sudo_available, run_process

if TYPE_CHECKING:
    from swenv.env import Env

_logger = logging.getLogger(__name__)


def update_proxy(env: Env, *, dry_run = False):
    update_pac(env, dry_run=dry_run)

    if sys.platform == 'win32':
        pass # ROADMAP
    else:
        if env.shell_env:
            update_shell_env(env, dry_run=dry_run)
            update_sudoers_env(dry_run=dry_run)


def update_pac(env: Env, *, dry_run = False):
    target = DATA_DIR.joinpath('proxy.pac')
    content = '// Automatically created and managed by swenv\n'
    content += 'function FindProxyForURL(url, host) {\n'
    if env.proxy_host:
        if env.no_proxy:
            for host in env.no_proxy.split(','):
                content += _get_noproxy_pac_code(host)
        content += f'  return "PROXY {env.proxy_host}:{env.proxy_port}";\n'
    else:
        content += '  return "DIRECT";\n'
    content += '}\n' 
    ensure_file(target, content, dry_run=dry_run)


def _get_noproxy_pac_code(host: str):
    if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', host): # ip address
        return f'  if (isInNet(host, "{host}", "255.255.255.255")) return "DIRECT";\n'
    elif re.match(r'^(\d{1,3}\.){1,3}\*$', host): # network
        dots = host.count('.')
        host = host[0:-2] + '.0' * (4 - dots)
        mask = ('.255' * dots + '.0' * (4 - dots)).lstrip('.')
        return f'  if (isInNet(host, "{host}", "{mask}")) return "DIRECT";\n'
    elif re.match(r'^[^"\'\n\r]+$', host, re.IGNORECASE): # domain    
        return f'  if (dnsDomainIs(host, "{host}")) return "DIRECT";\n'
    else:
        raise ValueError(f"Invalid argument 'host': {host}")

      
def update_shell_env(env: Env, *, dry_run = False):
    # User config
    update_shell_env_file(env, Path.home().joinpath('.bashrc'), remove=True, dry_run=dry_run)
    update_shell_env_file(env, Path.home().joinpath('.profile'), dry_run=dry_run)
    
    # System config
    target = Path('/etc/profile.d/proxy.sh')
    if env.proxy_host:
        tmp = None
        try:
            # Détermine le contenu attendu du fichier
            tmp = mktemp()
            update_shell_env_file(env, tmp, quiet=True)         
            with open(tmp, 'r', encoding='utf-8') as fp:
                expected_content = fp.read()

            # Vérifie le contenu actuel
            current_content = None
            if target.exists():
                current_content = None
                with open(target, 'r', encoding='utf-8') as fp:
                    current_content = fp.read()
            
            if current_content != expected_content:
                if dry_run:
                    _logger.info(f"{Color.YELLOW}Would{Color.RESET} update %s", target)
                elif not is_sudo_available():
                    _logger.warning("Skip updating %s (no sudo)", target)
                else:
                    _logger.info("Update %s", target)
                    if run_process(['cp', tmp, target], sudo=True).returncode != 0:
                        _logger.error("Could not update %s", target)
        finally:
            if tmp is not None:
                os.unlink(tmp)
        
    else: # no proxy
        if target.exists():
            if dry_run:
                _logger.info(f"{Color.YELLOW}Would{Color.RESET} delete %s", target)
            elif not is_sudo_available():
                _logger.warning("Skip deleting %s (no sudo)", target)
            else:
                _logger.info("Delete %s", target)
                if run_process(['rm', target], sudo=True).returncode != 0:
                    _logger.error("Could not delete %s", target)


def update_sudoers_env(*, dry_run = False):
    if not which('sudo'):
        return
    
    target = Path('/etc/sudoers.d/env-proxy')
    if target.exists():
        return

    if dry_run:
        _logger.info(f"{Color.YELLOW}Would{Color.RESET} create %s", target)
    elif not is_sudo_available():
        _logger.warning("Skip creating %s (no sudo)", target)
    else:
        _logger.info("Create %s", target)
        if run_process(['sh', '-c', f'echo "Defaults env_keep += \\\"HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy no_proxy\\\"" > {target}'], sudo=True).returncode != 0:
            _logger.error("Could not create %s", target)
        elif run_process(['chmod', '440', target], sudo=True).returncode != 0:
            _logger.error("Could not chmod %s", target)


def update_shell_env_file(env: Env, path: str|os.PathLike|TextIO, *, remove: bool|None = None, quiet = False, dry_run = False):
    target = ''

    change: list[str] = []
    uptodate: list[str] = []
        
    http_proxy_ref = False
    no_proxy_ref = False
    last_newline = False
    any_line = False

    if remove is None:
        remove = False if env.proxy_host else True

    if not isinstance(path, (str,os.PathLike)) or os.path.exists(path):
        with open(path, "r") if isinstance(path, (str,os.PathLike)) else nullcontext(path) as fp:
            for line in fp:
                if line != '':
                    any_line = True
                last_newline = line == '\n'

                if m := re.match(r'^\s*(?P<comment>#)?\s*(?P<prefix>(?:export\s+)?)(?P<name>[a-zA-Z_]+)="?(?P<value>[^"]+)"?(?P<suffix>\s*;?)\s*$', line):
                    if remove:
                        if not m['comment'] and m['name'] in {'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'}:
                            change.append(m['name'])
                            target += f'# {line}'
                        else:
                            target += line
                    else:
                        expected_value = None
                        
                        if m['name'] in {'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy'}:
                            if m['name'] == 'HTTP_PROXY':
                                http_proxy_ref = True
                                expected_value = env.proxy_url or ''
                            elif not http_proxy_ref:
                                expected_value = env.proxy_url or ''
                            else:
                                expected_value = f"$HTTP_PROXY"
                        
                        elif m['name'] in {'NO_PROXY', 'no_proxy'}:
                            if m['name'] == 'NO_PROXY':
                                no_proxy_ref = True
                                expected_value = env.no_proxy or ''
                            elif not no_proxy_ref:
                                expected_value = env.no_proxy or ''
                            else:
                                expected_value = f"$NO_PROXY"

                        if expected_value is not None:
                            if m['comment'] or m['value'] != expected_value:
                                change.append(m['name'])
                                target += f"export {m['name']}=\"{expected_value}\"\n"
                            else:
                                uptodate.append(m['name'])
                                target += line
                        else:
                            target += line
                else:
                    target += line

    if remove:
        if change:
            if dry_run:
                if not quiet:
                    _logger.info(f"{Color.YELLOW}Would{Color.RESET} remove %s from %s", ', '.join(change), path)
            else:
                if not quiet:
                    _logger.info("Remove %s from %s", ', '.join(change), path)
                with open(path, "w") if isinstance(path, (str,os.PathLike)) else nullcontext(path) as fp:
                    fp.write(target)
    else:
        first = True

        def append(name: str, value: str):
            nonlocal first, target
            if first:
                if any_line and not last_newline:
                    target += '\n'
                first = False
            target += f"export {name}=\"{value}\"\n"

        for name in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            if not name in uptodate and not name in change:
                change.append(name)
                if name == 'HTTP_PROXY':
                    http_proxy_ref = True
                    append(name, env.proxy_url or '')
                elif not http_proxy_ref:                    
                    append(name, env.proxy_url or '')
                else:
                    append(name, "$HTTP_PROXY")
        
        for name in ['NO_PROXY', 'no_proxy']:
            if not name in uptodate and not name in change:
                change.append(name)
                if name == 'NO_PROXY':
                    no_proxy_ref = True
                    append(name, env.no_proxy or '')
                elif not no_proxy_ref:
                    append(name, env.no_proxy or '')
                else:
                    append(name, "$NO_PROXY")

        if change:
            if dry_run:                
                if not quiet:
                    _logger.info(f"{Color.YELLOW}Would{Color.RESET} set %s in %s", ', '.join(change), path)
            else:                
                if not quiet:
                    _logger.info("Set %s in %s", ', '.join(change), path)
                with open(path, "w") if isinstance(path, (str,os.PathLike)) else nullcontext(path) as fp:
                    fp.write(target)
    
    return change


def get_proxy_env(env: Env):   
    environ = dict(os.environ)
    if env.proxy_url:
        for name in {'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy'}:
            environ[name] = env.proxy_url
        if env.no_proxy:
            for name in ['NO_PROXY', 'no_proxy']:
                environ[name] = env.no_proxy
    else:
        for name in {'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy'}:
            environ.pop(name, None)
    return environ
