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
        report = FrameworkReport(
            {"name": "demo"},
            suites=[
                SuiteResult("ui", findings=[finding]).finish(),
                SuiteResult("api").finish(),
            ],
            quality_gate={"passed": True},
        ).finish()
        with tempfile.TemporaryDirectory() as directory:
            files = UnifiedReporter(directory).generate(report, ["html", "json", "junit", "sarif", "text"])
            self.assertEqual(len(files), 5)
            self.assertEqual(len({Path(item).stem for item in files}), 1)
            html = next(Path(item).read_text(encoding="utf-8") for item in files if item.endswith(".html"))
            self.assertIn("&lt;script&gt;", html)
            self.assertNotIn("<script>alert", html)
            self.assertIn("<h2>ui</h2>", html)
            self.assertIn("<h2>api</h2>", html)
            self.assertIn("Nenhum achado nesta suíte", html)

    def test_reporter_deduplicates_requested_formats_without_overwriting_runs(self):
        report = FrameworkReport({"name": "demo"}, quality_gate={"passed": True}).finish()
        with tempfile.TemporaryDirectory() as directory:
            first = UnifiedReporter(directory).generate(report, ["json", "json"])
            second = UnifiedReporter(directory).generate(report, ["json"])
            self.assertEqual(len(first), 1)
            self.assertNotEqual(first[0], second[0])
            self.assertEqual([item for item in Path(directory).iterdir() if item.name.startswith(".")], [])

    def test_redacts_common_secrets(self):
        text = redact_text('Authorization: Bearer abc123 password="secret" token=xyz')
        self.assertNotIn("abc123", text)
        self.assertNotIn("secret", text)
        self.assertNotIn("xyz", text)
        self.assertEqual(text.count("[REDACTED]"), 3)

    def test_redacts_free_text_credential_pairs(self):
        text = redact_text("O sistema aceita credenciais fracas: admin/password")
        self.assertNotIn("admin/password", text)
        self.assertIn("[REDACTED]", text)
        text = redact_text("Login bem-sucedido com admin/password")
        self.assertNotIn("admin/password", text)
        self.assertIn("[REDACTED]", text)


if __name__ == "__main__":
    unittest.main()
