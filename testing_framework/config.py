"""Carregamento e validação da configuração YAML."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


DEFAULTS: dict[str, Any] = {
    "general": {"timeout": 15, "retry_attempts": 0, "max_workers": 10},
    "safety": {
        "allow_external_targets": False,
        "require_authorization_for_active_tests": True,
        "max_users": 50,
        "max_duration_seconds": 300,
        "max_requests_per_probe": 50,
    },
    "quality_gate": {"fail_on": ["critical", "high"]},
    "reporting": {"output_dir": "./reports", "output_dir_base": "cwd", "formats": ["html", "json", "junit", "sarif"]},
}


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.is_file():
        raise ValueError(f"Arquivo de configuração não encontrado: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    if not isinstance(raw, dict):
        raise ValueError("A raiz da configuração deve ser um objeto YAML")
    config = _merge(DEFAULTS, raw)
    validate_config(config)
    config["_config_path"] = str(config_path.resolve())
    return config


def validate_config(config: dict[str, Any]) -> None:
    target = config.get("target")
    if not isinstance(target, dict):
        raise ValueError("A seção target é obrigatória")
    base_url = target.get("base_url", "")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("target.base_url deve ser uma URL HTTP(S) válida")
    if parsed.username or parsed.password:
        raise ValueError("target.base_url não pode conter credenciais")

    for section in ("api", "openapi", "business_rules", "web_quality", "browser", "project_quality", "external_tools", "performance", "security", "access_control"):
        if section in config and not isinstance(config[section], dict):
            raise ValueError(f"A seção {section} deve ser um objeto")

    timeout = config["general"].get("timeout", 15)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("general.timeout deve ser positivo")

    formats = config["reporting"].get("formats", [])
    unsupported = set(formats) - {"html", "json", "junit", "sarif", "text"}
    if unsupported:
        raise ValueError(f"Formatos de relatório inválidos: {sorted(unsupported)}")

    output_dir_base = config["reporting"].get("output_dir_base", "cwd")
    if output_dir_base not in {"cwd", "config"}:
        raise ValueError("reporting.output_dir_base deve ser 'cwd' ou 'config'")

    max_requests_per_probe = config["safety"].get("max_requests_per_probe", 50)
    if not isinstance(max_requests_per_probe, int) or isinstance(max_requests_per_probe, bool) or max_requests_per_probe <= 0:
        raise ValueError("safety.max_requests_per_probe deve ser um inteiro positivo")

    project_quality = config.get("project_quality", {})
    provenance_severity = str(project_quality.get("ai_authorship_severity", "low")).lower()
    if provenance_severity not in {"critical", "high", "medium", "low", "info"}:
        raise ValueError("project_quality.ai_authorship_severity possui valor inválido")
    for key in ("ai_authorship_max_file_bytes", "ai_authorship_max_findings"):
        value = project_quality.get(key)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
            raise ValueError(f"project_quality.{key} deve ser um inteiro positivo")
    for key in ("ai_authorship_exclude", "ai_authorship_allowlist"):
        value = project_quality.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"project_quality.{key} deve ser uma lista de caminhos")


def selected_suites(config: dict[str, Any], requested: list[str] | None = None) -> list[str]:
    known = ["api", "openapi", "business_rules", "web_quality", "browser", "project_quality", "external_tools", "performance", "security", "access_control"]
    if requested:
        invalid = set(requested) - set(known)
        if invalid:
            raise ValueError(f"Suítes desconhecidas: {sorted(invalid)}")
        return requested
    return [name for name in known if config.get(name, {}).get("enabled", False)]
