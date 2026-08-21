"""Modelos normalizados compartilhados por todas as suítes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
import re


SEVERITY_ORDER = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
REDACTION_PATTERNS = [
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)([\"']?(?:password|passwd|token|api[_-]?key|secret)[\"']?\s*[:=]\s*[\"']?)[^\"'\s,;}]+"),
    re.compile(r"(?i)(set-cookie\s*:\s*)[^\r\n]+"),
    # Pares usuário/senha citados em prosa (ex.: achados de credenciais fracas do próprio framework).
    re.compile(r"(?i)((?:credencia(?:l|is)|login\s+bem-sucedido)[^:=\n]{0,30}(?:com|:)\s*)([^\s,;]+/[^\s,;]+)"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_text(value: str) -> str:
    result = value
    for pattern in REDACTION_PATTERNS:
        result = pattern.sub(r"\1[REDACTED]", result)
    return result


def redact_data(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {key: redact_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_data(item) for item in value)
    return value


@dataclass
class Finding:
    category: str
    title: str
    description: str
    severity: str = "medium"
    confidence: str = "medium"
    status: str = "confirmed"
    location: str = ""
    expected: str = ""
    observed: str = ""
    evidence: str = ""
    recommendation: str = ""
    reference: str = ""
    requirement_id: str = ""
    reproduction: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.severity = self.severity.lower()
        if self.severity not in SEVERITY_ORDER:
            raise ValueError(f"Severidade inválida: {self.severity}")
        if self.confidence not in {"low", "medium", "high"}:
            raise ValueError(f"Confiança inválida: {self.confidence}")
        if self.status not in {"confirmed", "suspected", "accepted", "resolved"}:
            raise ValueError(f"Status inválido: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return redact_data(asdict(self))


@dataclass
class SuiteResult:
    name: str
    status: str = "passed"
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    skipped_reason: str = ""
    started_at: str = field(default_factory=utc_now)
    finished_at: str = ""

    def finish(self) -> "SuiteResult":
        self.finished_at = utc_now()
        if self.skipped_reason:
            self.status = "skipped"
        elif any(f.severity in {"critical", "high"} for f in self.findings):
            self.status = "failed"
        return self

    def to_dict(self) -> dict[str, Any]:
        data = redact_data(asdict(self))
        data["findings"] = [item.to_dict() for item in self.findings]
        return data


@dataclass
class FrameworkReport:
    target: dict[str, Any]
    suites: list[SuiteResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: str = field(default_factory=utc_now)
    finished_at: str = ""
    quality_gate: dict[str, Any] = field(default_factory=dict)

    @property
    def findings(self) -> list[Finding]:
        return [finding for suite in self.suites for finding in suite.findings]

    def finish(self) -> "FrameworkReport":
        self.finished_at = utc_now()
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": redact_data(self.target),
            "metadata": redact_data(self.metadata),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "quality_gate": self.quality_gate,
            "summary": {
                "suites": len(self.suites),
                "findings": len(self.findings),
                "by_severity": {
                    severity: sum(1 for item in self.findings if item.severity == severity)
                    for severity in SEVERITY_ORDER
                },
            },
            "suites": [suite.to_dict() for suite in self.suites],
        }
