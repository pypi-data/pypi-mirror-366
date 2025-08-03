from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from swenv.settings import DATA_DIR
from swenv.utils import Color, download, is_sudo_available, run_process

if TYPE_CHECKING:
    from swenv.env import Env

CA_CERTIFICATES_BUNDLE = DATA_DIR.joinpath('ca-certificates.crt') if sys.platform == 'win32' else Path('/etc/ssl/certs/ca-certificates.crt')

_logger = logging.getLogger(__name__)

def update_ca(env: Env, *, dry_run = False):
    if os.path.exists(CA_CERTIFICATES_BUNDLE):
        ca_certificates = get_certificates_from_bundle(CA_CERTIFICATES_BUNDLE)            
        if not ca_certificates:
            _logger.error("No certificates found in %s", CA_CERTIFICATES_BUNDLE)
            return
    elif sys.platform == 'win32':
        if dry_run:
            _logger.info(f"{Color.YELLOW}Would{Color.RESET} download CA certificates bundle to {Color.CYAN}%s{Color.RESET}", CA_CERTIFICATES_BUNDLE)
        else:
            _logger.info(f"Download CA certificates bundle to {Color.CYAN}%s{Color.RESET}", CA_CERTIFICATES_BUNDLE)
            # See: https://github.com/certifi/python-certifi
            origin = "https://github.com/certifi/python-certifi/raw/refs/heads/master/certifi/cacert.pem"
            download(origin, CA_CERTIFICATES_BUNDLE, env=env)
        ca_certificates = []
    else:
        _logger.error("CA certificates bundle not found: %s", CA_CERTIFICATES_BUNDLE)
        return
    
    src_dir = DATA_DIR.joinpath('ca-certificates')
        
    missing: list[Path] = []
    if src_dir.exists():
        for path in src_dir.iterdir():
            for content in get_certificates_from_bundle(path):
                if not content in ca_certificates:
                    missing.append(path)
                    break

    if not missing:
        return
        
    _logger.info("Configure ca-certificates")
    if sys.platform == 'win32':
        run_update_ca_certificates_win32(missing, dry_run=dry_run)
    else:
        run_update_ca_certificates_linux(missing, dry_run=dry_run)
    
    
def get_certificates_from_bundle(path: Path) -> list[str]:
    contents: list[str] = []

    content: str|None = None
    with open(path, 'r', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if line == '-----BEGIN CERTIFICATE-----':
                content = ''
            elif line == '-----END CERTIFICATE-----':
                if content:
                    contents.append(content)
            elif content is not None:
                content += line

    return contents


def run_update_ca_certificates_win32(missing: list[Path], *, dry_run = False):
    if dry_run:
        for path in missing:
            _logger.info(f"{Color.YELLOW}Would{Color.RESET} install CA certificate {Color.CYAN}%s{Color.RESET}", path)
    
    else:
        with open(CA_CERTIFICATES_BUNDLE, 'a', encoding='ascii') as fp:
            for path in missing:
                _logger.info(f"Install CA certificate {Color.CYAN}%s{Color.RESET}", path)
                content = path.read_text(encoding='ascii').strip()
                fp.write('\n')
                fp.write(content)
                fp.write('\n')


def run_update_ca_certificates_linux(missing: list[Path], *, dry_run = False):
    if dry_run:
        _logger.info(f"{Color.YELLOW}Would{Color.RESET} install CA certificate {Color.CYAN}%s{Color.RESET}", CA_CERTIFICATES_BUNDLE)
        
    issue = False
    if os.path.exists('/usr/sbin/update-ca-certificates') or os.path.exists('/usr/bin/update-ca-certificates'):
        _logger.debug('update-ca-certificates command exists')
    else:
        _logger.error("Cannot configure ca-certificates: missing ca-certificates package")
        issue = True
    
    if not is_sudo_available():
        _logger.error("Cannot configure ca-certificates: sudo not available")
        issue = True
    
    if issue or dry_run:
        return
    
    run_process(['mkdir' '-p', '/usr/local/share/ca-certificates'], sudo=True)
    for path in missing:
        target = f'/usr/local/share/ca-certificates/{path.name}'
        _logger.info(f"Install CA certificate {Color.CYAN}%s{Color.RESET}", target)
        run_process(['cp', '-p', path, target], sudo=True)
        run_process(['chown', 'root:staff', target], sudo=True)
        
    _logger.info("Run update-ca-certificates")
    run_process(['update-ca-certificates'], sudo=True)
