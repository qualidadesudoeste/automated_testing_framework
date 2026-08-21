#!/usr/bin/env python3
"""CLI segura do framework completo de testes de software."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from testing_framework.config import load_config, selected_suites
from testing_framework.orchestrator import Orchestrator
from testing_framework.reporting import UnifiedReporter
from testing_framework.safety import SafetyError, validate_execution


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Framework automatizado de testes funcionais, regras, API, UI/UX, performance e segurança"
    )
    parser.add_argument("-c", "--config", default="config/config.yaml", help="Arquivo YAML de configuração")
    parser.add_argument(
        "--suite",
        action="append",
        choices=["api", "openapi", "business_rules", "web_quality", "browser", "project_quality", "external_tools", "performance", "security", "access_control"],
        help="Executar somente uma suíte; repetir a opção para combinar suítes",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validar e mostrar o plano sem acessar o alvo")
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="Confirmar que há autorização para testes ativos no alvo configurado",
    )
    parser.add_argument("--no-report", action="store_true", help="Não gravar relatórios")
    parser.add_argument("--output", help="Sobrescrever o diretório de relatórios")
    parser.add_argument("--list-suites", action="store_true", help="Listar suítes disponíveis e sair")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.list_suites:
        print("api\nopenapi\nbusiness_rules\nweb_quality\nbrowser\nproject_quality\nexternal_tools\nperformance\nsecurity\naccess_control")
        return 0
    try:
        config = load_config(args.config)
        suites = selected_suites(config, args.suite)
        target = validate_execution(config, suites, args.authorized, args.dry_run)
    except SafetyError as exc:
        print(f"BLOQUEADO POR SEGURANÇA: {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as exc:
        print(f"CONFIGURAÇÃO INVÁLIDA: {exc}", file=sys.stderr)
        return 1

    plan = {
        "target": config["target"].get("base_url"),
        "classification": target.scope,
        "addresses": target.addresses,
        "suites": suites,
        "active_authorized": args.authorized,
        "dry_run": args.dry_run,
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0
    if not suites:
        print("Nenhuma suíte habilitada.", file=sys.stderr)
        return 1

    report = Orchestrator(config, classification=target).run(suites)
    generated: list[str] = []
    if not args.no_report:
        reporting = config.get("reporting", {})
        output_dir = args.output or reporting.get("output_dir", "./reports")
        if reporting.get("output_dir_base", "cwd") == "config" and not Path(output_dir).is_absolute():
            output_dir = str(Path(config["_config_path"]).parent / output_dir)
        reporter = UnifiedReporter(output_dir)
        generated = reporter.generate(report, reporting.get("formats", ["html", "json"]))

    summary = report.to_dict()["summary"]
    print(f"Suítes: {summary['suites']} | Achados: {summary['findings']}")
    print(f"Quality gate: {'APROVADO' if report.quality_gate['passed'] else 'REPROVADO'}")
    for path in generated:
        print(f"Relatório: {path}")
    return 0 if report.quality_gate["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
