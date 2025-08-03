from __future__ import annotations

import logging
import os
import re
import sys
import urllib.request
from argparse import ArgumentParser
from pathlib import Path
from shutil import which
from urllib.error import HTTPError, URLError

from swenv.apt import configure_apt
from swenv.env import ENVS, load_envs
from swenv.settings import DATA_DIR, DEFAULT_CONFIG_URL
from swenv.utils import Color, check_port, get_wpad_config, unzip

_logger = logging.getLogger(__name__)

BIN_DIR = Path(__file__).resolve().parent.joinpath('bin')


def add_arguments(parser: ArgumentParser):
    parser.add_argument('-n', '--dry-run', action='store_true', help="show what would be done but do not modify any configuration")


def handle(*, dry_run = False):
    """
    Configure swenv command (e.g. add to PATH if not already).
    """
    configure_swenv_command(dry_run=dry_run)
    unzipped = create_swenv_config(dry_run=dry_run)
    display_envs(unzipped)
    configure_apt(dry_run=dry_run)


def display_envs(need_reload: bool = False):
    global ENVS

    if need_reload:
        ENVS = load_envs()

    if not ENVS:
        _logger.info("No environment configured")
    else:
        for env in ENVS.values():
            _logger.info(f"Available environment: {Color.CYAN}{env.name}{Color.RESET} {Color.GRAY}(definition: {env.path}){Color.RESET}")


def create_swenv_config(dry_run = False) -> bool:
    """
    Create configuration directory, trying to import default configuration from Nexus.
    """
    if DATA_DIR.exists():
        _logger.info(f"Configuration directory: {Color.CYAN}{DATA_DIR}{Color.RESET}")
        return False

    if dry_run:
        _logger.info(f"{Color.YELLOW}Would{Color.RESET} create configuration directory: {Color.CYAN}%s{Color.RESET}", DATA_DIR)
        return False
    else:
        _logger.info(f"Create configuration directory: {Color.CYAN}%s{Color.RESET}", DATA_DIR)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if '{nexus}' in DEFAULT_CONFIG_URL:
        # Determine nexus hostname
        wpad = get_wpad_config()
        if not wpad:
            nexus_host = 'nexus'
        else:
            domain = wpad.proxy_domain
            nexus_host = 'nexus' + (f'.{domain}' if domain else '')

        # Check if nexus port is opened
        if not check_port(nexus_host, 80, timeout=1.0):
            _logger.info(f"Nexus host not available: {Color.GRAY}{nexus_host}{Color.RESET}")
            return False
        default_config_url = DEFAULT_CONFIG_URL.format(nexus=nexus_host)
    else:
        default_config_url = DEFAULT_CONFIG_URL
    
    # Download from nexus
    default_config = DATA_DIR.joinpath('.default.zip')
    try:
        _logger.info(f"Try downloading default configuration at: {Color.CYAN}%s{Color.RESET}", default_config_url)
        urllib.request.urlretrieve(default_config_url, default_config)
    except HTTPError as err:
        _logger.error(f"Cannot retrieve default configuration: {Color.RED}HTTP {err.status} {err.reason}{Color.RESET}")
        return False
    except URLError as err:
        _logger.error(f"Cannot retrieve default configuration: {Color.RED}{err.reason}{Color.RESET}")
        return False
    
    # Unzip config
    _logger.info(f"Extract default configuration")
    unzip(default_config, DATA_DIR, omit_single_dir=True)
    return True


def configure_swenv_command(dry_run = False):
    cmd = which('swenv')
    if cmd:
        _logger.info(f'Command {Color.CYAN}swenv{Color.RESET} is installed {Color.GRAY}(location: %s){Color.RESET}', cmd)
        return
    else:
        _logger.debug('swenv command not found')

    if dry_run:
        _logger.info(f"{Color.YELLOW}Would{Color.RESET} install command {Color.CYAN}swenv{Color.RESET}")
        return
    else:
        _logger.info(f"Install command {Color.CYAN}swenv{Color.RESET}")

    if not BIN_DIR.exists():
        _logger.error("Directory not found: %s", BIN_DIR)
        return
    
    if sys.platform == 'win32':
        add_to_os_path(BIN_DIR, dry_run=dry_run)
    else:
        home_bin_dir = f"{os.environ['HOME']}/.local/bin"
        os.makedirs(home_bin_dir, exist_ok=True)
        if add_to_os_path(home_bin_dir, dry_run=dry_run):
            print("Restart your shell to take PATH modification into account: exec $SHELL --login")

        link = Path(f"{home_bin_dir}/swenv")
        target = BIN_DIR.joinpath('swenv')
        if link.exists():
            if link.is_symlink():
                current_target = link.readlink().resolve()
            else:
                current_target = None

            if current_target == target.resolve():
                _logger.debug("Symlink %s already points to %s", link, target)
            else:
                _logger.info("Replace %s by a symlink to %s", link, target)
                link.unlink()
                link.symlink_to(target)
        elif dry_run:
            _logger.info(f"{Color.YELLOW}Would{Color.RESET} create symlink %s to %s", link, target)
        else:
            _logger.info("Create symlink %s to %s", link, target)
            link.symlink_to(target)


