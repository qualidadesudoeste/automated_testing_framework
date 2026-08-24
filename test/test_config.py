import tempfile
import unittest
from pathlib import Path

from testing_framework.config import load_config, selected_suites


class ConfigTests(unittest.TestCase):
    def test_loads_defaults_and_enabled_suites(self):
        content = """
target:
  base_url: http://127.0.0.1:8000
api:
  enabled: true
security:
  enabled: false
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            config = load_config(path)
        self.assertEqual(selected_suites(config), ["api"])
        self.assertEqual(config["general"]["timeout"], 15)
        self.assertEqual(config["general"]["suite_timeout"], 300)

    def test_rejects_non_http_target(self):
        content = "target:\n  base_url: file:///tmp/data\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)

    def test_rejects_invalid_authorship_scan_limits(self):
        content = """
target:
  base_url: http://127.0.0.1:8000
project_quality:
  ai_authorship_max_findings: 0
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)

    def test_output_dir_base_defaults_to_cwd_and_accepts_config(self):
        content = "target:\n  base_url: http://127.0.0.1:8000\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            config = load_config(path)
        self.assertEqual(config["reporting"]["output_dir_base"], "cwd")

    def test_rejects_invalid_output_dir_base(self):
        content = "target:\n  base_url: http://127.0.0.1:8000\nreporting:\n  output_dir_base: elsewhere\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)

    def test_rejects_non_positive_max_requests_per_probe(self):
        content = "target:\n  base_url: http://127.0.0.1:8000\nsafety:\n  max_requests_per_probe: 0\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)

    def test_rejects_invalid_suite_timeout_and_empty_report_formats(self):
        invalid_configs = (
            "target:\n  base_url: http://127.0.0.1:8000\ngeneral:\n  suite_timeout: false\n",
            "target:\n  base_url: http://127.0.0.1:8000\nreporting:\n  formats: []\n",
        )
        for content in invalid_configs:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "config.yaml"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_config(path)

    def test_access_control_is_a_known_suite(self):
        content = "target:\n  base_url: http://127.0.0.1:8000\naccess_control:\n  enabled: true\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            config = load_config(path)
        self.assertEqual(selected_suites(config), ["access_control"])


if __name__ == "__main__":
    unittest.main()
