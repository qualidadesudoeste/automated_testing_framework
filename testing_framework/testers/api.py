"""Testes declarativos de API e contrato."""

from __future__ import annotations

from typing import Any
import concurrent.futures
import requests

from ..http import create_session, target_url
from ..models import Finding, SuiteResult
from ..assertions import OPERATORS


class ApiTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.target = config["target"]
        self.api_config = config.get("api", {})
        self.timeout = config.get("general", {}).get("timeout", 15)
        self.session = create_session(config, self.api_config.get("headers", {}))

    def run(self) -> SuiteResult:
        result = SuiteResult("api")
        endpoints = self.api_config.get("endpoints", self.target.get("api_endpoints", []))
        if not endpoints:
            result.skipped_reason = "Nenhum endpoint de API configurado"
            return result.finish()

        for raw in endpoints:
            spec = {"path": raw} if isinstance(raw, str) else raw
            self._test_endpoint(spec, result)
        result.metrics["endpoints_tested"] = len(endpoints)
        return result.finish()

    def _test_endpoint(self, spec: dict[str, Any], result: SuiteResult) -> None:
        path = str(spec.get("path", "/"))
        try:
            url = target_url(self.target["base_url"], path)
        except ValueError as exc:
            result.findings.append(Finding("framework", "Endpoint fora do alvo autorizado", str(exc), "high", "high"))
            return
        method = str(spec.get("method", "GET")).upper()
        expected_status = spec.get("expected_status", 200)
        expected_statuses = expected_status if isinstance(expected_status, list) else [expected_status]
        try:
            response = self.session.request(
                method,
                url,
                params=spec.get("params"),
                json=spec.get("json"),
                headers=spec.get("headers"),
                timeout=self.timeout,
                allow_redirects=spec.get("allow_redirects", True),
            )
        except requests.RequestException as exc:
            result.findings.append(Finding(
                category="api",
                title=f"Endpoint inacessível: {method} {path}",
                description="A chamada não pôde ser concluída.",
                severity="high",
                confidence="high",
                location=url,
                observed=str(exc),
                recommendation="Validar disponibilidade, DNS, certificado e timeout do endpoint.",
            ))
            return

        body = None
        try:
            body = response.json()
        except ValueError:
            pass

        if response.status_code not in expected_statuses:
            result.findings.append(Finding(
                category="api",
                title=f"Status inesperado em {method} {path}",
                description="O contrato de status HTTP não foi atendido.",
                severity=spec.get("severity", "high"),
                confidence="high",
                location=url,
                expected=str(expected_statuses),
                observed=str(response.status_code),
                evidence=response.text[:500],
                recommendation="Corrigir o endpoint ou atualizar explicitamente o contrato esperado.",
            ))

        content_type = spec.get("content_type")
        actual_content_type = response.headers.get("content-type", "")
        if content_type and content_type.lower() not in actual_content_type.lower():
            result.findings.append(Finding(
                category="api-contract",
                title=f"Content-Type inesperado em {path}",
                description="A resposta não utiliza o tipo de conteúdo definido no contrato.",
                severity="medium",
                confidence="high",
                location=url,
                expected=content_type,
                observed=actual_content_type,
            ))

        required_fields = spec.get("required_json_fields", [])
        if required_fields:
            missing = [field for field in required_fields if _resolve(body, field, missing=True)[0]]
            if missing:
                result.findings.append(Finding(
                    category="api-contract",
                    title=f"Campos obrigatórios ausentes em {path}",
                    description="A resposta JSON não atende ao contrato mínimo.",
                    severity="high",
                    confidence="high",
                    location=url,
                    expected=", ".join(required_fields),
                    observed=f"Ausentes: {', '.join(missing)}",
                ))

        contains = spec.get("response_contains")
        if contains is not None and str(contains) not in response.text:
            result.findings.append(Finding(
                category="functional",
                title=f"Conteúdo esperado ausente em {path}",
                description="A resposta não contém o conteúdo funcional configurado.",
                severity="medium",
                confidence="high",
                location=url,
                expected=str(contains),
                observed=response.text[:500],
            ))

        maximum = spec.get("max_response_ms")
        elapsed_ms = response.elapsed.total_seconds() * 1000
        if maximum is not None and elapsed_ms > float(maximum):
            result.findings.append(Finding(
                category="performance",
                title=f"SLA de resposta violado em {method} {path}",
                description="A chamada excedeu o tempo máximo configurado.",
                severity="high",
                confidence="high",
                location=url,
                expected=f"<= {maximum} ms",
                observed=f"{elapsed_ms:.2f} ms",
            ))

        for header in spec.get("required_headers", []):
            if str(header).lower() not in {name.lower() for name in response.headers}:
                result.findings.append(Finding("api-contract", f"Header obrigatório ausente: {header}", "A resposta não contém o header declarado.", "medium", "high", location=url))

        for assertion in spec.get("json_assertions", []):
            self._assert_json(body, assertion, url, result)

        sort_spec = spec.get("assert_sorted")
        if sort_spec:
            self._assert_sorted(body, sort_spec, url, result)

        filter_spec = spec.get("assert_filter")
        if filter_spec:
            self._assert_filter(body, filter_spec, url, result)

        pagination = spec.get("assert_pagination")
        if pagination:
            self._assert_pagination(method, url, spec, pagination, result)

        concurrency = spec.get("concurrency")
        if concurrency:
            self._assert_concurrency(method, url, spec, concurrency, result)

    def _assert_json(self, body: Any, assertion: dict[str, Any], url: str, result: SuiteResult) -> None:
        path = str(assertion.get("path", ""))
        operation = str(assertion.get("operator", "eq"))
        absent, actual = _resolve(body, path)
        expected = assertion.get("expected")
        try:
            passed = not absent and operation in OPERATORS and OPERATORS[operation](actual, expected)
        except (TypeError, ValueError, IndexError):
            passed = False
        if not passed:
            result.findings.append(Finding(
                "functional", f"Asserção JSON falhou: {path}",
                "A resposta não atende à condição funcional configurada.",
                str(assertion.get("severity", "high")), "high", location=url,
                expected=f"{operation} {expected!r}", observed="campo ausente" if absent else repr(actual),
                requirement_id=str(assertion.get("requirement_id", "")),
            ))

    def _assert_sorted(self, body: Any, spec: dict[str, Any], url: str, result: SuiteResult) -> None:
        absent, items = _resolve(body, str(spec.get("items_path", "")))
        field = str(spec.get("field", ""))
        direction = str(spec.get("direction", "asc"))
        try:
            values = [_resolve(item, field)[1] for item in items]
            expected = sorted(values, reverse=direction == "desc")
            passed = not absent and values == expected
        except (TypeError, KeyError):
            passed = False
            values = []
        if not passed:
            result.findings.append(Finding("functional", "Ordenação incorreta na API", "Os itens não respeitam a ordenação configurada.", "medium", "high", location=url, expected=f"{field} {direction}", observed=repr(values[:20])))

    def _assert_filter(self, body: Any, spec: dict[str, Any], url: str, result: SuiteResult) -> None:
        absent, items = _resolve(body, str(spec.get("items_path", "")))
        field = str(spec.get("field", ""))
        expected = str(spec.get("contains", ""))
        try:
            invalid = [item for item in items if expected.casefold() not in str(_resolve(item, field)[1]).casefold()]
        except TypeError:
            invalid = [body]
        if absent or invalid:
            result.findings.append(Finding("functional", "Filtro retornou dados incompatíveis", "Há resultados que não atendem ao filtro configurado.", "high", "high", location=url, expected=f"{field} contém {expected!r}", observed=f"{len(invalid)} itens incompatíveis"))

    def _assert_pagination(self, method: str, url: str, endpoint: dict[str, Any], spec: dict[str, Any], result: SuiteResult) -> None:
        if method != "GET":
            result.findings.append(Finding("framework", "Paginação exige GET", "A verificação automática de paginação aceita apenas GET.", "medium", "high", location=url))
            return
        page_param = str(spec.get("page_param", "page"))
        pages = list(spec.get("pages", [1, 2]))
        if len(pages) < 2:
            result.findings.append(Finding("framework", "Paginação exige duas páginas", "Configure duas páginas distintas para comparação.", "medium", "high", location=url))
            return
        first, second = pages[:2]
        params = dict(endpoint.get("params") or {})
        try:
            params[page_param] = first
            first_body = self.session.get(url, params=params, timeout=self.timeout).json()
            params[page_param] = second
            second_body = self.session.get(url, params=params, timeout=self.timeout).json()
            first_items = _resolve(first_body, str(spec.get("items_path", "")))[1]
            second_items = _resolve(second_body, str(spec.get("items_path", "")))[1]
            id_path = str(spec.get("id_path", "id"))
            ids1 = {_resolve(item, id_path)[1] for item in first_items}
            ids2 = {_resolve(item, id_path)[1] for item in second_items}
            overlap = ids1.intersection(ids2)
        except (requests.RequestException, ValueError, TypeError):
            overlap = {"erro"}
        if overlap:
            result.findings.append(Finding("functional", "Paginação inconsistente", "Páginas consecutivas possuem itens repetidos ou não puderam ser comparadas.", "medium", "medium", location=url, observed=repr(list(overlap)[:20])))

    def _assert_concurrency(self, method: str, url: str, endpoint: dict[str, Any], spec: dict[str, Any], result: SuiteResult) -> None:
        workers = max(1, min(int(spec.get("workers", 2)), int(self.config.get("general", {}).get("max_workers", 10))))
        requests_count = max(1, int(spec.get("requests", workers)))
        def execute() -> int:
            response = requests.request(method, url, params=endpoint.get("params"), json=endpoint.get("json"), headers=endpoint.get("headers"), timeout=self.timeout)
            return response.status_code
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                statuses = list(executor.map(lambda _index: execute(), range(requests_count)))
        except requests.RequestException as exc:
            statuses = [0]
            result.findings.append(Finding("reliability", "Falha durante teste concorrente", "Uma chamada concorrente não foi concluída.", "high", "high", location=url, observed=str(exc)))
        configured_status = spec.get("expected_status", [200])
        expected = set(configured_status if isinstance(configured_status, list) else [configured_status])
        invalid = [status for status in statuses if status not in expected]
        if invalid:
            result.findings.append(Finding("reliability", "Resultado inconsistente sob concorrência", "Chamadas simultâneas retornaram status inesperados.", "high", "high", location=url, expected=str(sorted(expected)), observed=str(statuses)))
        result.metrics.setdefault("concurrency", []).append({"url": url, "workers": workers, "requests": requests_count, "statuses": statuses})


def _resolve(value: Any, path: str, missing: bool = False) -> tuple[bool, Any]:
    current = value
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return True, None
    return False, current
