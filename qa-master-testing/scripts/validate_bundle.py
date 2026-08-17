#!/usr/bin/env python3
"""Valida a distribuição neutra do pacote multiagente."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from run_contract import ALL_AGENTS


FORBIDDEN_TERMS = [
    bytes.fromhex(value).decode("utf-8")
    for value in (
        "636f646578", "6f70656e6169", "63686174677074", "636c61756465",
        "696e74656c6967c3aa6e636961206172746966696369616c",
    )
]
FORBIDDEN = re.compile("|".join(re.escape(value) for value in FORBIDDEN_TERMS), re.IGNORECASE)
TEXT_SUFFIXES = {".md", ".json", ".py", ".yaml", ".yml", ".txt"}


def validate_bundle(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifesto inválido: {exc}"]
    if manifest.get("name") != root.name:
        errors.append("nome do manifesto deve coincidir com a pasta raiz")
    if manifest.get("skills") != "../skills/":
        errors.append("manifesto deve apontar para ../skills/")
    required_skills = ["qa-master", *ALL_AGENTS]
    for name in required_skills:
        skill = root / "skills" / name / "SKILL.md"
        if not skill.is_file():
            errors.append(f"skill ausente: {name}")
    for required in (
        root / "assets" / "agent-output.schema.json",
        root / "scripts" / "init_run.py",
        root / "scripts" / "check_run.py",
        root / "scripts" / "run_framework.py",
    ):
        if not required.is_file():
            errors.append(f"arquivo obrigatório ausente: {required.relative_to(root)}")
    specific_directory = "." + bytes.fromhex("636f646578").decode("utf-8") + "-plugin"
    if (root / specific_directory).exists():
        errors.append("diretório técnico específico não permitido")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if FORBIDDEN.search(text):
            errors.append(f"referência não neutra: {path.relative_to(root)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar pacote multiagente neutro")
    parser.add_argument("bundle", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_bundle(args.bundle.resolve())
    if errors:
        print(f"Pacote inválido: {len(errors)} problema(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Pacote multiagente válido e neutro.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
