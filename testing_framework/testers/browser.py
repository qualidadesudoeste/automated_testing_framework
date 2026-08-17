"""Jornadas multi-browser, axe local, traces e regressão visual."""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from ..http import target_url
from ..models import Finding, SuiteResult
from ..validators import profile_cases


class BrowserTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.browser_config = config.get("browser", {})
        self.evidence_dir = Path(self.browser_config.get("evidence_dir", "reports/evidence")).resolve()

    def run(self) -> SuiteResult:
        result = SuiteResult("browser")
        journeys = self.browser_config.get("journeys", [])
        if not journeys:
            result.skipped_reason = "Nenhuma jornada de navegador configurada"
            return result.finish()
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            result.skipped_reason = "Playwright não instalado; instale o extra browser"
            return result.finish()

        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        engines = self.browser_config.get("engines", ["chromium"])
        with sync_playwright() as playwright:
            for engine in engines:
                if engine not in {"chromium", "firefox", "webkit"}:
                    result.findings.append(Finding("framework", f"Engine inválido: {engine}", "Use chromium, firefox ou webkit.", "high", "high"))
                    continue
                self._run_engine(playwright, engine, journeys, result)
        result.metrics.update({"journeys_configured": len(journeys), "engines": engines})
        return result.finish()

    def _run_engine(self, playwright: Any, engine: str, journeys: list[dict[str, Any]], result: SuiteResult) -> None:
        browser = getattr(playwright, engine).launch(headless=self.browser_config.get("headless", True))
        context = browser.new_context(
            viewport=self.browser_config.get("viewport", {"width": 1440, "height": 900}),
            locale=self.browser_config.get("locale", "pt-BR"),
            timezone_id=self.browser_config.get("timezone_id", "America/Sao_Paulo"),
            storage_state=self.browser_config.get("storage_state"),
            ignore_https_errors=self.browser_config.get("ignore_https_errors", False),
        )
        tracing = bool(self.browser_config.get("trace", True))
        if tracing:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        try:
            for journey in journeys:
                page = context.new_page()
                self._run_journey(page, engine, journey, result)
                page.close()
        finally:
            if tracing:
                trace = self.evidence_dir / f"trace-{engine}.zip"
                context.tracing.stop(path=str(trace))
                result.evidence.append(str(trace))
            context.close()
            browser.close()

    def _run_journey(self, page: Any, engine: str, journey: dict[str, Any], result: SuiteResult) -> None:
        name = safe_name(str(journey.get("name", "journey")))
        console_errors: list[str] = []
        page_errors: list[str] = []
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        try:
            for index, action in enumerate(journey.get("steps", []), start=1):
                self._perform(page, engine, name, index, action, result)
            self._run_axe(page, engine, name, result)
            if self.browser_config.get("fail_on_console_error") and (console_errors or page_errors):
                raise AssertionError("; ".join((console_errors + page_errors)[:10]))
        except Exception as exc:
            path = self.evidence_dir / f"{name}-{engine}-failure.png"
            page.screenshot(path=str(path), full_page=True)
            result.evidence.append(str(path))
            result.findings.append(Finding(
                category="interface",
                title=f"Jornada falhou: {name} ({engine})",
                description="O fluxo real de navegador não atingiu o resultado esperado.",
                severity=str(journey.get("severity", "high")),
                confidence="high",
                location=page.url,
                observed=str(exc),
                evidence=str(path),
                reproduction=[str(step) for step in journey.get("steps", [])],
                metadata={"console_errors": console_errors, "page_errors": page_errors, "engine": engine},
            ))

    def _perform(self, page: Any, engine: str, name: str, index: int, action: dict[str, Any], result: SuiteResult) -> None:
        kind = action.get("action")
        locator = page.locator(action["selector"]) if action.get("selector") else None
        if kind == "goto":
            page.goto(target_url(self.config["target"]["base_url"], str(action.get("path", "/"))), wait_until=action.get("wait_until", "networkidle"))
        elif kind == "click":
            locator.click()
        elif kind == "fill":
            locator.fill(self._value(action.get("value", "")))
        elif kind == "select":
            locator.select_option(self._value(action.get("value", "")))
        elif kind == "check":
            locator.check()
        elif kind == "press":
            locator.press(str(action["key"]))
        elif kind == "wait_for":
            locator.wait_for(state=action.get("state", "visible"), timeout=action.get("timeout", 5000))
        elif kind == "check_text":
            actual = locator.inner_text()
            if self._value(action["value"]) not in actual:
                raise AssertionError(f"Texto esperado {action['value']!r}; obtido {actual!r}")
        elif kind == "expect_url":
            if not re.search(str(action["value"]), page.url):
                raise AssertionError(f"URL {page.url!r} não atende a {action['value']!r}")
        elif kind == "screenshot":
            self._capture_visual(page, engine, name, index, action, result)
        elif kind == "validate_field":
            self._validate_field(page, action)
        elif kind == "assert_required":
            required = locator.evaluate("element => element.required || element.getAttribute('aria-required') === 'true'")
            if not required:
                raise AssertionError("Campo não está marcado como obrigatório")
            if action.get("indicator_selector") and not page.locator(action["indicator_selector"]).is_visible():
                raise AssertionError("Indicador visual de obrigatoriedade ausente")
        elif kind == "assert_disabled":
            if not locator.is_disabled():
                raise AssertionError("Campo deveria estar desabilitado")
        elif kind == "assert_radio_exclusive":
            radios = page.locator(action["selector"])
            for radio_index in range(radios.count()):
                radios.nth(radio_index).check()
                checked = radios.evaluate_all("elements => elements.filter(item => item.checked).length")
                if checked != 1:
                    raise AssertionError(f"Grupo de rádio possui {checked} opções marcadas")
        elif kind == "assert_clear":
            for field in action.get("fields", []):
                page.locator(field["selector"]).fill(self._value(field.get("value", "teste")))
            page.locator(action["clear_selector"]).click()
            remaining = [field["selector"] for field in action.get("fields", []) if page.locator(field["selector"]).input_value()]
            if remaining:
                raise AssertionError(f"Campos não foram limpos: {remaining}")
        elif kind == "assert_sorted":
            values = [item.strip() for item in locator.all_inner_texts()]
            expected = sorted(values, key=str.casefold, reverse=action.get("direction", "asc") == "desc")
            if values != expected:
                raise AssertionError(f"Lista não está ordenada: {values[:20]}")
        elif kind == "assert_persistence":
            before = locator.input_value() if action.get("property", "value") == "value" else locator.inner_text()
            page.reload(wait_until="networkidle")
            refreshed = page.locator(action["selector"])
            after = refreshed.input_value() if action.get("property", "value") == "value" else refreshed.inner_text()
            if before != after:
                raise AssertionError(f"Valor não persistiu após reload: {before!r} != {after!r}")
        elif kind == "upload":
            upload_path = Path(self._value(action["path"])).resolve()
            if not upload_path.is_file():
                raise ValueError(f"Arquivo de upload não encontrado: {upload_path}")
            locator.set_input_files(str(upload_path))
        elif kind == "download":
            with page.expect_download() as download_info:
                locator.click()
            download = download_info.value
            target = self.evidence_dir / safe_name(download.suggested_filename)
            download.save_as(str(target))
            result.evidence.append(str(target))
        elif kind == "assert_confirmation":
            with page.expect_dialog() as dialog_info:
                locator.click()
            dialog = dialog_info.value
            expected = self._value(action.get("contains", ""))
            if expected and expected not in dialog.message:
                dialog.dismiss()
                raise AssertionError(f"Confirmação inesperada: {dialog.message!r}")
            dialog.dismiss()
        elif kind == "assert_tab_order":
            selectors = action.get("selectors", [])
            if not selectors:
                raise ValueError("assert_tab_order exige selectors")
            page.locator(selectors[0]).focus()
            for expected_selector in selectors[1:]:
                page.keyboard.press("Tab")
                matches = page.evaluate("selector => document.activeElement === document.querySelector(selector)", expected_selector)
                if not matches:
                    raise AssertionError(f"Ordem de TAB divergiu antes de {expected_selector}")
        elif kind == "assert_not_truncated":
            truncated = locator.evaluate("element => element.scrollWidth > element.clientWidth || element.scrollHeight > element.clientHeight")
            if truncated:
                raise AssertionError("Conteúdo está cortado ou truncado")
        elif kind == "measure_navigation":
            started = time.perf_counter()
            page.goto(target_url(self.config["target"]["base_url"], str(action.get("path", "/"))), wait_until=action.get("wait_until", "networkidle"))
            elapsed = (time.perf_counter() - started) * 1000
            maximum = float(action.get("max_ms", 2000))
            result.metrics.setdefault("browser_timings", []).append({"path": action.get("path", "/"), "elapsed_ms": elapsed, "engine": engine})
            if elapsed > maximum:
                raise AssertionError(f"Carregamento levou {elapsed:.2f}ms; máximo {maximum:.2f}ms")
        else:
            raise ValueError(f"Ação de navegador não suportada: {kind}")

    def _validate_field(self, page: Any, action: dict[str, Any]) -> None:
        locator = page.locator(action["selector"])
        cases = action.get("cases")
        if not cases and action.get("profile"):
            cases = profile_cases(str(action["profile"]))
        cases = cases or []
        for case in cases:
            value = self._value(case.get("value", ""))
            locator.fill(value)
            locator.press("Tab")
            native_valid = bool(locator.evaluate("element => typeof element.checkValidity === 'function' ? element.checkValidity() : true"))
            error_visible = bool(page.locator(case["error_selector"]).is_visible()) if case.get("error_selector") else False
            actual_valid = native_valid and not error_visible
            expected_valid = bool(case.get("valid", True))
            if actual_valid != expected_valid:
                raise AssertionError(f"Campo {action['selector']} aceitou/rejeitou incorretamente {value!r}")
            pattern = case.get("masked_pattern")
            if pattern and re.fullmatch(str(pattern), locator.input_value()) is None:
                raise AssertionError(f"Máscara incorreta para {value!r}: {locator.input_value()!r}")
        if action.get("max_length") is not None:
            actual_max = locator.get_attribute("maxlength")
            if actual_max != str(action["max_length"]):
                raise AssertionError(f"maxlength esperado {action['max_length']}; obtido {actual_max}")

    def _capture_visual(self, page: Any, engine: str, name: str, index: int, action: dict[str, Any], result: SuiteResult) -> None:
        actual = self.evidence_dir / f"{name}-{engine}-{index}.png"
        page.screenshot(path=str(actual), full_page=action.get("full_page", True))
        result.evidence.append(str(actual))
        baseline_raw = action.get("baseline")
        if not baseline_raw:
            return
        baseline = Path(str(baseline_raw)).resolve()
        if action.get("update_baseline", False):
            baseline.parent.mkdir(parents=True, exist_ok=True)
            baseline.write_bytes(actual.read_bytes())
            return
        if not baseline.is_file():
            result.findings.append(Finding("visual", f"Baseline visual ausente: {name}", "Não foi possível comparar a captura.", "medium", "high", evidence=str(actual), expected=str(baseline)))
            return
        try:
            ratio, diff_path = compare_images(baseline, actual, self.evidence_dir / f"{name}-{engine}-{index}-diff.png")
        except ImportError:
            result.findings.append(Finding("framework", "Pillow não instalado", "A comparação visual foi ignorada.", "info", "high", recommendation="Instalar o extra visual."))
            return
        threshold = float(action.get("max_diff_ratio", self.browser_config.get("max_diff_ratio", 0.001)))
        if ratio > threshold:
            result.evidence.append(str(diff_path))
            result.findings.append(Finding(
                "visual", f"Regressão visual: {name} ({engine})", "A diferença excedeu a tolerância configurada.",
                str(action.get("severity", "medium")), "high", evidence=str(diff_path),
                expected=f"diferença <= {threshold:.6f}", observed=f"diferença = {ratio:.6f}",
            ))

    def _run_axe(self, page: Any, engine: str, name: str, result: SuiteResult) -> None:
        axe_script = self.browser_config.get("axe_script")
        if not axe_script:
            return
        path = Path(str(axe_script)).resolve()
        if not path.is_file():
            result.findings.append(Finding("framework", "axe-core não encontrado", "O script local configurado não existe.", "medium", "high", location=str(path)))
            return
        page.add_script_tag(path=str(path))
        audit = page.evaluate("async () => await axe.run(document)")
        for violation in audit.get("violations", []):
            result.findings.append(Finding(
                category="accessibility",
                title=str(violation.get("help", violation.get("id", "Violação axe"))),
                description=str(violation.get("description", "")),
                severity=axe_severity(violation.get("impact")),
                confidence="high",
                location=page.url,
                evidence=json.dumps(violation.get("nodes", [])[:5], ensure_ascii=False),
                recommendation=str(violation.get("helpUrl", "")),
                reference=str(violation.get("id", "axe-core")),
                metadata={"engine": engine, "journey": name},
            ))

    @staticmethod
    def _value(raw: Any) -> str:
        value = str(raw)
        if value.startswith("${") and value.endswith("}"):
            name = value[2:-1]
            if name not in os.environ:
                raise ValueError(f"Variável de ambiente obrigatória ausente: {name}")
            return os.environ[name]
        return value


def compare_images(baseline: Path, actual: Path, diff_path: Path) -> tuple[float, Path]:
    from PIL import Image, ImageChops

    with Image.open(baseline).convert("RGBA") as expected, Image.open(actual).convert("RGBA") as observed:
        if expected.size != observed.size:
            return 1.0, diff_path
        diff = ImageChops.difference(expected, observed)
        histogram = diff.convert("RGB").histogram()
        changed = sum(value for index, value in enumerate(histogram) if index % 256 != 0)
        total = expected.width * expected.height * 3
        ratio = changed / total if total else 0.0
        if ratio:
            diff.save(diff_path)
        return ratio, diff_path


def axe_severity(impact: Any) -> str:
    return {"critical": "critical", "serious": "high", "moderate": "medium", "minor": "low"}.get(str(impact), "medium")


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-") or "journey"
