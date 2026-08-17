#!/usr/bin/env python3
"""Inicializa diretórios e manifesto de uma execução QA multiagente."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from run_contract import ALL_AGENTS, SUITES


def main() -> int:
    parser = argparse.ArgumentParser(description="Inicializar execução do QA Mestre")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--surface", choices=["auto", "A", "B", "C", "D"], default="auto")
    parser.add_argument("--depth", choices=["rapido", "padrao", "profundo"], default="profundo")
    args = parser.parse_args()
    root = args.run_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    for directory in ("agents", "evidence", "framework"):
        (root / directory).mkdir(exist_ok=True)
    manifest = root / "run-manifest.json"
    if manifest.exists():
        parser.error(f"execução já inicializada: {manifest}")
    data = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "surface_mode": args.surface,
        "depth_mode": args.depth,
        "controls": {"max_file_reads_per_pass": 40, "max_priority_findings_per_agent": 12, "critical_maturity_gate": 30},
        "agents": {name: "pending" for name in ALL_AGENTS},
        "suites": {name: "pending" for name in SUITES},
    }
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
