import unittest
from unittest.mock import MagicMock

from testing_framework.models import SuiteResult
from testing_framework.testers.access_control import AccessControlTester


def make_response(status_code, url="http://127.0.0.1:8000/probe", json_body=None):
    response = MagicMock()
    response.status_code = status_code
    response.url = url
    response.history = []
    response.json.return_value = json_body if json_body is not None else {}
    return response


def base_config():
    return {
        "target": {"base_url": "http://127.0.0.1:8000"},
        "general": {"timeout": 5},
        "access_control": {"identities": {"victim": {"headers": {}}, "attacker": {"headers": {}}}},
    }


def wire_sessions(tester, by_identity):
    tester._session_for = lambda identity: by_identity[identity]


class AccessControlBolaTests(unittest.TestCase):
    def test_flags_when_other_identity_is_not_denied(self):
        config = base_config()
        tester = AccessControlTester(config)
        victim = MagicMock(request=MagicMock(return_value=make_response(200)))
        attacker = MagicMock(request=MagicMock(return_value=make_response(200)))  # vulnerável: deveria ser negado
        wire_sessions(tester, {"victim": victim, "attacker": attacker})
        result = SuiteResult("access_control")
        tester._check_bola({"id": "BOLA-1", "path": "/orders/{id}", "owner_resource_id": "1", "owner_identity": "victim", "other_identity": "attacker"}, result)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].reference, "API1:2023")

    def test_no_finding_when_other_identity_is_denied(self):
        config = base_config()
        tester = AccessControlTester(config)
        victim = MagicMock(request=MagicMock(return_value=make_response(200)))
        attacker = MagicMock(request=MagicMock(return_value=make_response(403)))
        wire_sessions(tester, {"victim": victim, "attacker": attacker})
        result = SuiteResult("access_control")
        tester._check_bola({"id": "BOLA-2", "path": "/orders/{id}", "owner_resource_id": "1", "owner_identity": "victim", "other_identity": "attacker"}, result)
        self.assertEqual(result.findings, [])

    def test_missing_identities_is_a_configuration_finding(self):
        config = base_config()
        tester = AccessControlTester(config)
        result = SuiteResult("access_control")
        tester._check_bola({"id": "BOLA-3", "path": "/orders/1"}, result)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].category, "framework")


class AccessControlBflaTests(unittest.TestCase):
    def test_flags_when_low_privilege_identity_is_not_denied(self):
        config = base_config()
        tester = AccessControlTester(config)
        attacker = MagicMock(request=MagicMock(return_value=make_response(200)))
        wire_sessions(tester, {"attacker": attacker})
        result = SuiteResult("access_control")
        tester._check_bfla({"id": "BFLA-1", "path": "/admin/users/1/promote", "method": "POST", "identity": "attacker"}, result)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].reference, "API5:2023")

    def test_no_finding_when_denied(self):
        config = base_config()
        tester = AccessControlTester(config)
        attacker = MagicMock(request=MagicMock(return_value=make_response(401)))
        wire_sessions(tester, {"attacker": attacker})
        result = SuiteResult("access_control")
        tester._check_bfla({"id": "BFLA-2", "path": "/admin/users/1/promote", "method": "POST", "identity": "attacker"}, result)
        self.assertEqual(result.findings, [])


class AccessControlMassAssignmentTests(unittest.TestCase):
    def test_flags_when_privileged_field_is_persisted(self):
        config = base_config()
        tester = AccessControlTester(config)
        session = MagicMock()
        session.request.side_effect = [
            make_response(200),  # PATCH
            make_response(200, json_body={"role": "admin", "is_verified": True}),  # GET verificação
        ]
        wire_sessions(tester, {"victim": session})
        result = SuiteResult("access_control")
        tester._check_mass_assignment({
            "id": "MASSASSIGN-1", "path": "/users/1", "identity": "victim",
            "json": {"name": "Ana", "role": "admin"},
            "forbidden_expected_values": {"role": "admin"},
        }, result)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].reference, "API3:2023")

    def test_no_finding_when_privileged_field_did_not_take_effect(self):
        config = base_config()
        tester = AccessControlTester(config)
        session = MagicMock()
        session.request.side_effect = [
            make_response(200),
            make_response(200, json_body={"role": "user"}),
        ]
        wire_sessions(tester, {"victim": session})
        result = SuiteResult("access_control")
        tester._check_mass_assignment({
            "id": "MASSASSIGN-2", "path": "/users/1", "identity": "victim",
            "json": {"name": "Ana", "role": "admin"},
            "forbidden_expected_values": {"role": "admin"},
        }, result)
        self.assertEqual(result.findings, [])


class AccessControlSuiteTests(unittest.TestCase):
    def test_run_is_skipped_when_no_checks_are_configured(self):
        result = AccessControlTester(base_config()).run()
        self.assertEqual(result.status, "skipped")


if __name__ == "__main__":
    unittest.main()
