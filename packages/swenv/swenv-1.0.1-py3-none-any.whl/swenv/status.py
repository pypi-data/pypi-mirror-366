from __future__ import annotations

import logging

from swenv.detect import detect_env
from swenv.env import ENVS, Env
from swenv.update import handle as handle_update
from swenv.utils import Color, get_wpad_config

_logger = logging.getLogger(__name__)


def handle():
    """
    Determine current environment and show what needs to be changed.
    """
    if not ENVS:
        _logger.warning("No environment configured. Run config command.")

    env = detect_env(display=True)

    handle_update(env, dry_run=True)
    
    for env in ENVS.values():
        display_wpad_status(env)


def display_wpad_status(env: Env):
    wpad = get_wpad_config(f'wpad.{env.domain}' if env.domain else 'wpad')
    if not wpad:
        return
    
    print(f"Configured proxy:      {Color.GRAY}{env.proxy_host}:{env.proxy_port}{Color.RESET}")
    print(f"Value read in WPAD:    {Color.CYAN}{wpad.proxy_host}:{wpad.proxy_port}{Color.RESET}")
    if wpad.proxy_host == env.proxy_host and wpad.proxy_port == env.proxy_port:
        print(f"                       {Color.GREEN}(identical){Color.RESET}")
    else:
        print(f"                       {Color.RED}(different){Color.RESET}")
    
    print("")
    print(f"Configured no_proxy:   {Color.GRAY}{env.no_proxy}{Color.RESET}")
    print(f"Value read in WPAD:    {Color.CYAN}{wpad.no_proxy}{Color.RESET}")

    conf_no_proxy_set = set(env.no_proxy.split(',')) if env.no_proxy else set()
    wpad_no_proxy_set = set(wpad.no_proxy.split(',')) if wpad.no_proxy else set()
    missing1 = wpad_no_proxy_set - conf_no_proxy_set
    missing2 = conf_no_proxy_set - wpad_no_proxy_set
    if not missing1 and not missing2:
        print(f"                       {Color.GREEN}(identical){Color.RESET}")
    else:
        print(f"                       {Color.RED}(different){Color.RESET}")
        if missing1:
            print(f"Missing in configured: {Color.YELLOW}{','.join(sorted(missing1))}{Color.RESET}")
        if missing2:
            print(f"Missing in WPAD:       {Color.YELLOW}{','.join(sorted(missing2))}{Color.RESET}")
