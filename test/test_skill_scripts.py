import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    REPO_ROOT / "software-testing" / "scripts" / "run_framework.py",
    REPO_ROOT / "qa-master-testing" / "scripts" / "run_framework.py",
]


class SkillLauncherPortabilityTests(unittest.TestCase):
    """Nenhum launcher de skill pode fixar cwd de volta no repositório do framework.

    Fazer isso forçaria toda execução de volta para este repo mesmo quando o chamador
    pretende testar um projeto-alvo diferente (ver Fase 1.2 da refatoração de
    portabilidade). Este teste é uma varredura textual do código-fonte, no mesmo
    espírito de test_prompt_integrity.py.
    """

    def test_launchers_never_pin_cwd_to_their_own_repository(self):
        forbidden = ("cwd=repository_root", "cwd=skill_root", "cwd=plugin_root")
        for script in SCRIPTS:
            self.assertTrue(script.is_file(), script)
            text = script.read_text(encoding="utf-8")
            for pattern in forbidden:
                self.assertNotIn(pattern, text, f"{script} não deve conter {pattern!r}")


if __name__ == "__main__":
    unittest.main()
