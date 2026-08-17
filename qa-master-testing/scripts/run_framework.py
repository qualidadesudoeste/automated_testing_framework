#!/usr/bin/env python3
"""Instala e executa o framework determinístico embutido no plugin."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    plugin_root = Path(__file__).resolve().parents[1]
    wheels = sorted((plugin_root / "assets").glob("automated_software_testing_framework-*.whl"))
    if not wheels:
        print("Wheel do framework ausente em assets/.", file=sys.stderr)
        return 1
    wheel = wheels[-1]
    runtime = plugin_root / ".runtime"
    marker = runtime / f".{wheel.stem}.installed"
    if not marker.is_file():
        runtime.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "--target", str(runtime), str(wheel)]
        completed = subprocess.run(command, shell=False)
        if completed.returncode:
            return completed.returncode
        marker.write_text("ok\n", encoding="utf-8")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(runtime) + os.pathsep + environment.get("PYTHONPATH", "")
    return subprocess.call([sys.executable, "-m", "run_tests", *sys.argv[1:]], env=environment)


if __name__ == "__main__":
    raise SystemExit(main())
