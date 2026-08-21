"""Validação de contratos OpenAPI e smoke tests seguros de operações GET."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from ..http import assert_same_origin_response, create_session, target_url
from ..models import Finding, SuiteResult


class OpenApiTester:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.openapi_config = config.get("openapi", {})
        self.timeout = config.get("general", {}).get("timeout", 15)
        self.session = create_session(config, self.openapi_config.get("headers", {}))

    def run(self) -> SuiteResult:
        result = SuiteResult("openapi")
        spec_path = self._spec_path()
        if not spec_path:
            result.skipped_reason = "Nenhum arquivo OpenAPI configurado"
            return result.finish()
        try:
            spec = self._load(spec_path)
            self._validate_root(spec)
        except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
            result.findings.append(Finding("api-contract", "Especificação OpenAPI inválida", str(exc), "high", "high", location=str(spec_path)))
            return result.finish()

        operations = 0
        for path, path_item in spec.get("paths", {}).items():
            if not isinstance(path_item, dict) or "get" not in path_item:
                continue
            operation = path_item["get"] or {}
            if "{" in path:
                continue
            operations += 1
            self._test_get(spec, path, operation, result)
        result.metrics.update({"spec": str(spec_path), "get_operations_tested": operations})
        return result.finish()

    def _spec_path(self) -> Path | None:
        raw = self.openapi_config.get("spec")
        if not raw:
            return None
        path = Path(str(raw))
        if not path.is_absolute():
            config_path = Path(self.config.get("_config_path", ".")).resolve()
            path = config_path.parent / path
        return path.resolve()

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("A raiz da especificação deve ser um objeto")
        return data

    @staticmethod
    def _validate_root(spec: dict[str, Any]) -> None:
        if not str(spec.get("openapi", "")).startswith("3."):
            raise ValueError("Somente OpenAPI 3.x é suportado")
        if not isinstance(spec.get("paths"), dict):
            raise ValueError("O campo paths é obrigatório")

    def _test_get(self, spec: dict[str, Any], path: str, operation: dict[str, Any], result: SuiteResult) -> None:
        try:
            url = target_url(self.config["target"]["base_url"], path)
            response = self.session.get(url, timeout=self.timeout)
            assert_same_origin_response(self.config["target"]["base_url"], response)
        except Exception as exc:
            result.findings.append(Finding("api-contract", f"Operação GET falhou: {path}", "Não foi possível executar o smoke test do contrato.", "high", "high", location=path, observed=str(exc)))
            return
        responses = operation.get("responses", {})
        declared = {int(code) for code in responses if str(code).isdigit()}
        if declared and response.status_code not in declared:
            result.findings.append(Finding(
                "api-contract", f"Status não declarado no OpenAPI: GET {path}",
                "A implementação retornou um status ausente do contrato.", "high", "high",
                location=url, expected=str(sorted(declared)), observed=str(response.status_code),
            ))
            return
        response_spec = responses.get(str(response.status_code), responses.get("default", {}))
        content = response_spec.get("content", {}) if isinstance(response_spec, dict) else {}
        media = content.get("application/json") or next((value for key, value in content.items() if "json" in key), None)
        schema = media.get("schema") if isinstance(media, dict) else None
        if not schema:
            return
        try:
            payload = response.json()
        except ValueError:
            result.findings.append(Finding("api-contract", f"JSON inválido em GET {path}", "O contrato declara JSON, mas a resposta não pôde ser decodificada.", "high", "high", location=url, evidence=response.text[:500]))
            return
        errors = validate_schema(payload, resolve_ref(spec, schema), spec, "$")
        if errors:
            result.findings.append(Finding(
                "api-contract", f"Schema OpenAPI violado em GET {path}",
                "A resposta não atende ao schema declarado.", "high", "high",
                location=url, evidence="; ".join(errors[:20]), reference="OpenAPI 3.x",
            ))


def resolve_ref(spec: dict[str, Any], schema: Any) -> Any:
    if not isinstance(schema, dict) or "$ref" not in schema:
        return schema
    ref = schema["$ref"]
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise ValueError(f"Referência externa não suportada: {ref}")
    current: Any = spec
    for part in ref[2:].split("/"):
        current = current[part.replace("~1", "/").replace("~0", "~")]
    return current


def validate_schema(value: Any, schema: Any, spec: dict[str, Any], path: str) -> list[str]:
    schema = resolve_ref(spec, schema)
    if not isinstance(schema, dict):
        return []
    errors: list[str] = []
    expected_type = schema.get("type")
    type_map = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool, "null": type(None)}
    if expected_type in type_map and (not isinstance(value, type_map[expected_type]) or expected_type == "integer" and isinstance(value, bool)):
        return [f"{path}: esperado {expected_type}, obtido {type(value).__name__}"]
    if isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                errors.append(f"{path}.{name}: campo obrigatório ausente")
        for name, child in schema.get("properties", {}).items():
            if name in value:
                errors.extend(validate_schema(value[name], child, spec, f"{path}.{name}"))
    elif isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            errors.extend(validate_schema(item, schema["items"], spec, f"{path}[{index}]"))
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: valor {value!r} fora do enum")
    return errors

