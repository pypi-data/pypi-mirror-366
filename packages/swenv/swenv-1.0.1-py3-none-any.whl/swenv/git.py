from __future__ import annotations

import logging
import subprocess
from shutil import which

from swenv.env import Env
from swenv.utils import Color, run_process, verify_run_process

_logger = logging.getLogger(__name__)


def update_git(env: Env, *, dry_run = False):
    cmd = which('git')
    if cmd:
        _logger.debug('git command: %s', cmd)
    else:
        _logger.debug('git command not found')
        return
    
    _logger.info("Configure git")

    if env.proxy_host:
        proxy = f"http://:@{env.proxy_host}:{env.proxy_port}"
    else:
        proxy = None    
    _set_config("http.proxy", proxy, dry_run=dry_run)

    if env.git_repositories:
        for repo in env.git_repositories:
            _set_config(f"http.{repo}/.proxy", '', dry_run=dry_run)


def _get_config(name: str, *, system = False):
    args = ["git", "config", "--system" if system else "--global", name]
    cp = subprocess.run(args, text=True, capture_output=True)
    if cp.returncode == 1 and not cp.stdout and not cp.stderr:
        return None
    return verify_run_process(cp, strip='rstrip-newline', logger=_logger).stdout


def _set_config(name: str, value, *, dry_run = False, system = False):
    # Check current value
    current = _get_config(name, system=system)
    current_str = '(empty)' if current == '' else current
    value_str = '(empty)' if value == '' else value
    if current == value:
        _logger.debug("git: %s is already %s", name, value_str)
        return
    elif dry_run:
        _logger.info(f"git: {Color.YELLOW}would{Color.RESET} set {Color.CYAN}%s{Color.RESET} from {Color.GRAY}%s{Color.RESET} to {Color.CYAN}%s{Color.RESET}", name, current_str, value_str)
        return
    else:
        _logger.info(f"git: set {Color.CYAN}%s{Color.RESET} from {Color.GRAY}%s{Color.RESET} to {Color.CYAN}%s{Color.RESET}", name, current_str, value_str)

    # Set value
    if value is None:
        args = ["git", "config", "--system" if system else "--global", "--unset", name]
    else:
        args = ["git", "config", "--system" if system else "--global", name, str(value)]
    run_process(args, logger=_logger, capture_output=True)
