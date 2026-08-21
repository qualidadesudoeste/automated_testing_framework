"""Controle de acesso declarativo: API1 BOLA/IDOR, API3 Mass Assignment, API5 BFLA.

Suíte opt-in (``access_control.enabled``/checks ausentes = pulada). Sempre ativa
(``testing_framework.safety.ACTIVE_SUITES``) porque envia requisições autenticadas e
potencialmente mutantes contra recursos reais usando múltiplas identidades — exige
``--authorized`` como qualquer outra suíte ativa.
"""

from __future__ import annotations

from typing import Any

import requests

from ..assertions import resolve_placeholder
from ..http import assert_same_origin_response, create_session, target_url
from ..models import Finding, SuiteResult


class AccessControlTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.ac_config = config.get("access_control", {})
        self.timeout = config.get("general", {}).get("timeout", 15)
        self._sessions: dict[str, requests.Session] = {}

    def run(self) -> SuiteResult:
        result = SuiteResult("access_control")
        bola_checks = self.ac_config.get("bola_checks", [])
        bfla_checks = self.ac_config.get("bfla_checks", [])
        mass_assignment_checks = self.ac_config.get("mass_assignment_checks", [])
        if not (bola_checks or bfla_checks or mass_assignment_checks):
            result.skipped_reason = "Nenhuma checagem de controle de acesso configurada"
            return result.finish()
        for spec in bola_checks:
            self._check_bola(spec, result)
        for spec in bfla_checks:
            self._check_bfla(spec, result)
        for spec in mass_assignment_checks:
            self._check_mass_assignment(spec, result)
        result.metrics.update({
            "bola_checks": len(bola_checks),
            "bfla_checks": len(bfla_checks),
            "mass_assignment_checks": len(mass_assignment_checks),
        })
        return result.finish()

    def _session_for(self, identity: str) -> requests.Session:
        if identity not in self._sessions:
            spec = self.ac_config.get("identities", {}).get(identity)
            if spec is None:
                raise ValueError(f"Identidade não configurada: {identity}")
            raw_headers = spec.get("headers", {}) if isinstance(spec, dict) else {}
            headers = {str(key): resolve_placeholder(value) for key, value in raw_headers.items()}
            self._sessions[identity] = create_session(self.config, headers)
        return self._sessions[identity]

    def _request(
        self, identity: str, method: str, url: str, spec: dict[str, Any], result: SuiteResult, check_id: str
    ) -> requests.Response | None:
        try:
            session = self._session_for(identity)
        except ValueError as exc:
            result.findings.append(Finding("framework", f"Identidade inválida em {check_id}", str(exc), "high", "high", requirement_id=check_id))
            return None
        try:
            response = session.request(method, url, json=spec.get("json"), timeout=self.timeout)
            assert_same_origin_response(self.config["target"]["base_url"], response)
        except (requests.RequestException, ValueError) as exc:
            result.findings.append(Finding(
                "framework", f"Falha ao executar {check_id}", "A chamada de controle de acesso não foi concluída.",
                "medium", "medium", location=url, observed=str(exc), requirement_id=check_id,
            ))
            return None
        return response

    def _check_bola(self, spec: dict[str, Any], result: SuiteResult) -> None:
        check_id = str(spec.get("id", "BOLA"))
        method = str(spec.get("method", "GET")).upper()
        owner = str(spec.get("owner_identity", ""))
        other = str(spec.get("other_identity", ""))
        if not owner or not other:
            result.findings.append(Finding("framework", f"Checagem BOLA mal configurada: {check_id}", "owner_identity e other_identity são obrigatórios.", "high", "high", requirement_id=check_id))
            return
        try:
            path = str(spec.get("path", "/"))
            placeholder = str(spec.get("id_placeholder", "{id}"))
            resource_id = str(spec.get("owner_resource_id", ""))
            if placeholder and resource_id:
                path = path.replace(placeholder, resource_id)
            url = target_url(self.config["target"]["base_url"], path)
        except ValueError as exc:
            result.findings.append(Finding("framework", f"Origem inválida em {check_id}", str(exc), "high", "high", requirement_id=check_id))
            return
        if self._request(owner, method, url, spec, result, check_id) is None:
            return
        probe = self._request(other, method, url, spec, result, check_id)
        if probe is None:
            return
        denied_statuses = set(spec.get("expect_denied_status", [401, 403, 404]))
        if probe.status_code not in denied_statuses:
            result.findings.append(Finding(
                category="access-control",
                title=f"Possível BOLA/IDOR: {check_id}",
                description="Uma identidade distinta do dono do recurso obteve acesso ao mesmo objeto.",
                severity=str(spec.get("severity", "critical")),
                confidence="medium",
                status="suspected",
                location=url,
                expected=f"status em {sorted(denied_statuses)}",
                observed=f"status {probe.status_code}",
                reference="API1:2023",
                requirement_id=check_id,
                recommendation="Validar autorização por objeto (object-level) no servidor, não apenas autenticação.",
            ))

    def _check_bfla(self, spec: dict[str, Any], result: SuiteResult) -> None:
        check_id = str(spec.get("id", "BFLA"))
        method = str(spec.get("method", "GET")).upper()
        identity = str(spec.get("identity", ""))
        if not identity:
            result.findings.append(Finding("framework", f"Checagem BFLA mal configurada: {check_id}", "identity é obrigatório.", "high", "high", requirement_id=check_id))
            return
        try:
            url = target_url(self.config["target"]["base_url"], str(spec.get("path", "/")))
        except ValueError as exc:
            result.findings.append(Finding("framework", f"Origem inválida em {check_id}", str(exc), "high", "high", requirement_id=check_id))
            return
        response = self._request(identity, method, url, spec, result, check_id)
        if response is None:
            return
        denied_statuses = set(spec.get("expect_denied_status", [401, 403]))
        if response.status_code not in denied_statuses:
            result.findings.append(Finding(
                category="access-control",
                title=f"Possível violação de autorização por função: {check_id}",
                description="Uma identidade de baixo privilégio acessou uma função que deveria ser restrita.",
                severity=str(spec.get("severity", "critical")),
                confidence="medium",
                status="suspected",
                location=url,
                expected=f"status em {sorted(denied_statuses)}",
                observed=f"status {response.status_code}",
                reference="API5:2023",
                requirement_id=check_id,
                recommendation="Validar o papel/permissão do chamador no servidor antes de executar a função.",
            ))

    def _check_mass_assignment(self, spec: dict[str, Any], result: SuiteResult) -> None:
        check_id = str(spec.get("id", "MASSASSIGN"))
        method = str(spec.get("method", "PATCH")).upper()
        identity = str(spec.get("identity", ""))
        if not identity:
            result.findings.append(Finding("framework", f"Checagem de mass assignment mal configurada: {check_id}", "identity é obrigatório.", "high", "high", requirement_id=check_id))
            return
        try:
            url = target_url(self.config["target"]["base_url"], str(spec.get("path", "/")))
            verify_url = target_url(self.config["target"]["base_url"], str(spec.get("verify_path", spec.get("path", "/"))))
        except ValueError as exc:
            result.findings.append(Finding("framework", f"Origem inválida em {check_id}", str(exc), "high", "high", requirement_id=check_id))
            return
        if self._request(identity, method, url, spec, result, check_id) is None:
            return
        verify_response = self._request(identity, "GET", verify_url, {}, result, check_id)
        if verify_response is None:
            return
        try:
            payload = verify_response.json()
        except ValueError:
            result.findings.append(Finding("framework", f"Não foi possível verificar {check_id}", "A resposta de verificação não é JSON.", "medium", "medium", location=verify_url, requirement_id=check_id))
            return
        forbidden = spec.get("forbidden_expected_values", {})
        leaked = {key: value for key, value in forbidden.items() if isinstance(payload, dict) and payload.get(key) == value}
        if leaked:
            result.findings.append(Finding(
                category="access-control",
                title=f"Possível mass assignment: {check_id}",
                description="Campos privilegiados enviados pelo cliente foram aceitos/persistidos pelo servidor.",
                severity=str(spec.get("severity", "high")),
                confidence="medium",
                status="suspected",
                location=url,
                observed=f"Campos aceitos indevidamente: {leaked}",
                reference="API3:2023",
                requirement_id=check_id,
                recommendation="Usar allowlist explícita de campos editáveis por identidade/papel no servidor.",
            ))
