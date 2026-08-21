import unittest
from unittest.mock import MagicMock

from testing_framework.http import assert_same_origin_response, target_url


def fake_response(url: str, history: list | None = None) -> MagicMock:
    response = MagicMock()
    response.url = url
    response.history = history or []
    return response


class TargetUrlTests(unittest.TestCase):
    def test_joins_path_within_authorized_origin(self):
        self.assertEqual(target_url("http://127.0.0.1:8000", "/api/health"), "http://127.0.0.1:8000/api/health")

    def test_rejects_cross_origin_path(self):
        with self.assertRaises(ValueError):
            target_url("http://127.0.0.1:8000", "https://example.com/data")


class AssertSameOriginResponseTests(unittest.TestCase):
    def test_passes_when_final_url_matches_authorized_origin(self):
        response = fake_response("http://127.0.0.1:8000/api/health")
        assert_same_origin_response("http://127.0.0.1:8000", response)  # não deve levantar

    def test_passes_when_redirect_chain_stays_in_origin(self):
        response = fake_response(
            "http://127.0.0.1:8000/final",
            history=[fake_response("http://127.0.0.1:8000/redirect-1")],
        )
        assert_same_origin_response("http://127.0.0.1:8000", response)  # não deve levantar

    def test_raises_when_final_response_left_the_origin(self):
        response = fake_response("http://evil.example.com/steal")
        with self.assertRaises(ValueError):
            assert_same_origin_response("http://127.0.0.1:8000", response)

    def test_raises_when_intermediate_hop_left_the_origin(self):
        response = fake_response(
            "http://127.0.0.1:8000/final",
            history=[fake_response("http://169.254.169.254/latest/meta-data/")],
        )
        with self.assertRaises(ValueError):
            assert_same_origin_response("http://127.0.0.1:8000", response)


if __name__ == "__main__":
    unittest.main()
