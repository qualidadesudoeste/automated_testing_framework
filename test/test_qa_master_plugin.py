import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "qa-master-testing"
SCRIPTS = PLUGIN / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class QaMasterPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(SCRIPTS))
        cls.contract = load("run_contract")
        cls.checker = load("check_run")
        cls.bundle_validator = load("validate_bundle")
        cls.initializer = load("init_run")

    def write_result(self, root, agent, coverage=None):
        payload = {
            "agent": agent,
            "status": "complete",
            "summary": "Execução concluída",
            "coverage": coverage or [{"id": "scope", "status": "complete", "evidence": ["evidence.txt"]}],
            "findings": [],
            "artifacts": ["evidence.txt"],
        }
        (root / "agents" / f"{agent}.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_plugin_has_master_and_all_real_specialist_skills(self):
        names = ["qa-master", *self.contract.ALL_AGENTS]
        for name in names:
            skill = PLUGIN / "skills" / name / "SKILL.md"
            self.assertTrue(skill.is_file(), name)

    def test_neutral_bundle_is_valid(self):
        self.assertEqual(self.bundle_validator.validate_bundle(PLUGIN), [])

    def test_checker_blocks_missing_agents_and_releases_complete_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "agents").mkdir()
            manifest = {
                "surface_mode": "auto", "depth_mode": "profundo",
                "controls": {"max_file_reads_per_pass": 40, "max_priority_findings_per_agent": 12, "critical_maturity_gate": 30},
            }
            (root / "run-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertGreater(len(self.checker.validate_run(root, final=False)), 12)
            (root / "SYSTEM_MAP.md").write_text("# Map", encoding="utf-8")
            required = [{"id": item, "status": "complete", "evidence": ["evidence.txt"]} for item in self.contract.REQUIRED_COVERAGE]
            for index, agent in enumerate(self.contract.SPECIALISTS):
                self.write_result(root, agent, required if index == 0 else None)
            self.assertEqual(self.checker.validate_run(root, final=False), [])
            self.write_result(root, self.contract.CONSOLIDATOR)
            for deliverable in self.contract.DELIVERABLES:
                (root / deliverable).write_text("complete", encoding="utf-8")
            self.assertEqual(self.checker.validate_run(root, final=True), [])

    def test_init_run_requires_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "run"
            with self.assertRaises(SystemExit):
                self.initializer.main([str(run_dir)])

    def test_init_run_rejects_run_dir_inside_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "meu-projeto"
            project_root.mkdir()
            run_dir = project_root / "qa-results"
            with self.assertRaises(SystemExit):
                self.initializer.main([str(run_dir), "--project-root", str(project_root)])
            self.assertFalse(run_dir.exists())

    def test_init_run_accepts_run_dir_outside_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "meu-projeto"
            project_root.mkdir()
            run_dir = Path(directory) / "qa-results"
            code = self.initializer.main([str(run_dir), "--project-root", str(project_root)])
            self.assertEqual(code, 0)
            self.assertTrue((run_dir / "run-manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
