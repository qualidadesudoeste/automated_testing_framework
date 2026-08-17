#!/usr/bin/env python3
"""Cria um manifesto que torna omissões de cobertura visíveis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_manifest import new_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Inicializar manifesto de auditoria QA Mestre")
    parser.add_argument("output", type=Path, help="Caminho de audit-manifest.json")
    parser.add_argument("--force", action="store_true", help="Sobrescrever manifesto existente")
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists() and not args.force:
        parser.error(f"o arquivo já existe: {output}; use --force conscientemente")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(new_manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
