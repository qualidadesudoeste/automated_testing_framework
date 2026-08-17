import json
import tempfile
import unittest
from pathlib import Path

from testing_framework.testers.external_tools import count_findings


class ExternalToolTests(unittest.TestCase):
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

