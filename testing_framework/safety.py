"""Políticas que impedem execução ativa acidental contra alvos externos."""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


ACTIVE_SUITES = {"browser", "external_tools", "performance", "security"}


class SafetyError(RuntimeError):
    pass


@dataclass
class TargetClassification:
    host: str
    scope: str
    addresses: list[str]


def classify_target(base_url: str) -> TargetClassification:
    host = urlparse(base_url).hostname or ""
    if host.lower() == "localhost":
        return TargetClassification(host, "local", ["127.0.0.1"])
    addresses: list[str] = []
    try:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(host, None)})
    except socket.gaierror:
        return TargetClassification(host, "unresolved", [])
    scopes = []
    for address in addresses:
        ip = ipaddress.ip_address(address)
        scopes.append("local" if ip.is_loopback else "private" if ip.is_private else "external")
    scope = "external" if "external" in scopes else "private" if "private" in scopes else "local"
    return TargetClassification(host, scope, addresses)


def validate_execution(
    config: dict[str, Any], suites: list[str], authorized: bool, dry_run: bool
) -> TargetClassification:
    classification = classify_target(config["target"]["base_url"])
    if dry_run:
        return classification

    safety = config.get("safety", {})
    active = bool(ACTIVE_SUITES.intersection(suites)) or has_active_requests(config, suites)
    if classification.scope in {"external", "unresolved"} and not safety.get("allow_external_targets", False):
        raise SafetyError(
            "Alvo externo ou não resolvido bloqueado. Use um ambiente local/staging e configure "
            "safety.allow_external_targets somente com autorização formal."
        )
    if active and safety.get("require_authorization_for_active_tests", True) and not authorized:
        raise SafetyError("Testes ativos exigem a opção --authorized")

    max_users = int(safety.get("max_users", 50))
    max_duration = int(safety.get("max_duration_seconds", 300))
    performance = config.get("performance", {})
    numeric_checks = {
        "load_test.users": performance.get("load_test", {}).get("users", 0),
        "stress_test.max_users": performance.get("stress_test", {}).get("max_users", 0),
        "spike_test.spike_users": performance.get("spike_test", {}).get("spike_users", 0),
    }
    for name, value in numeric_checks.items():
        if value and int(value) > max_users:
            raise SafetyError(f"performance.{name}={value} excede safety.max_users={max_users}")
    duration_values = [
        performance.get("load_test", {}).get("duration", 0),
        performance.get("stress_test", {}).get("step_duration", 0),
        performance.get("spike_test", {}).get("spike_duration", 0),
    ]
    if any(value and int(value) > max_duration for value in duration_values):
        raise SafetyError(f"Uma duração excede safety.max_duration_seconds={max_duration}")
    return classification


def has_active_requests(config: dict[str, Any], suites: list[str]) -> bool:
    safe_methods = {"GET", "HEAD", "OPTIONS"}
    if "api" in suites:
        endpoints = config.get("api", {}).get("endpoints", config.get("target", {}).get("api_endpoints", []))
        for raw in endpoints:
            spec = {"path": raw} if isinstance(raw, str) else raw
            if str(spec.get("method", "GET")).upper() not in safe_methods or spec.get("concurrency"):
                return True
    if "business_rules" in suites:
        for rule in config.get("business_rules", {}).get("rules", []):
            if str(rule.get("method", "GET")).upper() not in safe_methods:
                return True
    return False
