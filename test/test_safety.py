import unittest
from unittest.mock import patch

from testing_framework.safety import (
    SafetyError,
    TargetClassification,
    classify_target,
    has_active_requests,
    revalidate_or_raise,
    validate_execution,
)
from testing_framework.http import target_url


def base_config(url="http://127.0.0.1:8000"):
    return {
        "target": {"base_url": url},
        "safety": {
            "allow_external_targets": False,
            "require_authorization_for_active_tests": True,
            "max_users": 10,
            "max_duration_seconds": 30,
        },
        "performance": {
            "load_test": {"users": 5, "duration": 5},
            "stress_test": {"max_users": 5, "step_duration": 5},
            "spike_test": {"spike_users": 5, "spike_duration": 5},
        },
    }


class SafetyTests(unittest.TestCase):
    def test_local_target_is_classified(self):
        self.assertEqual(classify_target("http://127.0.0.1:8000").scope, "local")

    def test_active_suite_requires_authorization(self):
        with self.assertRaises(SafetyError):
            validate_execution(base_config(), ["performance"], authorized=False, dry_run=False)

    def test_dry_run_never_requires_authorization(self):
        target = validate_execution(base_config(), ["performance"], authorized=False, dry_run=True)
        self.assertEqual(target.scope, "local")

    def test_external_target_is_blocked(self):
        with self.assertRaises(SafetyError):
            validate_execution(base_config("https://8.8.8.8"), ["api"], authorized=False, dry_run=False)

    def test_endpoint_cannot_escape_authorized_origin(self):
        with self.assertRaises(ValueError):
            target_url("http://127.0.0.1:8000", "https://example.com/data")

    def test_mutating_api_requires_authorization(self):
        config = base_config()
        config["api"] = {"endpoints": [{"path": "/users", "method": "POST"}]}
        self.assertTrue(has_active_requests(config, ["api"]))
        with self.assertRaises(SafetyError):
            validate_execution(config, ["api"], authorized=False, dry_run=False)

    def test_link_local_target_is_classified_external(self):
        # Inclui o metadata IP de nuvem (169.254.169.254): tratar como "private" bastaria
        # com --authorized; precisa exigir allow_external_targets, o nível mais alto.
        with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("169.254.169.254", 0))]):
            self.assertEqual(classify_target("http://metadata.internal").scope, "external")

    def test_link_local_target_is_blocked_without_allow_external_targets(self):
        config = base_config("http://metadata.internal")
        with patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("169.254.169.254", 0))]):
            with self.assertRaises(SafetyError):
                validate_execution(config, ["security"], authorized=True, dry_run=False)

    def test_revalidate_or_raise_ignores_passive_suites(self):
        classification = TargetClassification("127.0.0.1", "local", ["127.0.0.1"])
        revalidate_or_raise(base_config(), classification, "api")  # não deve levantar

    def test_revalidate_or_raise_blocks_on_dns_rebinding(self):
        classification = TargetClassification("127.0.0.1", "local", ["127.0.0.1"])
        with patch("testing_framework.safety.classify_target", return_value=TargetClassification("127.0.0.1", "external", ["203.0.113.5"])):
            with self.assertRaises(SafetyError):
                revalidate_or_raise(base_config(), classification, "security")

    def test_revalidate_or_raise_allows_stable_resolution(self):
        classification = TargetClassification("127.0.0.1", "local", ["127.0.0.1"])
        with patch("testing_framework.safety.classify_target", return_value=classification):
            revalidate_or_raise(base_config(), classification, "security")  # não deve levantar


if __name__ == "__main__":
    unittest.main()
