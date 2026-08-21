import unittest
from unittest.mock import MagicMock, patch

from security.security_tester import SecurityTester


def make_response(text="", url="http://127.0.0.1:8000/api/health", status_code=200, headers=None):
    response = MagicMock()
    response.text = text
    response.url = url
    response.history = []
    response.status_code = status_code
    response.headers = headers or {}
    return response


def base_config(**safety_overrides):
    return {
        "target": {"base_url": "http://127.0.0.1:8000", "api_endpoints": ["/api/health"], "web_endpoints": []},
        "general": {"timeout": 5},
        "safety": {"max_requests_per_probe": 3, **safety_overrides},
        "security": {},
    }


class SecurityTesterBoundedProbesTests(unittest.TestCase):
    def test_max_requests_per_probe_caps_injection_payload_loop(self):
        with patch("security.security_tester.create_session") as create_session:
            session = MagicMock()
            session.get.return_value = make_response()
            create_session.return_value = session
            tester = SecurityTester(base_config())
            self.assertEqual(tester.max_requests_per_probe, 3)
            self.assertGreater(len(tester.sql_payloads), 3)
            tester.test_sql_injection()
            self.assertEqual(session.get.call_count, 3)

    def test_default_max_requests_per_probe_matches_previous_hardcoded_value(self):
        with patch("security.security_tester.create_session") as create_session:
            create_session.return_value = MagicMock()
            tester = SecurityTester({"target": {"base_url": "http://127.0.0.1:8000"}, "general": {}, "safety": {}, "security": {}})
            self.assertEqual(tester.max_requests_per_probe, 50)


class SecurityTesterOriginGuardTests(unittest.TestCase):
    def test_uses_shared_session_and_origin_validated_requests(self):
        with patch("security.security_tester.create_session") as create_session:
            session = MagicMock()
            create_session.return_value = session
            tester = SecurityTester(base_config())
            self.assertIs(tester.session, session)
            create_session.assert_called_once()

    def test_get_helper_rejects_cross_origin_redirect(self):
        with patch("security.security_tester.create_session") as create_session:
            session = MagicMock()
            redirected = make_response(url="http://evil.example.com/steal")
            session.get.return_value = redirected
            create_session.return_value = session
            tester = SecurityTester(base_config())
            with self.assertRaises(ValueError):
                tester._get("http://127.0.0.1:8000/api/health")


class SecurityTesterNoSqlInjectionTests(unittest.TestCase):
    def test_nosql_payloads_are_no_longer_dead_code(self):
        with patch("security.security_tester.create_session") as create_session:
            session = MagicMock()
            session.get.return_value = make_response(text="MongoError: bad query")
            create_session.return_value = session
            tester = SecurityTester(base_config())
            tester.test_nosql_injection()
            self.assertEqual(len(tester.issues), 1)
            self.assertEqual(tester.issues[0].cwe_id, "CWE-943")


if __name__ == "__main__":
    unittest.main()
