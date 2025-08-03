from __future__ import annotations

import logging
from pathlib import Path
from shutil import which

from swenv.env import Env
from swenv.utils import Color, ensure_file, run_process

_logger = logging.getLogger(__name__)


def update_docker(env: Env, *, dry_run = False):
    cmd = which('docker')
    if cmd:
        _logger.debug('docker command: %s', cmd)
    else:
        _logger.debug('docker command not found')
        return
    
    target = Path('/etc/systemd/system/docker.service.d/proxy.conf')
    backup = Path('/etc/systemd/system/docker.service.d/proxy.conf~')
    if env.proxy_url:
        content = f"[Service]\n"
        content += f"Environment=\"HTTP_PROXY={env.proxy_url}\"\n"
        content += f"Environment=\"HTTPS_PROXY={env.proxy_url}\"\n"
        if env.no_proxy:
            content += f"Environment=\"NO_PROXY={env.no_proxy}\"\n"
        #NOTE/ROADMAP: il pourrait etre nécessaire d'adapter NO_PROXY pour Docker? Exemple : Environment="NO_PROXY=localhost,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16,10.0.0.0/8,.mycompany.lan"
    else:
        content = None
    change = ensure_file(target, content, dry_run=dry_run, backup=backup, sudo=True)

    if change:
        if dry_run:
            _logger.info(f"{Color.YELLOW}Would{Color.RESET} restart Docker service{Color.RESET}")
        else:
            _logger.info(f"Restart Docker service{Color.RESET}")
            if run_process(['systemctl', 'daemon-reload'], sudo=True).returncode != 0:
                _logger.error("Could not run systemctl daemon-reload")
                return
            if run_process(['systemctl', 'restart', 'docker'], sudo=True).returncode != 0:
                _logger.error("Could not run systemctl restart docker")
                return
