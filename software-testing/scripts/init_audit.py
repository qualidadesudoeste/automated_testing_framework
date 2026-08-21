#!/usr/bin/env python3
"""Cria um manifesto que torna omissões de cobertura visíveis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_manifest import new_manifest


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inicializar manifesto de auditoria QA Mestre")
    parser.add_argument("output", type=Path, help="Caminho de audit-manifest.json")
    parser.add_argument(
        "--project-root", type=Path, required=True,
        help="Raiz do projeto-alvo auditado. O diretório de saída nunca pode ficar dentro dela: "
             "entregáveis vivem fora do repositório testado, nunca versionados junto com ele.",
    )
    parser.add_argument("--force", action="store_true", help="Sobrescrever manifesto existente")
    args = parser.parse_args(argv)

    output = args.output.resolve()
    project_root = args.project_root.resolve()
    if is_inside(output, project_root):
        parser.error(
            f"diretório de saída dentro do projeto-alvo: {output} está sob {project_root}. "
            "Use um caminho fora do repositório auditado (ex.: pasta temporária do sistema ou "
            "diretório irmão do projeto)."
        )
    if output.exists() and not args.force:
        parser.error(f"o arquivo já existe: {output}; use --force conscientemente")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(new_manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
