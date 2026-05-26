import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

_src = Path(__file__).parent / "src"
sys.path.insert(0, str(_src))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.config")

import django

django.setup()

_spec: Any = importlib.util.spec_from_file_location("_src_main", _src / "main.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
app = _mod.app
