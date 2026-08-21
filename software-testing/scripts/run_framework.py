#!/usr/bin/env python3
"""Executa o framework no repositório ou instala o wheel embutido localmente."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    repository_root = skill_root.parent
    repository_runner = repository_root / "run_tests.py"
    if repository_runner.is_file():
        # Não fixar cwd no repositório do framework: isso forçaria toda execução de
        # volta para este repo mesmo quando o chamador pretende testar outro projeto.
        # O cwd do processo chamador é preservado; caminhos relativos em --config/--output
        # continuam resolvendo a partir de onde o usuário invocou a skill.
        return subprocess.call([sys.executable, str(repository_runner), *sys.argv[1:]])

    wheels = sorted((skill_root / "assets").glob("automated_software_testing_framework-*.whl"))
    if not wheels:
        print("Wheel do framework ausente em assets/. Regenere o pacote da skill.", file=sys.stderr)
        return 1
    wheel = wheels[-1]
    runtime = skill_root / ".runtime"
    marker = runtime / f".{wheel.stem}.installed"
    if not marker.is_file():
        runtime.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "--target", str(runtime), str(wheel)]
        completed = subprocess.run(command, shell=False)
        if completed.returncode:
            print("Falha ao instalar o runtime local da skill.", file=sys.stderr)
            return completed.returncode
        marker.write_text("ok\n", encoding="utf-8")

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(runtime) + os.pathsep + environment.get("PYTHONPATH", "")
    return subprocess.call([sys.executable, "-m", "run_tests", *sys.argv[1:]], env=environment)


if __name__ == "__main__":
    raise SystemExit(main())

