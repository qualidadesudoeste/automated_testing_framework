#!/usr/bin/env python3
"""Impede consolidação ou encerramento com agentes ausentes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_contract import ALLOWED_COVERAGE_STATUS, ALL_AGENTS, CONSOLIDATOR, DELIVERABLES, REQUIRED_COVERAGE, SPECIALISTS


def validate_agent(path: Path, expected: str) -> list[str]:
    if not path.is_file():
        return [f"resultado ausente: {path.name}"]
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"resultado inválido {path.name}: {exc}"]
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{path.name}: objeto JSON esperado"]
    if data.get("agent") != expected:
        errors.append(f"{path.name}: agent deve ser {expected}")
    if data.get("status") != "complete":
        errors.append(f"{path.name}: agente deve concluir com status complete")
    if not str(data.get("summary", "")).strip():
        errors.append(f"{path.name}: summary obrigatório")
    if not isinstance(data.get("coverage"), list) or not data["coverage"]:
        errors.append(f"{path.name}: coverage não pode ser vazio")
    else:
        for index, item in enumerate(data["coverage"]):
            label = f"{path.name}: coverage[{index}]"
            if not isinstance(item, dict) or not str(item.get("id", "")).strip():
                errors.append(f"{label}: id obrigatório")
                continue
            status = item.get("status")
            if status not in ALLOWED_COVERAGE_STATUS:
                errors.append(f"{label}: status inválido")
            elif status == "complete" and not item.get("evidence"):
                errors.append(f"{label}: complete exige evidence")
            elif status in {"blocked", "not_applicable"} and not str(item.get("reason", "")).strip():
                errors.append(f"{label}: {status} exige reason")
    if not isinstance(data.get("findings"), list):
        errors.append(f"{path.name}: findings deve ser uma lista")
    if not isinstance(data.get("artifacts"), list):
        errors.append(f"{path.name}: artifacts deve ser uma lista")
    return errors


def validate_run(root: Path, final: bool) -> list[str]:
    required_agents = ALL_AGENTS if final else SPECIALISTS
    errors: list[str] = []
    manifest_path = root / "run-manifest.json"
    if not manifest_path.is_file():
        errors.append("run-manifest.json ausente")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("surface_mode") not in {"auto", "A", "B", "C", "D"}:
                errors.append("surface_mode inválido no manifesto")
            if manifest.get("depth_mode") not in {"rapido", "padrao", "profundo"}:
                errors.append("depth_mode inválido no manifesto")
            controls = manifest.get("controls", {})
            expected_controls = {"max_file_reads_per_pass": 40, "max_priority_findings_per_agent": 12, "critical_maturity_gate": 30}
            if any(controls.get(key) != value for key, value in expected_controls.items()):
                errors.append("controles de custo/maturidade ausentes ou alterados")
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"run-manifest.json inválido: {exc}")
    for agent in required_agents:
        errors.extend(validate_agent(root / "agents" / f"{agent}.json", agent))
    observed: set[str] = set()
    for agent in SPECIALISTS:
        path = root / "agents" / f"{agent}.json"
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            observed.update(str(item.get("id")) for item in data.get("coverage", []) if isinstance(item, dict))
        except (OSError, json.JSONDecodeError, AttributeError):
            continue
    missing = [item for item in REQUIRED_COVERAGE if item not in observed]
    if missing:
        errors.append(f"cobertura obrigatória ausente: {', '.join(missing)}")
    if not (root / "SYSTEM_MAP.md").is_file():
        errors.append("SYSTEM_MAP.md ausente")
    if final:
        for name in DELIVERABLES:
            path = root / name
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"entregável ausente ou vazio: {name}")
    elif (root / "agents" / f"{CONSOLIDATOR}.json").exists():
        errors.append("consolidador executado antes da verificação dos especialistas")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar execução multiagente do QA Mestre")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    errors = validate_run(args.run_dir.resolve(), args.final)
    if errors:
        print(f"Execução incompleta: {len(errors)} problema(s)")
        for error in errors:
            print(f"- {error}")
        return 2
    print("Execução multiagente completa." if args.final else "Especialistas concluídos; consolidação liberada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
