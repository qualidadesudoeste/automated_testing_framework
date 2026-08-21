"""Auditoria estática de documentação, modularidade, testes e contratos."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from ..models import Finding, SuiteResult
from ..source_provenance import scan_source_provenance


IGNORED = {".git", ".venv", "venv", "node_modules", "build", "dist", "reports", "__pycache__", ".runtime"}


class ProjectQualityTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.quality_config = config.get("project_quality", {})
        config_path = Path(config.get("_config_path", ".")).resolve()
        raw = Path(str(self.quality_config.get("project_root", config_path.parent)))
        self.root = (config_path.parent / raw).resolve() if not raw.is_absolute() else raw.resolve()

    def run(self) -> SuiteResult:
        result = SuiteResult("project_quality")
        if not self.root.is_dir():
            result.findings.append(Finding("maintainability", "Projeto não encontrado", "Não foi possível executar a auditoria estática.", "high", "high", location=str(self.root)))
            return result.finish()
        files = [item for item in self.root.rglob("*") if item.is_file() and not IGNORED.intersection(item.relative_to(self.root).parts)]
        python_files = [item for item in files if item.suffix == ".py"]
        test_files = [item for item in files if item.name.startswith("test_") or any(part.lower() in {"test", "tests", "spec", "specs"} for part in item.relative_to(self.root).parts)]
        max_lines = int(self.quality_config.get("max_file_lines", 600))
        long_files = []
        public_items = documented_items = 0
        syntax_errors = []
        for path in python_files:
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = text.count("\n") + 1
            if lines > max_lines:
                long_files.append((path, lines))
            try:
                tree = ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                syntax_errors.append((path, exc.lineno))
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
                    public_items += 1
                    documented_items += bool(ast.get_docstring(node))
        for path, line in syntax_errors:
            result.findings.append(Finding("code-quality", "Erro de sintaxe", "O arquivo não pôde ser analisado.", "high", "high", location=f"{path}:{line}"))
        for path, lines in long_files:
            result.findings.append(Finding("maintainability", "Arquivo excessivamente longo", "O arquivo ultrapassa o limite de modularidade configurado.", "medium", "high", location=str(path), expected=f"<= {max_lines} linhas", observed=f"{lines} linhas", recommendation="Separar responsabilidades e preservar coesão."))
        if not test_files:
            result.findings.append(Finding("test-coverage", "Testes automatizados não encontrados", "O projeto não possui arquivos de teste detectáveis.", "high", "high", location=str(self.root)))
        documentation_ratio = documented_items / public_items if public_items else 1.0
        minimum_docs = float(self.quality_config.get("min_documented_ratio", 0.5))
        if documentation_ratio < minimum_docs:
            result.findings.append(Finding("maintainability", "Documentação de código insuficiente", "Poucos símbolos públicos possuem docstrings.", "medium", "medium", expected=f">= {minimum_docs:.0%}", observed=f"{documentation_ratio:.0%}"))
        openapi_files = [item for item in files if item.name.lower() in {"openapi.yaml", "openapi.yml", "openapi.json", "swagger.yaml", "swagger.json"}]
        if self.quality_config.get("require_openapi") and not openapi_files:
            result.findings.append(Finding("api-governance", "Documentação OpenAPI ausente", "O projeto exige contrato de API versionado.", "high", "high", location=str(self.root)))
        coverage_markers = [item for item in files if item.name in {".coveragerc", "coverage.xml", "pyproject.toml", "jest.config.js", "vitest.config.ts"}]
        if self.quality_config.get("require_coverage") and not coverage_markers:
            result.findings.append(Finding("test-coverage", "Configuração de cobertura ausente", "Não foi localizado indicador de medição de cobertura.", "medium", "medium", location=str(self.root)))
        for required in self.quality_config.get("required_files", []):
            if not (self.root / str(required)).exists():
                result.findings.append(Finding("governance", f"Artefato obrigatório ausente: {required}", "Um documento ou contrato exigido não foi encontrado.", "medium", "high", location=str(self.root / str(required))))
        provenance_signals = []
        provenance_files_scanned = 0
        if self.quality_config.get("detect_ai_authorship", True):
            provenance_signals, provenance_files_scanned = scan_source_provenance(
                self.root,
                files,
                exclude=self.quality_config.get("ai_authorship_exclude", []),
                allowlist=self.quality_config.get("ai_authorship_allowlist", []),
                max_file_bytes=int(self.quality_config.get("ai_authorship_max_file_bytes", 1_000_000)),
                max_signals=int(self.quality_config.get("ai_authorship_max_findings", 100)),
            )
            severity = str(self.quality_config.get("ai_authorship_severity", "low")).lower()
            for signal in provenance_signals:
                relative = signal.path.relative_to(self.root)
                result.findings.append(Finding(
                    "source-provenance",
                    "Indício de autoria automatizada no código-fonte",
                    "Foi encontrada uma assinatura textual ou um artefato associado a assistência automatizada. O indício não prova autoria e deve ser validado no contexto do projeto.",
                    severity,
                    signal.confidence,
                    status="suspected",
                    location=f"{relative}:{signal.line}",
                    observed=signal.kind,
                    evidence=signal.excerpt,
                    recommendation="Revisar a origem do trecho e remover, justificar ou autorizar o indício conforme a política do projeto.",
                    requirement_id="SOURCE-AUTHORSHIP-001",
                ))
        result.metrics.update({
            "files": len(files), "python_files": len(python_files), "test_files": len(test_files),
            "public_symbols": public_items, "documented_ratio": documentation_ratio,
            "openapi_files": [str(item) for item in openapi_files],
            "provenance_files_scanned": provenance_files_scanned,
            "provenance_signals": len(provenance_signals),
        })
        return result.finish()
