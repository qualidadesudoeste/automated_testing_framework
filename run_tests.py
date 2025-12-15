#!/usr/bin/env python3
"""
Script Principal do Framework de Testes Automatizados
Orquestra a execução de testes de performance e segurança
"""

import sys
import os
import yaml
import argparse
from datetime import datetime

# Adiciona diretórios ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'performance'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'security'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from performance_tester import PerformanceTester
from security_tester import SecurityTester
from report_generator import ReportGenerator


class TestFramework:
    """Classe principal do framework de testes"""
    
    def __init__(self, config_path: str):
        """Inicializa o framework com arquivo de configuração"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.report_generator = ReportGenerator(
            output_dir=self.config.get('reporting', {}).get('output_dir', './reports')
        )
    
    def run_performance_tests(self) -> dict:
        """Executa testes de performance"""
        print("\n" + "="*80)
        print("INICIANDO TESTES DE PERFORMANCE")
        print("="*80)
        
        tester = PerformanceTester(self.config)
        results = tester.run_all_tests()
        
        print("\n" + "="*80)
        print("TESTES DE PERFORMANCE CONCLUÍDOS")
        print("="*80)
        
        return results
    
    def run_security_tests(self) -> dict:
        """Executa testes de segurança"""
        print("\n" + "="*80)
        print("INICIANDO TESTES DE SEGURANÇA")
        print("="*80)
        
        tester = SecurityTester(self.config)
        results = tester.run_all_tests()
        
        print("\n" + "="*80)
        print("TESTES DE SEGURANÇA CONCLUÍDOS")
        print("="*80)
        print(f"\nScore de Segurança: {results.get('security_score', 0)}/100")
        print(f"Total de Vulnerabilidades: {results.get('total_issues', 0)}")
        
        issues = results.get('issues', {})
        if issues.get('critical'):
            print(f"  🔴 Críticas: {len(issues['critical'])}")
        if issues.get('high'):
            print(f"  🟠 Altas: {len(issues['high'])}")
        if issues.get('medium'):
            print(f"  🟡 Médias: {len(issues['medium'])}")
        if issues.get('low'):
            print(f"  🔵 Baixas: {len(issues['low'])}")
        if issues.get('info'):
            print(f"  ℹ️  Informativas: {len(issues['info'])}")
        
        return results
    
    def run_all_tests(self) -> dict:
        """Executa todos os testes (performance e segurança)"""
        results = {
            'test_suite': 'complete',
            'target': self.config.get('target', {}),
            'start_time': datetime.now().isoformat()
        }
        
        # Testes de Performance
        if self.config.get('performance', {}).get('enabled', True):
            results['performance'] = self.run_performance_tests()
        
        # Testes de Segurança
        if self.config.get('security', {}).get('enabled', True):
            results['security'] = self.run_security_tests()
        
        results['end_time'] = datetime.now().isoformat()
        
        return results
    
    def generate_reports(self, results: dict):
        """Gera relatórios nos formatos configurados"""
        print("\n" + "="*80)
        print("GERANDO RELATÓRIOS")
        print("="*80)
        
        formats = self.config.get('reporting', {}).get('formats', ['html', 'json'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        generated_files = []
        
        # Relatório JSON
        if 'json' in formats:
            json_file = self.report_generator.generate_json_report(
                results,
                filename=f'report_{timestamp}.json'
            )
            generated_files.append(json_file)
            print(f"✓ Relatório JSON: {json_file}")
        
        # Relatório HTML
        if 'html' in formats:
            html_file = self.report_generator.generate_html_report(
                results,
                filename=f'report_{timestamp}.html'
            )
            generated_files.append(html_file)
            print(f"✓ Relatório HTML: {html_file}")
        
        # Relatório Texto
        if 'text' in formats:
            text_file = self.report_generator.generate_text_report(
                results,
                filename=f'report_{timestamp}.txt'
            )
            generated_files.append(text_file)
            print(f"✓ Relatório TXT: {text_file}")
        
        return generated_files


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Framework de Testes Automatizados de Performance e Segurança',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Executar todos os testes
  python run_tests.py -c config/config.yaml
  
  # Executar apenas testes de performance
  python run_tests.py -c config/config.yaml --performance-only
  
  # Executar apenas testes de segurança
  python run_tests.py -c config/config.yaml --security-only
  
  # Executar sem gerar relatórios
  python run_tests.py -c config/config.yaml --no-report
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='Caminho para o arquivo de configuração (padrão: config/config.yaml)'
    )
    
    parser.add_argument(
        '--performance-only',
        action='store_true',
        help='Executar apenas testes de performance'
    )
    
    parser.add_argument(
        '--security-only',
        action='store_true',
        help='Executar apenas testes de segurança'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Não gerar relatórios'
    )
    
    args = parser.parse_args()
    
    # Verifica se arquivo de configuração existe
    if not os.path.exists(args.config):
        print(f"❌ Erro: Arquivo de configuração não encontrado: {args.config}")
        sys.exit(1)
    
    try:
        # Inicializa framework
        framework = TestFramework(args.config)
        
        # Executa testes
        if args.performance_only:
            results = framework.run_performance_tests()
        elif args.security_only:
            results = framework.run_security_tests()
        else:
            results = framework.run_all_tests()
        
        # Gera relatórios
        if not args.no_report:
            framework.generate_reports(results)
        
        print("\n" + "="*80)
        print("EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
