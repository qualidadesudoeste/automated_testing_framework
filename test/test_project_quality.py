import tempfile
import unittest
from pathlib import Path

from testing_framework.testers.project_quality import ProjectQualityTester


class ProjectQualityRootResolutionTests(unittest.TestCase):
    def test_default_project_root_is_config_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text("target:\n  base_url: http://127.0.0.1:8000\n", encoding="utf-8")
            config = {"_config_path": str(config_path)}
            tester = ProjectQualityTester(config)
            self.assertEqual(tester.root, Path(directory).resolve())

    def test_explicit_project_root_overrides_default(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "sub" / "config.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("target:\n  base_url: http://127.0.0.1:8000\n", encoding="utf-8")
            config = {"_config_path": str(config_path), "project_quality": {"project_root": ".."}}
            tester = ProjectQualityTester(config)
            self.assertEqual(tester.root, Path(directory).resolve())


if __name__ == "__main__":
    unittest.main()
