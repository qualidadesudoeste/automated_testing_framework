"""Validadores e partições brasileiras para dados de teste."""

from __future__ import annotations

import re
from typing import Any


def digits(value: Any) -> str:
    return re.sub(r"\D", "", str(value))


def validate_cpf(value: Any) -> bool:
    number = digits(value)
    if len(number) != 11 or len(set(number)) == 1:
        return False
    for size in (9, 10):
        total = sum(int(number[index]) * (size + 1 - index) for index in range(size))
        check = (total * 10) % 11
        check = 0 if check == 10 else check
        if check != int(number[size]):
            return False
    return True


def validate_cnpj(value: Any) -> bool:
    number = digits(value)
    if len(number) != 14 or len(set(number)) == 1:
        return False
    for size, weights in ((12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]), (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])):
        remainder = sum(int(number[index]) * weights[index] for index in range(size)) % 11
        check = 0 if remainder < 2 else 11 - remainder
        if check != int(number[size]):
            return False
    return True


def profile_cases(profile: str) -> list[dict[str, Any]]:
    profiles = {
        "cpf": [
            {"value": "52998224725", "valid": True, "masked_pattern": r"\d{3}\.\d{3}\.\d{3}-\d{2}"},
            {"value": "52998224724", "valid": False},
            {"value": "00000000000", "valid": False},
            {"value": "123", "valid": False},
            {"value": "", "valid": False},
        ],
        "cnpj": [
            {"value": "11222333000181", "valid": True, "masked_pattern": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"},
            {"value": "11222333000180", "valid": False},
            {"value": "00000000000000", "valid": False},
            {"value": "123", "valid": False},
            {"value": "", "valid": False},
        ],
        "numeric": [
            {"value": "10", "valid": True},
            {"value": "0", "valid": False},
            {"value": "-1", "valid": False},
            {"value": "abc", "valid": False},
            {"value": "10@", "valid": False},
            {"value": "", "valid": False},
        ],
        "required": [
            {"value": "valor", "valid": True},
            {"value": "", "valid": False},
            {"value": "   ", "valid": False},
        ],
    }
    if profile not in profiles:
        raise ValueError(f"Perfil de campo desconhecido: {profile}")
    return profiles[profile]

