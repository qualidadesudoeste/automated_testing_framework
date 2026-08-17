"""Contrato compartilhado do manifesto de cobertura da auditoria."""

from __future__ import annotations

ROLES = [
    "system-mapper", "crud-lifecycle", "interactive-ui", "roles-access",
    "state-machines", "data-integrity", "validation-layers", "critical-journeys",
    "search-reporting", "audit-privacy", "edge-reliability",
    "semantics-accessibility", "consolidator",
]

SUITES = [
    "api", "openapi", "business_rules", "web_quality", "browser",
    "project_quality", "external_tools", "performance", "security",
]

DIMENSIONS = [f"D{index:02d}" for index in range(1, 26)]
ADVERSARIAL = [f"ADV{index:02d}" for index in range(1, 25)]

DELIVERABLES = [
    "EXECUTIVE_REPORT.md", "FINDINGS.json", "FINDINGS.csv",
    "TEST_CASES.feature", "TRACEABILITY.csv", "MESSAGE_CATALOG.csv",
    "ACTION_PLAN.md", "PENDING.md", "SYSTEM_MAP.md",
]

FINAL_STATUSES = {"complete", "blocked", "not_applicable"}


def blank_item() -> dict[str, object]:
    return {"status": "pending", "evidence": [], "reason": ""}


def new_manifest() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "audit": {
            "system": "", "scope": "", "environment": "",
            "started_at": "", "finished_at": "", "authorized_active_tests": False,
            "assumptions": [],
        },
        "roles": {name: blank_item() for name in ROLES},
        "suites": {name: blank_item() for name in SUITES},
        "dimensions": {name: blank_item() for name in DIMENSIONS},
        "adversarial_tests": {name: blank_item() for name in ADVERSARIAL},
        "deliverables": {name: blank_item() for name in DELIVERABLES},
    }
