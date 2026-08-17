import unittest

from testing_framework.validators import profile_cases, validate_cnpj, validate_cpf


class BrazilianValidatorTests(unittest.TestCase):
    def test_validates_cpf(self):
        self.assertTrue(validate_cpf("529.982.247-25"))
        self.assertFalse(validate_cpf("529.982.247-24"))
        self.assertFalse(validate_cpf("000.000.000-00"))

    def test_validates_cnpj(self):
        self.assertTrue(validate_cnpj("11.222.333/0001-81"))
        self.assertFalse(validate_cnpj("11.222.333/0001-80"))

    def test_profiles_include_boundaries(self):
        cpf = profile_cases("cpf")
        self.assertTrue(any(case["valid"] for case in cpf))
        self.assertTrue(any(not case["valid"] for case in cpf))
        self.assertTrue(any(case["value"] == "" for case in cpf))


if __name__ == "__main__":
    unittest.main()

