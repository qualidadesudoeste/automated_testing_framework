"""Contrato compartilhado das execuções multiagente."""

from __future__ import annotations

SPECIALISTS = [
    "qa-system-mapper", "qa-business", "qa-functional", "qa-api",
    "qa-interface", "qa-ui-ux", "qa-accessibility", "qa-performance",
    "qa-security", "qa-privacy-lgpd", "qa-code-quality", "qa-integrations",
]

CONSOLIDATOR = "qa-consolidator"
ALL_AGENTS = [*SPECIALISTS, CONSOLIDATOR]

SUITES = [
    "api", "openapi", "business_rules", "web_quality", "browser",
    "project_quality", "external_tools", "performance", "security",
    "access_control",
]

DIMENSIONS = [f"D{index:02d}" for index in range(1, 26)]
ADVERSARIAL = [f"ADV{index:02d}" for index in range(1, 25)]
SUITE_COVERAGE = [f"SUITE:{name}" for name in SUITES]
PROVENANCE_COVERAGE = ["SOURCE:AI-PROVENANCE"]
REQUIRED_COVERAGE = [*DIMENSIONS, *ADVERSARIAL, *SUITE_COVERAGE, *PROVENANCE_COVERAGE]
SOURCE_REQUIREMENTS = [
    *[f"SRC:MASTER:{index}" for index in range(10)],
    *[f"SRC:BUSINESS:{index}" for index in range(10)],
]
REQUIRED_COVERAGE.extend(SOURCE_REQUIREMENTS)

DELIVERABLES = [
    "EXECUTIVE_REPORT.md", "FINDINGS.json", "FINDINGS.csv",
    "TEST_CASES.feature", "TRACEABILITY.csv", "MESSAGE_CATALOG.csv",
    "ACTION_PLAN.md", "PENDING.md", "PENDENCIAS.md", "SYSTEM_MAP.md",
    "AUDITORIA_NEGOCIO.md", "ACHADOS_NEGOCIO.csv", "PENDENCIAS_NEGOCIO.md",
    "MAPA_SISTEMA.md", "audit-manifest.json",
]

ALLOWED_COVERAGE_STATUS = {"complete", "blocked", "not_applicable"}
