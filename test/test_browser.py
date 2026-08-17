import importlib.util
import unittest
from pathlib import Path

from testing_framework.testers.browser import axe_severity, compare_images, safe_name


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


if __name__ == "__main__":
    unittest.main()

