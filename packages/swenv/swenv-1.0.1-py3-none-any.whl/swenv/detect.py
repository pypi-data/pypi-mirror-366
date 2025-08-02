from __future__ import annotations

import logging
from threading import Thread
from time import sleep, time

from swenv.env import DIRECT_ENV, ENVS, Env
from swenv.utils import Color, check_port

_logger = logging.getLogger(__name__)


def detect_env(*, display = False) -> Env:
    if not ENVS:
        _logger.warning("No environment configured")
        return DIRECT_ENV
    
    first_found_env = None

    for env in ENVS.values():
        is_current = check_env(env)
        if display:
            _logger.info(f"Detect environment: {Color.CYAN}%s{Color.RESET}: %s", env.name, f'{Color.GREEN}yes{Color.RESET}' if is_current else f'{Color.GRAY}no{Color.RESET}')
            if is_current and not first_found_env:
                first_found_env = env
        else:
            if is_current:
                return env
            
    return first_found_env or DIRECT_ENV


_check_results: dict[str,bool] = {}

def check_env(env: Env, *, timeout = 1.0, force = False) -> bool:
    if not force and env.name in _check_results:
        return _check_results[env.name]

    if not env.dns_servers:
        _logger.warning("Cannot check env %s: no dns servers configured", env.name)
        _check_results[env.name] = False
        return _check_results[env.name]
    
    results: list[bool] = []
    port = 53

    def run(host: str):
        result = check_port(host, port, timeout=timeout) is not None
        results.append(result)

    threads: list[Thread] = []
    for server in env.dns_servers:
        thread = Thread(target=lambda: run(server), daemon=True)
        thread.start()
        threads.append(thread)

    def check_results():
        while True:
            try:
                if results.pop():
                    return True
            except IndexError:
                return False

    # Wait for at least one thread to return True, or for all threads to complete, with a timeout
    stop_time = time() + timeout
    while time() < stop_time:
        if check_results():
            _check_results[env.name] = True
            return _check_results[env.name]

        if any(t.is_alive() for t in threads):
            sleep(0.1)
        else:
            _check_results[env.name] = check_results()
            return _check_results[env.name]
        
    _check_results[env.name] = check_results()
    return _check_results[env.name]
