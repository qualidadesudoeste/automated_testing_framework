import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "qa-master-testing" / "skills" / "qa-master" / "references"


class PromptIntegrityTests(unittest.TestCase):
    def test_master_reference_preserves_all_dimensions_and_controls(self):
        text = (REFERENCES / "prompt-qa-master-complete.md").read_text(encoding="utf-8")
        dimensions = set(re.findall(r"^### D(\d+)\s", text, re.MULTILINE))
        self.assertEqual(dimensions, {str(index) for index in range(1, 26)})
        for phrase in ("MODO SELECIONADO", "Toda correção sugerida vem com código", "TESTES ADVERSARIAIS", "SMOKE DE 10 MINUTOS"):
            self.assertIn(phrase, text)

    def test_business_reference_preserves_taxonomy_modes_limits_and_outputs(self):
        text = (REFERENCES / "prompt-qa-business-complete.md").read_text(encoding="utf-8")
        for phrase in (
            "RÁPIDO", "PADRÃO", "PROFUNDO", "40 leituras", "12 achados",
            "mais de 30 achados", "AUDITORIA_NEGOCIO.md", "ACHADOS_NEGOCIO.csv",
            "PENDENCIAS_NEGOCIO.md", "MAPA_SISTEMA.md",
        ):
            self.assertIn(phrase, text)
        expected = {f"{group}{index:02d}" for group, maximum in {"A": 9, "B": 9, "C": 6, "D": 7, "E": 7, "F": 6, "G": 6, "H": 6}.items() for index in range(1, maximum + 1)}
        self.assertTrue(expected.issubset(set(re.findall(r"\b[A-H]\d{2}\b", text))))

    def test_normative_references_are_platform_neutral(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in REFERENCES.glob("prompt-qa-*-complete.md"))
        forbidden = [
            bytes.fromhex(value).decode("utf-8")
            for value in ("636c61756465", "636f646578", "6f70656e6169", "63686174677074")
        ]
        self.assertIsNone(re.search("|".join(map(re.escape, forbidden)), combined, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
