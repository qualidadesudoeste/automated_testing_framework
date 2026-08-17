#!/usr/bin/env python3
"""Valida que nenhum papel, suíte ou critério foi omitido silenciosamente."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_manifest import ADVERSARIAL, DELIVERABLES, DIMENSIONS, FINAL_STATUSES, ROLES, SUITES


def validate_group(data: dict[str, Any], group: str, required: list[str], require_complete: bool = False) -> list[str]:
    errors: list[str] = []
    values = data.get(group)
    if not isinstance(values, dict):
        return [f"{group}: grupo ausente ou inválido"]

    for name in required:
        item = values.get(name)
        prefix = f"{group}.{name}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: item ausente")
            continue
        status = item.get("status")
        evidence = item.get("evidence")
        reason = str(item.get("reason", "")).strip()
        if require_complete and status != "complete":
            errors.append(f"{prefix}: deve ser complete")
        elif status not in FINAL_STATUSES:
            errors.append(f"{prefix}: status deve ser complete, blocked ou not_applicable")
        elif status == "complete" and (not isinstance(evidence, list) or not evidence):
            errors.append(f"{prefix}: execução completa exige evidência")
        elif status in {"blocked", "not_applicable"} and not reason:
            errors.append(f"{prefix}: {status} exige justificativa")

    extras = sorted(set(values) - set(required))
    if extras:
        errors.append(f"{group}: itens desconhecidos: {', '.join(extras)}")
    return errors


def validate_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        errors.append("schema_version: esperado 1.0")
    audit = data.get("audit")
    if not isinstance(audit, dict):
        errors.append("audit: metadados ausentes")
    else:
        for field in ("system", "scope", "environment", "started_at", "finished_at"):
            if not str(audit.get(field, "")).strip():
                errors.append(f"audit.{field}: obrigatório")
    errors.extend(validate_group(data, "roles", ROLES, require_complete=True))
    errors.extend(validate_group(data, "suites", SUITES))
    errors.extend(validate_group(data, "dimensions", DIMENSIONS))
    errors.extend(validate_group(data, "adversarial_tests", ADVERSARIAL))
    errors.extend(validate_group(data, "deliverables", DELIVERABLES, require_complete=True))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar cobertura da auditoria QA Mestre")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Manifesto inválido: {exc}")
        return 1
    errors = validate_manifest(data)
    if errors:
        print(f"Auditoria incompleta: {len(errors)} pendência(s)")
        for error in errors:
            print(f"- {error}")
        return 2
    print("Auditoria completa: contrato de cobertura atendido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
