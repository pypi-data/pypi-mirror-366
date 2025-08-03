from __future__ import annotations

import os
from pathlib import Path

from swenv.utils import get_app_data_dir

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = get_app_data_dir('swenv', BASE_DIR)

DEFAULT_CONFIG_URL = os.environ.get('SWENV_DEFAULT_CONFIG_URL', 'http://{nexus}/swenv-config.zip')
