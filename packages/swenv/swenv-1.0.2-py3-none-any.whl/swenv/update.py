from __future__ import annotations

import logging
from argparse import ArgumentParser

from swenv.apt import update_apt
from swenv.ca import update_ca
from swenv.detect import detect_env
from swenv.docker import update_docker
from swenv.env import ENVS, Env
from swenv.git import update_git
from swenv.npm import update_npm
from swenv.pip import update_pip
from swenv.proxy import update_proxy
from swenv.utils import Color

_logger = logging.getLogger(__name__)

def add_arguments(parser: ArgumentParser):
    parser.add_argument('env', nargs='?', choices=ENVS.keys(), help="Target environment (automatically detected if none is given).")
    parser.add_argument('-n', '--dry-run', action='store_true', help="Show what would be done but do not modify any configuration.")

    group = parser.add_argument_group(title='modules', description="(all are updated if no module if given)")
    group.add_argument('--ca', action='store_true', help="Configure ca-certificates.")
    group.add_argument('--proxy', action='store_true', help="Configure proxy environment variables.")
    group.add_argument('--apt', action='store_true', help="Configure apt (Debian package manager).")
    group.add_argument('--git', action='store_true', help="Configure git (source code version manager).")
    group.add_argument('--pip', action='store_true', help="Configure pip (python package manager).")
    group.add_argument('--npm', action='store_true', help="Configure npm (node/javascript package manager).")
    group.add_argument('--docker', action='store_true', help="Cconfigure docker.")


def handle(env: Env|str|None = None, *, ca = False, proxy = False, apt = False, git = False, pip = False, npm = False, docker = False, dry_run = False):
    """
    Update system and application settings for the given environment (or the detected environment if none is given).
    """
    if isinstance(env, str):
        env = ENVS[env]
    elif not env:
        env = detect_env()

    _logger.info(f"Target environment: {Color.CYAN}%s{Color.RESET}", env)

    if not ca and not proxy and not apt and not git and not pip and not npm and not docker:
        ca = proxy = apt = git = pip = npm = docker = True

    if ca:
        update_ca(env, dry_run=dry_run)
    if proxy:
        update_proxy(env, dry_run=dry_run)
    if apt:
        update_apt(env, dry_run=dry_run)
    if git:
        update_git(env, dry_run=dry_run)
    if pip:
        update_pip(env, dry_run=dry_run)
    if npm:
        update_npm(env, dry_run=dry_run)
    if docker:
        update_docker(env, dry_run=dry_run)
