"""Auditoria estática de UI, UX e acessibilidade em HTML."""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Any
import requests

from ..http import assert_same_origin_response, create_session, target_url
from ..models import Finding, SuiteResult


class PageAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.has_title = False
        self.has_viewport = False
        self.images_without_alt = 0
        self.controls_without_name = 0
        self.inputs: list[dict[str, str]] = []
        self.label_targets: set[str] = set()
        self.labels: dict[str, str] = {}
        self._current_label = ""
        self._label_text: list[str] = []
        self.required_ids: set[str] = set()
        self.boolean_ids: set[str] = set()
        self.boolean_cells = 0
        self._in_cell = False
        self._cell_text: list[str] = []
        self.headings: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.lang = data.get("lang", "")
        elif tag == "title":
            self.has_title = True
        elif tag == "meta" and data.get("name", "").lower() == "viewport":
            self.has_viewport = True
        elif tag == "img" and "alt" not in data:
            self.images_without_alt += 1
        elif tag == "label" and data.get("for"):
            self.label_targets.add(data["for"])
            self._current_label = data["for"]
            self._label_text = []
        elif tag == "input" and data.get("type", "text") not in {"hidden", "submit", "button"}:
            self.inputs.append(data)
            if "required" in data or data.get("aria-required") == "true":
                self.required_ids.add(data.get("id", ""))
            if data.get("type") in {"checkbox", "radio"}:
                self.boolean_ids.add(data.get("id", ""))
        elif tag in {"button", "a"}:
            if not any(data.get(name) for name in ("aria-label", "title")) and tag == "a" and not data.get("href"):
                self.controls_without_name += 1
        elif len(tag) == 2 and tag.startswith("h") and tag[1].isdigit():
            self.headings.append(int(tag[1]))
        elif tag in {"td", "th"}:
            self._in_cell = True
            self._cell_text = []

    def handle_data(self, data: str) -> None:
        if self._current_label:
            self._label_text.append(data)
        if self._in_cell:
            self._cell_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self._current_label:
            self.labels[self._current_label] = " ".join(self._label_text).strip()
            self._current_label = ""
            self._label_text = []
        elif tag in {"td", "th"} and self._in_cell:
            if " ".join(self._cell_text).strip() in {"S", "N"}:
                self.boolean_cells += 1
            self._in_cell = False
            self._cell_text = []


class WebQualityTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.web_config = config.get("web_quality", {})
        self.timeout = config.get("general", {}).get("timeout", 15)
        self.session = create_session(config)

    def run(self) -> SuiteResult:
        result = SuiteResult("web_quality")
        endpoints = self.web_config.get("pages", self.config["target"].get("web_endpoints", []))
        if not endpoints:
            result.skipped_reason = "Nenhuma página web configurada"
            return result.finish()
        for endpoint in endpoints:
            self._audit(str(endpoint), result)
        result.metrics["pages_tested"] = len(endpoints)
        return result.finish()

    def _audit(self, endpoint: str, result: SuiteResult) -> None:
        try:
            url = target_url(self.config["target"]["base_url"], endpoint)
        except ValueError as exc:
            result.findings.append(Finding("framework", "Página fora do alvo autorizado", str(exc), "high", "high"))
            return
        try:
            response = self.session.get(url, timeout=self.timeout)
            assert_same_origin_response(self.config["target"]["base_url"], response)
            response.raise_for_status()
        except requests.RequestException as exc:
            result.findings.append(Finding("ui", f"Página inacessível: {endpoint}", "A página não pôde ser auditada.", "high", "high", location=url, observed=str(exc)))
            return
        except ValueError as exc:
            result.findings.append(Finding("framework", f"Redirecionamento cross-origin não autorizado em {endpoint}", "A resposta saiu da origem autorizada durante um redirecionamento.", "high", "high", location=url, observed=str(exc)))
            return
        parser = PageAuditParser()
        parser.feed(response.text)
        checks = [
            (not parser.has_title, "ui", "Página sem título", "Adicionar um elemento <title> descritivo.", "medium", "WCAG 2.4.2"),
            (not parser.lang, "accessibility", "Idioma da página não definido", "Definir o atributo lang no elemento <html>.", "medium", "WCAG 3.1.1"),
            (not parser.has_viewport, "ui-responsive", "Viewport responsivo ausente", "Adicionar meta viewport para dispositivos móveis.", "medium", "Responsive Design"),
            (parser.images_without_alt > 0, "accessibility", "Imagens sem atributo alt", f"Adicionar texto alternativo às {parser.images_without_alt} imagens identificadas.", "high", "WCAG 1.1.1"),
        ]
        unlabeled = [item for item in parser.inputs if not item.get("aria-label") and not item.get("title") and item.get("id") not in parser.label_targets]
        checks.append((bool(unlabeled), "accessibility", "Campos de formulário sem rótulo", f"Associar labels aos {len(unlabeled)} campos identificados.", "high", "WCAG 3.3.2"))
        heading_jump = any(current - previous > 1 for previous, current in zip(parser.headings, parser.headings[1:]))
        checks.append((heading_jump, "ux-structure", "Hierarquia de títulos inconsistente", "Evitar saltos de nível na hierarquia de headings.", "low", "WCAG 1.3.1"))
        h1_count = parser.headings.count(1)
        checks.append((h1_count == 0, "ux-structure", "Página sem H1", "Adicionar um único <h1> descritivo por página.", "medium", "WCAG 1.3.1"))
        checks.append((h1_count > 1, "ux-structure", "Página com múltiplos H1", "Manter apenas um <h1> por página; usar <h2>+ para subseções.", "low", "WCAG 1.3.1"))
        required_without_indicator = [field_id for field_id in parser.required_ids if field_id and "*" not in parser.labels.get(field_id, "")]
        checks.append((bool(required_without_indicator), "ux-form", "Campos obrigatórios sem indicação visual", f"Indicar visualmente os {len(required_without_indicator)} campos obrigatórios, sem depender apenas do asterisco para acessibilidade.", "low", "WCAG 3.3.2"))
        boolean_questions = [field_id for field_id in parser.boolean_ids if "?" in parser.labels.get(field_id, "")]
        checks.append((bool(boolean_questions), "ux-copy", "Rótulo booleano utiliza interrogação", "Usar uma afirmação clara no rótulo de checkbox ou switch.", "low", "Design system"))
        checks.append((parser.boolean_cells > 0, "ux-copy", "Booleanos exibidos como S/N", f"Foram encontradas {parser.boolean_cells} células com S ou N; preferir Sim/Não quando a especificação exigir.", "info", "Content guideline"))
        for failed, category, title, recommendation, severity, reference in checks:
            if failed:
                result.findings.append(Finding(
                    category=category,
                    title=title,
                    description="A auditoria estrutural do HTML encontrou uma não conformidade.",
                    severity=severity,
                    confidence="high",
                    location=url,
                    recommendation=recommendation,
                    reference=reference,
                ))
