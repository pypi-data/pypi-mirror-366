from __future__ import annotations

import logging
import subprocess
from shutil import which
from urllib.parse import urlparse

from swenv.env import Env
from swenv.utils import Color, run_process, verify_run_process

_logger = logging.getLogger(__name__)


def update_pip(env: Env, *, dry_run = False):
    cmd = which('pip')
    if cmd:
        _logger.debug('pip command: %s', cmd)
    else:
        _logger.debug('pip command not found')
        return

    _logger.info("Configure pip")
    if env.pip_repository:
        trusted_hosts = []
        if host := urlparse(env.pip_repository).hostname:
            trusted_hosts.append(host)
        if env.git_repositories:
            for url in env.git_repositories:
                host = urlparse(url).hostname
                if host and not host in trusted_hosts:
                    trusted_hosts.append(host)

        _set_config("global.index", f"{env.pip_repository}/pypi", dry_run=dry_run)
        _set_config("global.index-url", f"{env.pip_repository}/simple", dry_run=dry_run)
        _set_config("global.trusted-host", ' '.join(trusted_hosts), dry_run=dry_run)
    else:
        _set_config("global.index", None, dry_run=dry_run)
        _set_config("global.index-url", None, dry_run=dry_run)
        _set_config("global.trusted-host", None, dry_run=dry_run)


def _get_config(name: str, *, system = False):
    args = ["pip", "config", "get", name]
    if system:
        args.append('--global')
    
    cp = subprocess.run(args, text=True, capture_output=True)
    if cp.returncode == 1 and cp.stderr.startswith("ERROR: No such key - "):
        return None
    return verify_run_process(cp, strip='rstrip-newline', logger=_logger).stdout


def _set_config(name: str, value, *, dry_run = False, system = False):
    # Check current value
    current = _get_config(name, system=system)
    if current == value:
        _logger.debug("pip: %s is already %s", name, value)
        return
    elif dry_run:
        _logger.info(f"pip: {Color.YELLOW}would{Color.RESET} set {Color.CYAN}%s{Color.RESET} from {Color.GRAY}%s{Color.RESET} to {Color.CYAN}%s{Color.RESET}", name, current, value)
        return
    else:
        _logger.info(f"pip: set {Color.CYAN}%s{Color.RESET} from {Color.GRAY}%s{Color.RESET} to {Color.CYAN}%s{Color.RESET}", name, current, value)

    # Set value
    if value is None:
        args = ["pip", "config", "unset", name]
    else:
        args = ["pip", "config", "set", name, str(value)]
    if system:
        args.append('--global')
    
    run_process(args, logger=_logger, capture_output=True)
