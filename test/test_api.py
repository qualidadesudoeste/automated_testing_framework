import unittest
from unittest.mock import MagicMock, patch

from testing_framework.models import SuiteResult
from testing_framework.testers.api import ApiTester


def base_config():
    return {"target": {"base_url": "http://127.0.0.1:8000"}, "general": {"timeout": 5, "max_workers": 10}, "api": {}}


class ApiResourceLimitsTests(unittest.TestCase):
    def test_flags_when_server_does_not_cap_page_size(self):
        with patch("testing_framework.testers.api.create_session") as create_session:
            session = MagicMock()
            response = MagicMock()
            response.json.return_value = {"items": list(range(5000))}
            session.get.return_value = response
            create_session.return_value = session
            tester = ApiTester(base_config())
            result = SuiteResult("api")
            tester._assert_resource_limits(
                "GET", "http://127.0.0.1:8000/api/customers", {},
                {"page_size_param": "limit", "oversized_value": 100000, "items_path": "items", "max_allowed_items": 200},
                result,
            )
            self.assertEqual(len(result.findings), 1)
            self.assertEqual(result.findings[0].reference, "API4:2023")

    def test_no_finding_when_server_caps_page_size(self):
        with patch("testing_framework.testers.api.create_session") as create_session:
            session = MagicMock()
            response = MagicMock()
            response.json.return_value = {"items": list(range(150))}
            session.get.return_value = response
            create_session.return_value = session
            tester = ApiTester(base_config())
            result = SuiteResult("api")
            tester._assert_resource_limits(
                "GET", "http://127.0.0.1:8000/api/customers", {},
                {"page_size_param": "limit", "oversized_value": 100000, "items_path": "items", "max_allowed_items": 200},
                result,
            )
            self.assertEqual(result.findings, [])

    def test_only_supports_get(self):
        with patch("testing_framework.testers.api.create_session") as create_session:
            create_session.return_value = MagicMock()
            tester = ApiTester(base_config())
            result = SuiteResult("api")
            tester._assert_resource_limits("POST", "http://127.0.0.1:8000/api/customers", {}, {}, result)
            self.assertEqual(len(result.findings), 1)
            self.assertEqual(result.findings[0].category, "framework")


if __name__ == "__main__":
    unittest.main()
