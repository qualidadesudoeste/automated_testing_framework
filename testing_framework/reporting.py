"""Relatórios unificados em JSON, HTML, JUnit XML, SARIF e texto."""

from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .models import FrameworkReport, redact_text


class UnifiedReporter:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, report: FrameworkReport, formats: list[str]) -> list[str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files = []
        for output_format in formats:
            path = self.output_dir / f"report_{timestamp}.{self._extension(output_format)}"
            content = getattr(self, f"_{output_format}")(report)
            path.write_text(content, encoding="utf-8")
            files.append(str(path.resolve()))
        return files

    @staticmethod
    def _extension(output_format: str) -> str:
        return {"junit": "xml", "text": "txt"}.get(output_format, output_format)

    @staticmethod
    def _json(report: FrameworkReport) -> str:
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

    @staticmethod
    def _text(report: FrameworkReport) -> str:
        data = report.to_dict()
        lines = [
            "RELATÓRIO DE QUALIDADE DE SOFTWARE",
            f"Alvo: {data['target'].get('name', data['target'].get('base_url', 'N/A'))}",
            f"Quality gate: {'APROVADO' if data['quality_gate'].get('passed') else 'REPROVADO'}",
            f"Achados: {data['summary']['findings']}",
        ]
        for suite in report.suites:
            lines.append(f"\n[{suite.name}] {suite.status} - {len(suite.findings)} achados")
            lines.extend(f"- {item.severity.upper()}: {item.title}" for item in suite.findings)
        return "\n".join(lines) + "\n"

    @staticmethod
    def _html(report: FrameworkReport) -> str:
        data = report.to_dict()
        cards = []
        for finding in report.findings:
            cards.append(
                f'<article class="finding {escape(finding.severity)}">'
                f'<span>{escape(finding.severity.upper())}</span>'
                f'<h3>{escape(redact_text(finding.title))}</h3>'
                f'<p>{escape(redact_text(finding.description))}</p>'
                f'<dl><dt>Local</dt><dd>{escape(redact_text(finding.location or "N/A"))}</dd>'
                f'<dt>Evidência</dt><dd>{escape(redact_text(finding.evidence or finding.observed or "N/A"))}</dd>'
                f'<dt>Recomendação</dt><dd>{escape(redact_text(finding.recommendation or "N/A"))}</dd></dl></article>'
            )
        return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Relatório de testes</title>
<style>body{{font:16px system-ui;margin:0;background:#f6f7fb;color:#172033}}main{{max-width:1100px;margin:auto;padding:32px}}header,.finding{{background:white;padding:24px;border-radius:12px;margin-bottom:16px;box-shadow:0 2px 10px #0001}}.finding{{border-left:6px solid #64748b}}.critical{{border-color:#991b1b}}.high{{border-color:#dc2626}}.medium{{border-color:#d97706}}.low{{border-color:#2563eb}}dt{{font-weight:700;margin-top:8px}}dd{{margin-left:0;white-space:pre-wrap}}.passed{{color:#15803d}}.failed{{color:#b91c1c}}</style></head>
<body><main><header><h1>Relatório de qualidade de software</h1><p>Alvo: {escape(str(data['target'].get('name', 'N/A')))}</p>
<p class="{'passed' if data['quality_gate'].get('passed') else 'failed'}">Quality gate: {'APROVADO' if data['quality_gate'].get('passed') else 'REPROVADO'}</p>
<p>{data['summary']['findings']} achados em {data['summary']['suites']} suítes</p></header>{''.join(cards) or '<p>Nenhum achado.</p>'}</main></body></html>"""

    @staticmethod
    def _junit(report: FrameworkReport) -> str:
        root = ET.Element("testsuites")
        for suite in report.suites:
            node = ET.SubElement(root, "testsuite", name=suite.name, tests=str(max(1, len(suite.findings))), failures=str(len(suite.findings)))
            if not suite.findings:
                ET.SubElement(node, "testcase", name=f"{suite.name}-quality-gate")
            for finding in suite.findings:
                case = ET.SubElement(node, "testcase", name=finding.title, classname=suite.name)
                failure = ET.SubElement(case, "failure", type=finding.severity, message=finding.description)
                failure.text = finding.evidence or finding.observed
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def _sarif(report: FrameworkReport) -> str:
        level = {"critical": "error", "high": "error", "medium": "warning", "low": "note", "info": "note"}
        results: list[dict[str, Any]] = []
        for finding in report.findings:
            item: dict[str, Any] = {
                "ruleId": finding.reference or finding.category,
                "level": level[finding.severity],
                "message": {"text": f"{finding.title}: {finding.description}"},
                "properties": {"confidence": finding.confidence, "status": finding.status},
            }
            if finding.location:
                item["locations"] = [{"physicalLocation": {"artifactLocation": {"uri": finding.location}}}]
            results.append(item)
        sarif = {"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json", "runs": [{"tool": {"driver": {"name": "automated-testing-framework"}}, "results": results}]}
        return json.dumps(sarif, ensure_ascii=False, indent=2)
