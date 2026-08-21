import json
import tempfile
import unittest
from pathlib import Path

from testing_framework.testers.external_tools import ExternalToolsTester, count_findings


class ExternalToolTests(unittest.TestCase):
    def test_default_project_root_is_config_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text("target:\n  base_url: http://127.0.0.1:8000\n", encoding="utf-8")
            config = {"_config_path": str(config_path), "target": {"base_url": "http://127.0.0.1:8000"}}
            tester = ExternalToolsTester(config)
            self.assertEqual(tester.project_root, Path(directory).resolve())

    def test_counts_list_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps([{"rule": "a"}, {"rule": "b"}]), encoding="utf-8")
            self.assertEqual(count_findings(path), 2)

    def test_counts_named_results(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps({"results": [{"rule": "a"}]}), encoding="utf-8")
            self.assertEqual(count_findings(path), 1)


if __name__ == "__main__":
    unittest.main()

