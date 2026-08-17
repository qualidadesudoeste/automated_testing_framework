"""Validação declarativa e segura de regras de negócio."""

from __future__ import annotations

from typing import Any
import requests

from ..http import create_session, target_url
from ..models import Finding, SuiteResult
from ..assertions import OPERATORS, resolve


class BusinessRuleTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.rules_config = config.get("business_rules", {})
        self.timeout = config.get("general", {}).get("timeout", 15)
        self.session = create_session(config)

    def run(self) -> SuiteResult:
        result = SuiteResult("business_rules")
        rules = self.rules_config.get("rules", [])
        if not rules:
            result.skipped_reason = "Nenhuma regra declarativa configurada"
            return result.finish()
        for rule in rules:
            self._run_rule(rule, result)
        result.metrics["rules_tested"] = len(rules)
        return result.finish()

    def _run_rule(self, rule: dict[str, Any], result: SuiteResult) -> None:
        rule_id = str(rule.get("id", "RULE"))
        operation = str(rule.get("operator", "eq"))
        if operation not in OPERATORS:
            result.findings.append(Finding(
                category="business-rule",
                title=f"Operador inválido na regra {rule_id}",
                description=f"O operador {operation!r} não é suportado.",
                severity="high",
                confidence="high",
                requirement_id=rule_id,
            ))
            return
        try:
            url = target_url(self.config["target"]["base_url"], str(rule.get("endpoint", "/")))
        except ValueError as exc:
            result.findings.append(Finding("framework", f"Origem inválida na regra {rule_id}", str(exc), "high", "high", requirement_id=rule_id))
            return
        try:
            response = self.session.request(
                str(rule.get("method", "GET")).upper(),
                url,
                params=rule.get("params"),
                json=rule.get("json"),
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            result.findings.append(Finding(
                category="business-rule",
                title=f"Não foi possível avaliar a regra {rule_id}",
                description="A fonte de dados da regra falhou ou não retornou JSON.",
                severity="high",
                confidence="high",
                location=url,
                observed=str(exc),
                requirement_id=rule_id,
            ))
            return
        absent, actual = resolve(payload, str(rule.get("path", "")))
        expected = rule.get("expected")
        try:
            passed = False if absent else OPERATORS[operation](actual, expected)
        except (TypeError, ValueError, IndexError) as exc:
            result.findings.append(Finding(
                category="business-rule",
                title=f"Regra mal configurada: {rule_id}",
                description="O operador não pôde avaliar o valor recebido.",
                severity="high",
                confidence="high",
                observed=str(exc),
                requirement_id=rule_id,
            ))
            return
        if not passed:
            result.findings.append(Finding(
                category="business-rule",
                title=f"Regra de negócio violada: {rule_id}",
                description=str(rule.get("description", "O resultado não atende à regra declarada.")),
                severity=str(rule.get("severity", "high")),
                confidence="high",
                location=url,
                expected=f"{rule.get('path')} {operation} {expected!r}",
                observed="campo ausente" if absent else repr(actual),
                requirement_id=rule_id,
                recommendation=str(rule.get("recommendation", "Corrigir a implementação ou revisar a regra configurada.")),
            ))
