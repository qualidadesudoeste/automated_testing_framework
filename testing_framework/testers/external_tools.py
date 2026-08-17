"""Adaptadores allowlisted para ferramentas especializadas."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..models import Finding, SuiteResult


ALLOWED_TOOLS = {"semgrep", "gitleaks", "trivy", "lighthouse", "k6", "zap"}


class ExternalToolsTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.tool_config = config.get("external_tools", {})
        self.timeout = int(self.tool_config.get("timeout", 600))
        config_path = Path(config.get("_config_path", ".")).resolve()
        project_raw = Path(str(self.tool_config.get("project_root", config_path.parent.parent)))
        self.project_root = (config_path.parent / project_raw).resolve() if not project_raw.is_absolute() else project_raw.resolve()
        evidence_raw = Path(str(self.tool_config.get("evidence_dir", "reports/tools")))
        self.evidence_dir = (self.project_root / evidence_raw).resolve() if not evidence_raw.is_absolute() else evidence_raw.resolve()

    def run(self) -> SuiteResult:
        result = SuiteResult("external_tools")
        requested = self.tool_config.get("tools", [])
        if not requested:
            result.skipped_reason = "Nenhuma ferramenta externa configurada"
            return result.finish()
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        executed = 0
        unavailable = []
        for raw in requested:
            spec = {"name": raw} if isinstance(raw, str) else raw
            name = str(spec.get("name", "")).lower()
            if name not in ALLOWED_TOOLS:
                result.findings.append(Finding("framework", f"Ferramenta não permitida: {name}", "Somente adaptadores allowlisted podem ser executados.", "high", "high"))
                continue
            executable = shutil.which("zap-baseline.py" if name == "zap" else name)
            if not executable:
                unavailable.append(name)
                continue
            try:
                command, evidence = self._command(name, executable, spec)
            except ValueError as exc:
                result.findings.append(Finding("framework", f"Configuração inválida para {name}", str(exc), "high", "high"))
                continue
            executed += 1
            self._execute(name, command, evidence, result)
        result.metrics.update({"executed": executed, "unavailable": unavailable, "requested": len(requested)})
        if executed == 0 and not result.findings:
            result.skipped_reason = f"Ferramentas não instaladas: {', '.join(unavailable)}"
        return result.finish()

    def _command(self, name: str, executable: str, spec: dict[str, Any]) -> tuple[list[str], Path]:
        evidence = self.evidence_dir / f"{name}.json"
        target = self.config["target"]["base_url"]
        if name == "semgrep":
            return [executable, "scan", "--config", str(spec.get("config", "auto")), "--json", "--output", str(evidence), str(self.project_root)], evidence
        if name == "gitleaks":
            return [executable, "detect", "--source", str(self.project_root), "--report-format", "json", "--report-path", str(evidence), "--no-banner"], evidence
        if name == "trivy":
            return [executable, "fs", "--format", "json", "--output", str(evidence), str(self.project_root)], evidence
        if name == "lighthouse":
            return [executable, target, "--quiet", "--output=json", f"--output-path={evidence}", "--chrome-flags=--headless"], evidence
        if name == "k6":
            script = self._project_file(spec.get("script"), "k6.script")
            return [executable, "run", "--summary-export", str(evidence), str(script)], evidence
        return [executable, "-t", target, "-J", str(evidence)], evidence

    def _project_file(self, raw: Any, field: str) -> Path:
        if not raw:
            raise ValueError(f"{field} é obrigatório")
        path = (self.project_root / str(raw)).resolve()
        try:
            path.relative_to(self.project_root)
        except ValueError as exc:
            raise ValueError(f"{field} deve permanecer dentro do projeto") from exc
        if not path.is_file():
            raise ValueError(f"Arquivo não encontrado: {path}")
        return path

    def _execute(self, name: str, command: list[str], evidence: Path, result: SuiteResult) -> None:
        try:
            completed = subprocess.run(command, cwd=self.project_root, capture_output=True, text=True, timeout=self.timeout, shell=False)
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            result.findings.append(Finding("tooling", f"Falha ao executar {name}", "A integração externa não foi concluída.", "high", "high", observed=str(exc)))
            return
        result.evidence.append(str(evidence))
        count = count_findings(evidence)
        if completed.returncode != 0 or count:
            result.findings.append(Finding(
                category="security" if name in {"semgrep", "gitleaks", "trivy", "zap"} else "performance",
                title=f"{name} encontrou problemas" if count else f"{name} terminou com erro",
                description=f"A ferramenta reportou {count} itens." if count else "A ferramenta retornou código diferente de zero.",
                severity="high" if name in {"gitleaks", "zap"} else "medium",
                confidence="medium",
                status="suspected",
                evidence=str(evidence) if evidence.exists() else (completed.stderr or completed.stdout)[-2000:],
                recommendation="Revisar o relatório nativo, confirmar os achados e criar testes de regressão.",
            ))


def count_findings(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for key in ("results", "Results", "vulnerabilities", "alerts"):
            value = data.get(key)
            if isinstance(value, list):
                return len(value)
    return 0
