#!/usr/bin/env python3
"""Descobre stacks e ferramentas de teste sem executar código do projeto."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


MARKERS = {
    "python": {"pyproject.toml", "requirements.txt", "setup.py", "pytest.ini"},
    "node": {"package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"},
    "java": {"pom.xml", "build.gradle", "build.gradle.kts"},
    "dotnet": {"*.sln", "*.csproj"},
    "go": {"go.mod"},
    "rust": {"Cargo.toml"},
    "playwright": {"playwright.config.ts", "playwright.config.js", "playwright.config.py"},
    "cypress": {"cypress.config.ts", "cypress.config.js"},
    "openapi": {"openapi.yaml", "openapi.yml", "openapi.json", "swagger.yaml", "swagger.json"},
}
IGNORED = {".git", ".venv", "venv", "node_modules", "dist", "build", "reports", "__pycache__"}


def discover(root: Path) -> dict:
    if not root.is_dir():
        raise ValueError(f"Diretório não encontrado: {root}")
    files: list[Path] = []
    for item in root.rglob("*"):
        if item.is_file() and not IGNORED.intersection(item.relative_to(root).parts):
            files.append(item)
    names = {item.name for item in files}
    detected = {}
    for capability, patterns in MARKERS.items():
        matches = sorted({item.name for item in files for pattern in patterns if item.match(pattern) or item.name == pattern})
        if matches:
            detected[capability] = matches
    extensions = Counter(item.suffix.lower() or "<none>" for item in files)
    return {
        "root": str(root.resolve()),
        "file_count": len(files),
        "detected": detected,
        "top_extensions": dict(extensions.most_common(12)),
        "test_directories": sorted({part for item in files for part in item.relative_to(root).parts if part.lower() in {"test", "tests", "spec", "specs", "e2e"}}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Descobrir stack e ferramentas de um projeto")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    try:
        print(json.dumps(discover(Path(args.root)), ensure_ascii=False, indent=2))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

