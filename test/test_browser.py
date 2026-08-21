import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from testing_framework.testers.browser import BrowserTester, axe_severity, compare_images, safe_name


class BrowserUtilityTests(unittest.TestCase):
    def test_normalizes_evidence_name(self):
        self.assertEqual(safe_name("Login / usuário"), "Login-usu-rio")

    def test_maps_axe_impact(self):
        self.assertEqual(axe_severity("serious"), "high")
        self.assertEqual(axe_severity("minor"), "low")

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow opcional não instalado")
    def test_identical_visuals_have_zero_diff(self):
        root = Path(__file__).resolve().parents[1]
        logo = root / "assets" / "LogoSudoeste_OFICIAL.png"
        ratio, _ = compare_images(logo, logo, root / "reports" / "unused-diff.png")
        self.assertEqual(ratio, 0.0)


def make_tester() -> BrowserTester:
    return BrowserTester({"target": {"base_url": "http://127.0.0.1:8000"}, "browser": {}})


class AssertLoadingStateTests(unittest.TestCase):
    """Nielsen H1 — visibilidade do status do sistema. Testado sem browser real:
    `_perform`/os helpers só chamam métodos do objeto `page`, nunca importam Playwright."""

    def test_passes_when_indicator_appears_and_resolves(self):
        tester = make_tester()
        page = MagicMock()
        tester._assert_loading_state(page, {"trigger_selector": "#submit", "loading_selector": "#spinner"})
        page.locator.return_value.wait_for.assert_any_call(state="visible", timeout=2000)
        page.locator.return_value.wait_for.assert_any_call(state="hidden", timeout=5000)

    def test_raises_when_indicator_never_appears(self):
        tester = make_tester()
        page = MagicMock()
        page.locator.return_value.wait_for.side_effect = TimeoutError("boom")
        with self.assertRaisesRegex(AssertionError, "não apareceu"):
            tester._assert_loading_state(page, {"trigger_selector": "#submit", "loading_selector": "#spinner"})

    def test_raises_when_indicator_stays_visible(self):
        tester = make_tester()
        page = MagicMock()
        page.locator.return_value.wait_for.side_effect = [None, TimeoutError("boom")]
        with self.assertRaisesRegex(AssertionError, "permaneceu visível"):
            tester._assert_loading_state(page, {"trigger_selector": "#submit", "loading_selector": "#spinner"})


class AssertUnsavedChangesWarningTests(unittest.TestCase):
    """Nielsen H3 — controle e liberdade do usuário."""

    def test_passes_when_in_app_modal_is_visible(self):
        tester = make_tester()
        page = MagicMock()
        page.locator.return_value.is_visible.return_value = True
        tester._assert_unsaved_changes_warning(page, {"fill_selector": "#name", "navigate_selector": "#cancel", "warning_selector": "#unsaved-modal"})

    def test_raises_when_in_app_modal_is_absent(self):
        tester = make_tester()
        page = MagicMock()
        page.locator.return_value.is_visible.return_value = False
        with self.assertRaises(AssertionError):
            tester._assert_unsaved_changes_warning(page, {"fill_selector": "#name", "navigate_selector": "#cancel", "warning_selector": "#unsaved-modal"})

    def test_passes_when_native_dialog_appears(self):
        tester = make_tester()
        page = MagicMock()
        page.expect_dialog.return_value.__enter__.return_value.value = MagicMock()
        tester._assert_unsaved_changes_warning(page, {"fill_selector": "#name", "navigate_selector": "#cancel"})

    def test_raises_when_no_native_dialog_appears(self):
        tester = make_tester()
        page = MagicMock()
        page.expect_dialog.side_effect = TimeoutError("sem diálogo")
        with self.assertRaises(AssertionError):
            tester._assert_unsaved_changes_warning(page, {"fill_selector": "#name", "navigate_selector": "#cancel"})


class ValidateFieldErrorContainsTests(unittest.TestCase):
    """Nielsen H9 — mensagens de erro devem explicar o problema, não só aparecer."""

    def test_passes_when_error_message_explains_the_problem(self):
        tester = make_tester()
        page = MagicMock()
        page.locator.return_value.evaluate.return_value = True
        page.locator.return_value.is_visible.return_value = True
        page.locator.return_value.inner_text.return_value = "CPF inválido"
        page.locator.return_value.input_value.return_value = "123"
        tester._validate_field(page, {"selector": "#cpf", "cases": [
            {"value": "123", "valid": False, "error_selector": "#cpf-error", "error_contains": "CPF inválido"},
        ]})

    def test_raises_when_error_message_is_generic(self):
        tester = make_tester()
        page = MagicMock()
        page.locator.return_value.evaluate.return_value = True
        page.locator.return_value.is_visible.return_value = True
        page.locator.return_value.inner_text.return_value = "Erro"
        page.locator.return_value.input_value.return_value = "123"
        with self.assertRaisesRegex(AssertionError, "não explica"):
            tester._validate_field(page, {"selector": "#cpf", "cases": [
                {"value": "123", "valid": False, "error_selector": "#cpf-error", "error_contains": "CPF inválido"},
            ]})


if __name__ == "__main__":
    unittest.main()

