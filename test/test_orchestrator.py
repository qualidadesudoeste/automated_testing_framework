import time
import unittest

from testing_framework.models import Finding, FrameworkReport, SuiteResult
from testing_framework.orchestrator import Orchestrator


class OrchestratorResilienceTests(unittest.TestCase):
    def test_suite_timeout_returns_error_instead_of_blocking_report(self):
        orchestrator = Orchestrator({
            "target": {"base_url": "http://127.0.0.1:8000"},
            "general": {"suite_timeout": 0.01},
        })

        started = time.monotonic()
        result = orchestrator._run_with_timeout("future_suite", lambda: self._slow_suite())

        self.assertLess(time.monotonic() - started, 0.2)
        self.assertEqual(result.status, "error")
        self.assertIn("excedeu o limite", result.findings[0].observed)

    @staticmethod
    def _slow_suite() -> SuiteResult:
        time.sleep(0.5)
        return SuiteResult("future_suite").finish()

    def test_deduplication_keeps_attribution_across_suites(self):
        first = Finding("contract", "Mesmo sintoma", "Falha", location="/users")
        second = Finding("contract", "Mesmo sintoma", "Falha", location="/users")
        report = FrameworkReport(
            {"name": "demo"},
            suites=[SuiteResult("api", findings=[first]), SuiteResult("openapi", findings=[second])],
        )

        Orchestrator._deduplicate(report)

        self.assertEqual([len(suite.findings) for suite in report.suites], [1, 1])


if __name__ == "__main__":
    unittest.main()
