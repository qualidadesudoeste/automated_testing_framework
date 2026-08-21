import ast
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    REPO_ROOT / "security" / "security_tester.py",
    REPO_ROOT / "performance" / "performance_tester.py",
]


def has_main_guard(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
        ):
            return True
    return False


class NoDirectExecutionBypassTests(unittest.TestCase):
    """security_tester.py e performance_tester.py não podem expor um bloco
    `if __name__ == "__main__"`: isso permitia rodar o módulo direto, ignorando
    totalmente `testing_framework.safety.validate_execution()`/--authorized."""

    def test_modules_have_no_standalone_entrypoint(self):
        for module_path in MODULES:
            self.assertTrue(module_path.is_file(), module_path)
            tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
            self.assertFalse(has_main_guard(tree), f"{module_path} não deve ter bloco __main__")


if __name__ == "__main__":
    unittest.main()
