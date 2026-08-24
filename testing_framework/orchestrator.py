"""Orquestra suítes heterogêneas e aplica quality gates."""

from __future__ import annotations

from queue import Empty, Queue
from threading import Thread
from typing import Any, Callable

from performance.performance_tester import PerformanceTester
from security.security_tester import SecurityTester

from .models import Finding, FrameworkReport, SuiteResult
from .safety import TargetClassification, revalidate_or_raise
from .testers.access_control import AccessControlTester
from .testers.api import ApiTester
from .testers.browser import BrowserTester
from .testers.business_rules import BusinessRuleTester
from .testers.openapi import OpenApiTester
from .testers.external_tools import ExternalToolsTester
from .testers.project_quality import ProjectQualityTester
from .testers.web_quality import WebQualityTester


class Orchestrator:
    def __init__(self, config: dict[str, Any], classification: TargetClassification | None = None):
        self.config = config
        self.classification = classification

    def run(self, suites: list[str]) -> FrameworkReport:
        report = FrameworkReport(
            target=self.config["target"],
            metadata={"config": self.config.get("_config_path", "")},
        )
        runners: dict[str, Callable[[], SuiteResult]] = {
            "api": lambda: ApiTester(self.config).run(),
            "openapi": lambda: OpenApiTester(self.config).run(),
            "business_rules": lambda: BusinessRuleTester(self.config).run(),
            "web_quality": lambda: WebQualityTester(self.config).run(),
            "browser": lambda: BrowserTester(self.config).run(),
            "project_quality": lambda: ProjectQualityTester(self.config).run(),
            "external_tools": lambda: ExternalToolsTester(self.config).run(),
            "performance": self._run_performance,
            "security": self._run_security,
            "access_control": lambda: AccessControlTester(self.config).run(),
        }
        for name in suites:
            suite = self._run_with_timeout(name, runners[name])
            report.suites.append(suite)
        self._deduplicate(report)
        report.quality_gate = self._quality_gate(report)
        return report.finish()

    def _run_with_timeout(self, name: str, runner: Callable[[], SuiteResult]) -> SuiteResult:
        """Isola uma suíte para que um deadlock futuro não bloqueie o relatório inteiro.

        A thread é daemon porque Python não oferece cancelamento seguro de threads. Os testadores
        atuais também aplicam timeout nas operações de I/O; este limite é a última barreira.
        """
        outcome: Queue[SuiteResult | BaseException] = Queue(maxsize=1)

        def execute() -> None:
            try:
                if self.classification is not None:
                    revalidate_or_raise(self.config, self.classification, name)
                outcome.put(runner())
            except BaseException as exc:  # inclui saídas inesperadas de extensões futuras
                outcome.put(exc)

        worker = Thread(target=execute, name=f"suite-{name}", daemon=True)
        worker.start()
        suite_timeout = float(self.config.get("general", {}).get("suite_timeout", 300))
        worker.join(suite_timeout)
        if worker.is_alive():
            return self._framework_error(
                name,
                f"A suíte excedeu o limite de {suite_timeout:g} segundos.",
                "Revisar loops, esperas e dependências; ajustar general.suite_timeout apenas se a duração for esperada.",
            )
        try:
            result = outcome.get_nowait()
        except Empty:
            return self._framework_error(name, "A suíte terminou sem devolver resultado.")
        if isinstance(result, BaseException):
            return self._framework_error(
                name,
                f"{type(result).__name__}: {result}",
                "Revisar configuração, dependências e logs da suíte.",
            )
        return result

    @staticmethod
    def _framework_error(name: str, observed: str, recommendation: str = "Revisar a implementação da suíte.") -> SuiteResult:
        suite = SuiteResult(name, status="error")
        suite.findings.append(Finding(
            category="framework",
            title=f"Falha interna na suíte {name}",
            description="A suíte não concluiu normalmente; as demais continuaram sendo executadas.",
            severity="high",
            confidence="high",
            observed=observed,
            recommendation=recommendation,
        ))
        return suite.finish()

    def _run_performance(self) -> SuiteResult:
        raw = PerformanceTester(self.config).run_all_tests()
        result = SuiteResult("performance", metrics={"raw": raw})
        thresholds = self.config.get("performance", {}).get("thresholds", {})
        metric_sets: list[tuple[str, dict[str, Any]]] = []
        for test_name, test in raw.get("tests", {}).items():
            if "metrics" in test:
                metric_sets.append((test_name, test["metrics"]))
            for phase in ("baseline", "spike", "recovery"):
                if phase in test:
                    metric_sets.append((f"{test_name}.{phase}", test[phase]))
            for index, step in enumerate(test.get("results_by_step", [])):
                metric_sets.append((f"{test_name}.step-{index + 1}", step.get("metrics", {})))
        for label, metrics in metric_sets:
            self._check_performance_thresholds(label, metrics, thresholds, result)
        result.metrics["measurements"] = len(metric_sets)
        return result.finish()

    def _check_performance_thresholds(
        self, label: str, metrics: dict[str, Any], thresholds: dict[str, Any], result: SuiteResult
    ) -> None:
        response = metrics.get("response_times", {})
        checks = [
            ("response_time_p95", response.get("p95"), "lte", "P95 de resposta"),
            ("response_time_p99", response.get("p99"), "lte", "P99 de resposta"),
            ("requests_per_second", metrics.get("requests_per_second"), "gte", "throughput"),
        ]
        error_limit = thresholds.get("error_rate")
        if error_limit is not None:
            error_limit = float(error_limit) * 100 if float(error_limit) <= 1 else float(error_limit)
            checks.append(("error_rate", metrics.get("error_rate"), "lte", "taxa de erro (%)"))
            thresholds = dict(thresholds, error_rate=error_limit)
        for key, actual, mode, label_name in checks:
            if key not in thresholds or actual is None:
                continue
            expected = float(thresholds[key])
            failed = float(actual) > expected if mode == "lte" else float(actual) < expected
            if failed:
                result.findings.append(Finding(
                    category="performance",
                    title=f"Threshold de {label_name} violado em {label}",
                    description="A medição não atende ao orçamento de performance configurado.",
                    severity="high",
                    confidence="high",
                    expected=f"{mode} {expected}",
                    observed=str(actual),
                    recommendation="Investigar gargalos e confirmar a regressão com execuções repetidas.",
                ))

    def _run_security(self) -> SuiteResult:
        raw = SecurityTester(self.config).run_all_tests()
        result = SuiteResult("security", metrics={
            "security_score": raw.get("security_score"),
            "tests_executed": raw.get("tests_executed", []),
            "total_issues": raw.get("total_issues", 0),
        })
        for severity, issues in raw.get("issues", {}).items():
            for issue in issues:
                result.findings.append(Finding(
                    category=str(issue.get("category", "security")),
                    title=str(issue.get("title", "Achado de segurança")),
                    description=str(issue.get("description", "")),
                    severity=severity,
                    confidence="medium",
                    status="suspected",
                    location=str(issue.get("url", "")),
                    evidence=str(issue.get("evidence", "")),
                    recommendation=str(issue.get("recommendation", "")),
                    reference=str(issue.get("cwe_id", "")),
                ))
        return result.finish()

    def _quality_gate(self, report: FrameworkReport) -> dict[str, Any]:
        fail_on = set(self.config.get("quality_gate", {}).get("fail_on", ["critical", "high"]))
        blockers = [item.id for item in report.findings if item.severity in fail_on]
        return {"passed": not blockers, "fail_on": sorted(fail_on), "blocking_findings": blockers}

    @staticmethod
    def _deduplicate(report: FrameworkReport) -> None:
        for suite in report.suites:
            # Não deduplicar entre suítes: o mesmo sintoma em tipos de teste diferentes
            # é informação de cobertura e deve continuar atribuído a ambos.
            seen: set[tuple[str, str, str]] = set()
            unique = []
            for item in suite.findings:
                key = (item.category, item.title, item.location)
                if key not in seen:
                    unique.append(item)
                    seen.add(key)
            suite.findings = unique