def add_to_os_path(directory: str|Path, *, dry_run = False, remove = False):
    if isinstance(directory, Path):
        directory = str(directory)
    directory = directory.removesuffix('/').removesuffix('\\')

    if sys.platform == 'win32':
        import ctypes
        import winreg

        directory = directory.replace('/', '\\')

        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:
            with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                current_path = [d for d in winreg.QueryValueEx(key, 'PATH')[0].split(';') if d]
                if remove:
                    if not directory in current_path:
                        _logger.debug("Already not in PATH: %s", directory)
                        return False
                    elif dry_run:
                        _logger.info(f"{Color.YELLOW}Would{Color.RESET} remove from PATH: %s", directory)
                        return False
                    else:
                        _logger.info("Remove from PATH: %s", directory)
                    new_path = ';'.join([d for d in current_path if d != directory])
                else:
                    if directory in current_path:
                        _logger.debug("Already in PATH: %s", directory)
                        return False
                    elif dry_run:
                        _logger.info(f"{Color.YELLOW}Would{Color.RESET} append to PATH: %s", directory)
                        return False
                    else:
                        _logger.info("Append to PATH: %s", directory)
                    new_path = ';'.join([*current_path, directory])
                
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)                                
                
                # Tell other processes to update their environment.
                # (It is still required to restart the current change for changes to take effect)
                HWND_BROADCAST = 0xFFFF
                WM_SETTINGCHANGE = 0x1A
                SMTO_ABORTIFHUNG = 0x0002
                result = ctypes.c_long()
                SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
                SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, u"Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(result),)

                return True
    else:
        def get_path(file: str):
            full = f"{os.environ['HOME']}/{file}"
            path = []
            with open(full, "r") as fp:
                for line in fp:
                    line = line.strip()
                    if line.startswith('#'):
                        continue
                    if m := re.match(r'^(?:export\s+)?PATH="?([^"]+)"?\s*[\\;]?$', line, re.IGNORECASE):
                        for p in m[1].split(':'):
                            if p != '$PATH':
                                path.append(p.replace('$HOME', os.environ['HOME']))
            return path
        
        def remove_from_path(file: str, directory: str):
            full = f"{os.environ['HOME']}/{file}"
            if directory.startswith(f"{os.environ['HOME']}/"):
                directory = '$HOME/' + directory.removeprefix(f"{os.environ['HOME']}/")
            target = ''
            found = False
            with open(full, "r") as fp:
                for line in fp:
                    if re.match(r'^\s#', line):
                        target += line
                    elif m := re.match(r'^\s*((?:export\s+)?PATH="?)([^"]+)("?\s*[\\;]?)\s*$', line, re.IGNORECASE):
                        target_path = []
                        for p in m[2].split(':'):
                            if p == directory:
                                found = True
                            else:
                                target_path.append(p)
                        if target_path != ['$PATH']:
                            target += m[1] + ':'.join(target_path) + m[3]
                    else:
                        target += line
            if found:
                with open(full, "w") as fp:
                    fp.write(target)
            return found
        
        def append_to_path(file: str, directory: str):
            full = f"{os.environ['HOME']}/{file}"
            if directory.startswith(f"{os.environ['HOME']}/"):
                directory = '$HOME/' + directory.removeprefix(f"{os.environ['HOME']}/")
            with open(full, "a") as fp:
                fp.write(f"\nPATH=\"{directory}:$PATH\"\n")

        current_profile_path = get_path('.profile')
        current_bashrc_path = get_path('.bashrc')

        if remove:
            if not (directory in current_profile_path and directory in current_bashrc_path):
                _logger.debug("Already not in PATH: %s", directory)
                return False
            elif dry_run:
                _logger.info(f"{Color.YELLOW}Would{Color.RESET} remove from PATH: %s", directory)
                return False
            else:
                _logger.info("Remove from PATH: %s", directory)
        else:
            if directory in current_profile_path and directory in current_bashrc_path:
                _logger.debug("Already in PATH: %s", directory)
                return False
            elif dry_run:
                _logger.info(f"{Color.YELLOW}Would{Color.RESET} append to PATH: %s", directory)
                return False
            else:
                _logger.info("Append to PATH: %s", directory)

        if remove:
            if directory in current_profile_path:
                if remove_from_path('.profile', directory):
                    os.system(f". {os.environ['HOME']}/.profile")
            if directory in current_bashrc_path:
                if remove_from_path('.bashrc', directory):
                    os.system(f". {os.environ['HOME']}/.bashrc")
        else:
            if not directory in current_profile_path:
                append_to_path('.profile', directory)
                os.system(f". {os.environ['HOME']}/.profile")
            if not directory in current_bashrc_path:
                append_to_path('.bashrc', directory)
                os.system(f". {os.environ['HOME']}/.bashrc")

        return True
