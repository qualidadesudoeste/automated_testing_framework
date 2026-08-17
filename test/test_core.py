import tempfile
import unittest
from pathlib import Path

from testing_framework.models import Finding, FrameworkReport, SuiteResult, redact_text
from testing_framework.reporting import UnifiedReporter


class CoreTests(unittest.TestCase):
    def test_report_normalizes_findings(self):
        finding = Finding("api", "Contrato inválido", "Falha", "high", "high")
        suite = SuiteResult("api", findings=[finding]).finish()
        report = FrameworkReport({"name": "demo"}, suites=[suite], quality_gate={"passed": False}).finish()
        data = report.to_dict()
        self.assertEqual(data["summary"]["findings"], 1)
        self.assertEqual(data["summary"]["by_severity"]["high"], 1)

    def test_reporter_escapes_html_and_generates_ci_formats(self):
        finding = Finding("ui", "<script>alert(1)</script>", "Falha", "medium", "high")
        report = FrameworkReport({"name": "demo"}, suites=[SuiteResult("ui", findings=[finding]).finish()], quality_gate={"passed": True}).finish()
        with tempfile.TemporaryDirectory() as directory:
            files = UnifiedReporter(directory).generate(report, ["html", "json", "junit", "sarif", "text"])
            self.assertEqual(len(files), 5)
            html = next(Path(item).read_text(encoding="utf-8") for item in files if item.endswith(".html"))
            self.assertIn("&lt;script&gt;", html)
            self.assertNotIn("<script>alert", html)

    def test_redacts_common_secrets(self):
        text = redact_text('Authorization: Bearer abc123 password="secret" token=xyz')
        self.assertNotIn("abc123", text)
        self.assertNotIn("secret", text)
        self.assertNotIn("xyz", text)
        self.assertEqual(text.count("[REDACTED]"), 3)


if __name__ == "__main__":
    unittest.main()
