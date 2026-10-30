"""annetbox is needed by the netbox adapter only, annet works without it."""

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CODE = """
import importlib
import sys

sys.modules["annetbox"] = None  # annetbox is not installed

for name in (
    "annet",
    "annet.cli",
    "annet.gen",
    "annet.api",
    "annet.annlib.netdev.views.dump",
    "annet.adapters.file.provider",
    "annet.adapters.netbox.provider",
):
    importlib.import_module(name)

from annet.adapters.file.provider import Interface

assert Interface(name="eth0", description="uplink").dump("i") == [
    "i.description = 'uplink'",
    "i.enabled = True",
    "i.name = 'eth0'",
    "i.vrf = None",
]
"""


def test_annet_works_without_annetbox():
    result = subprocess.run(
        [sys.executable, "-c", CODE],
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
