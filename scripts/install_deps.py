"""
SessionStart hook: install Python dependencies into ${CLAUDE_PLUGIN_DATA}/.venv.

Creates the venv on first run if it doesn't exist, then runs pip install only
when requirements.txt changes. Uses stdlib only — no third-party packages required.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

plugin_root = Path(os.environ["CLAUDE_PLUGIN_ROOT"])
plugin_data = Path(os.environ["CLAUDE_PLUGIN_DATA"])

src = plugin_root / "requirements.txt"
cached = plugin_data / "requirements.txt"
venv = plugin_data / ".venv"
venv_python = venv / ("Scripts" if sys.platform == "win32" else "bin") / "python"

plugin_data.mkdir(parents=True, exist_ok=True)

# Create venv if it doesn't exist
if not venv_python.exists():
    result = subprocess.run([sys.executable, "-m", "venv", str(venv)], capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(result.returncode)

if cached.exists() and cached.read_bytes() == src.read_bytes():
    sys.exit(0)  # nothing changed, skip install

result = subprocess.run(
    [str(venv_python), "-m", "pip", "install", "-r", str(src), "-q"],
    capture_output=True,
)

if result.returncode != 0:
    # Remove cached copy so the next session retries
    cached.unlink(missing_ok=True)
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)

shutil.copy2(src, cached)
