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


if __name__ == "__main__":
    unittest.main()
