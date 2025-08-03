#
# ROADMAP? `NODE_TLS_REJECT_UNAUTHORIZED=0 npm install`
#
from __future__ import annotations

import logging
import sys
from shutil import which

from swenv.ca import CA_CERTIFICATES_BUNDLE
from swenv.env import Env
from swenv.utils import Color, run_process

_logger = logging.getLogger(__name__)


def update_npm(env: Env, *, dry_run = False):
    cmd = which('npm')
    if cmd:
        _logger.debug('npm command: %s', cmd)
    else:
        _logger.debug('npm command not found')
        return
    
    _logger.info("Configure npm")
    if env.npm_repository:
        _set_config("registry", f'{env.npm_repository}', dry_run=dry_run)
        if CA_CERTIFICATES_BUNDLE.exists():
            _set_config("cafile", str(CA_CERTIFICATES_BUNDLE), dry_run=dry_run)
    else:
        _set_config("registry", None, dry_run=dry_run)


def _get_config(name: str, *, system = False):
    args = ["npm", "config", "get", name]
    if system or sys.platform == 'win32':
        args.append('--global')
    
    value = run_process(args, logger=_logger, capture_output='rstrip-newline', shell=sys.platform == 'win32').stdout # shell necessary to call 'npm.cmd' on Windows
    if value == 'undefined':
        return None
    if name == 'registry' and value == 'https://registry.npmjs.org/':
        return None
    return value


def _set_config(name: str, value, *, dry_run = False, system = False):
    # Check current value
    current = _get_config(name, system=system)
    if current == value:
        _logger.debug("npm: %s is already %s", name, value)
        return
    elif dry_run:
        _logger.info(f"npm: {Color.YELLOW}would{Color.RESET} set {Color.CYAN}%s{Color.RESET} from {Color.GRAY}%s{Color.RESET} to {Color.CYAN}%s{Color.RESET}", name, current, value)
        return
    else:
        _logger.info(f"npm: set {Color.CYAN}%s{Color.RESET} from {Color.GRAY}%s{Color.RESET} to {Color.CYAN}%s{Color.RESET}", name, current, value)

    # Set value
    if value is None:
        args = ["npm", "config", "delete", name]
    else:
        args = ["npm", "config", "set", name, str(value)]
    if system or sys.platform == 'win32':
        args.append('--global')
    
    run_process(args, logger=_logger, shell=sys.platform == 'win32', capture_output=True) # shell necessary to call 'npm.cmd' on Windows
