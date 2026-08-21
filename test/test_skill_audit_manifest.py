import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "software-testing" / "scripts"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AuditManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sys

        sys.path.insert(0, str(SCRIPTS))
        cls.contract = load_module("audit_manifest")
        cls.validator = load_module("validate_audit")
        cls.initializer = load_module("init_audit")

    def test_new_manifest_exposes_every_required_item(self):
        manifest = self.contract.new_manifest()
        self.assertEqual(set(manifest["roles"]), set(self.contract.ROLES))
        self.assertEqual(set(manifest["suites"]), set(self.contract.SUITES))
        self.assertEqual(len(manifest["dimensions"]), 25)
        self.assertEqual(len(manifest["adversarial_tests"]), 24)

    def test_pending_manifest_is_rejected(self):
        errors = self.validator.validate_manifest(self.contract.new_manifest())
        self.assertGreater(len(errors), 70)

    def test_complete_or_justified_manifest_is_accepted(self):
        manifest = self.contract.new_manifest()
        manifest["audit"].update({
            "system": "Example", "scope": "full", "environment": "local",
            "started_at": "2026-08-17T10:00:00-03:00",
            "finished_at": "2026-08-17T11:00:00-03:00",
        })
        for group in ("roles", "suites", "dimensions", "adversarial_tests", "deliverables"):
            for item in manifest[group].values():
                item.update({"status": "complete", "evidence": ["evidence.json"]})
        self.assertEqual(self.validator.validate_manifest(manifest), [])
        json.dumps(manifest)

    def test_roles_and_deliverables_cannot_be_skipped(self):
        manifest = self.contract.new_manifest()
        manifest["audit"].update({
            "system": "Example", "scope": "full", "environment": "local",
            "started_at": "2026-08-17T10:00:00-03:00",
            "finished_at": "2026-08-17T11:00:00-03:00",
        })
        for group in ("roles", "suites", "dimensions", "adversarial_tests", "deliverables"):
            for item in manifest[group].values():
                item.update({"status": "complete", "evidence": ["evidence.json"]})
        manifest["roles"]["system-mapper"] = {"status": "not_applicable", "evidence": [], "reason": "sem código"}
        manifest["deliverables"]["PENDING.md"] = {"status": "blocked", "evidence": [], "reason": "sem pendências"}
        errors = self.validator.validate_manifest(manifest)
        self.assertTrue(any("roles.system-mapper: deve ser complete" in error for error in errors))
        self.assertTrue(any("deliverables.PENDING.md: deve ser complete" in error for error in errors))


class InitAuditOutputIsolationTests(unittest.TestCase):
    """O diretório de saída da auditoria deve ficar sempre fora do projeto-alvo."""

    @classmethod
    def setUpClass(cls):
        import sys

        sys.path.insert(0, str(SCRIPTS))
        cls.initializer = load_module("init_audit")

    def test_project_root_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out" / "audit-manifest.json"
            with self.assertRaises(SystemExit):
                self.initializer.main([str(output)])

    def test_rejects_output_inside_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "meu-projeto"
            project_root.mkdir()
            output = project_root / "qa-results" / "audit-manifest.json"
            with self.assertRaises(SystemExit):
                self.initializer.main([str(output), "--project-root", str(project_root)])
            self.assertFalse(output.exists())

    def test_accepts_output_outside_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "meu-projeto"
            project_root.mkdir()
            output = Path(directory) / "qa-results" / "audit-manifest.json"
            code = self.initializer.main([str(output), "--project-root", str(project_root)])
            self.assertEqual(code, 0)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
