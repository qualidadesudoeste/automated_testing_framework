#!/usr/bin/env python3
"""
Módulo de Testes de Segurança
Realiza testes de vulnerabilidades web, autenticação, injeção e análise de rede
"""

import re
import ssl
import socket
import requests
import urllib.parse
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib


@dataclass
class SecurityIssue:
    """Representa uma vulnerabilidade ou problema de segurança encontrado"""
    severity: str  # critical, high, medium, low, info
    category: str
    title: str
    description: str
    url: str = None
    evidence: str = None
    recommendation: str = None
    cwe_id: str = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'severity': self.severity,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'evidence': self.evidence,
            'recommendation': self.recommendation,
            'cwe_id': self.cwe_id,
            'timestamp': self.timestamp.isoformat()
        }


class SecurityTester:
    """Classe principal para testes de segurança"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target = config.get('target', {})
        self.sec_config = config.get('security', {})
        self.timeout = config.get('general', {}).get('timeout', 30)
        self.session = requests.Session()
        self.issues: List[SecurityIssue] = []
        
        # Payloads para testes de injeção
        self.sql_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin' --",
            "1' UNION SELECT NULL--",
            "' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055'",
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "'\"><script>alert(String.fromCharCode(88,83,83))</script>",
        ]
        
        self.command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "& dir",
            "`id`",
            "$(whoami)",
            "; cat /etc/passwd",
        ]
        
        self.nosql_payloads = [
            "{'$gt': ''}",
            "{'$ne': null}",
            "{'$regex': '.*'}",
            "admin' || '1'=='1",
        ]
    
    def _add_issue(self, issue: SecurityIssue):
        """Adiciona uma vulnerabilidade à lista"""
        self.issues.append(issue)
        severity_emoji = {
            'critical': '[CRITICAL]',
            'high': '[HIGH]',
            'medium': '[MEDIUM]',
            'low': '[LOW]',
            'info': '[INFO]'
        }
        print(f"  {severity_emoji.get(issue.severity, '[ISSUE]')} {issue.title}")
    
    def test_sql_injection(self) -> List[SecurityIssue]:
        """Testa vulnerabilidades de SQL Injection"""
        print("\n[SECURITY] Testando SQL Injection...")
        
        endpoints = self.target.get('api_endpoints', []) + self.target.get('web_endpoints', [])
        base_url = self.target['base_url']
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            
            # Testa em parâmetros GET
            for payload in self.sql_payloads:
                test_url = f"{url}?id={urllib.parse.quote(payload)}"
                
                try:
                    response = self.session.get(test_url, timeout=self.timeout)
                    
                    # Procura por indicadores de SQL injection
                    sql_errors = [
                        'sql syntax',
                        'mysql_fetch',
                        'postgresql',
                        'ora-',
                        'sqlite',
                        'syntax error',
                        'unclosed quotation',
                        'quoted string not properly terminated'
                    ]
                    
                    response_lower = response.text.lower()
                    for error in sql_errors:
                        if error in response_lower:
                            self._add_issue(SecurityIssue(
                                severity='critical',
                                category='injection',
                                title='Possível SQL Injection',
                                description=f'O endpoint pode ser vulnerável a SQL Injection. '
                                          f'Erro de banco de dados detectado na resposta.',
                                url=test_url,
                                evidence=f'Payload: {payload}, Error pattern: {error}',
                                recommendation='Utilize prepared statements ou ORM para prevenir SQL injection. '
                                             'Valide e sanitize todas as entradas do usuário.',
                                cwe_id='CWE-89'
                            ))
                            break
                
                except Exception as e:
                    pass  # Ignora erros de conexão
        
        return self.issues
    
    def test_xss(self) -> List[SecurityIssue]:
        """Testa vulnerabilidades de Cross-Site Scripting (XSS)"""
        print("\n[SECURITY] Testando XSS (Cross-Site Scripting)...")
        
        endpoints = self.target.get('web_endpoints', [])
        base_url = self.target['base_url']
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            
            for payload in self.xss_payloads:
                # Testa em parâmetros GET
                test_url = f"{url}?q={urllib.parse.quote(payload)}"
                
                try:
                    response = self.session.get(test_url, timeout=self.timeout)
                    
                    # Verifica se o payload foi refletido sem sanitização
                    if payload in response.text or payload.replace('"', '&quot;') in response.text:
                        self._add_issue(SecurityIssue(
                            severity='high',
                            category='injection',
                            title='Possível XSS Refletido',
                            description='O endpoint pode refletir entrada do usuário sem sanitização adequada.',
                            url=test_url,
                            evidence=f'Payload refletido: {payload}',
                            recommendation='Encode todas as saídas HTML. Use Content Security Policy (CSP). '
                                         'Valide e sanitize entradas do usuário.',
                            cwe_id='CWE-79'
                        ))
                        break
                
                except Exception as e:
                    pass
        
        return self.issues
    
    def test_security_headers(self) -> List[SecurityIssue]:
        """Verifica presença de headers de segurança importantes"""
        print("\n[SECURITY] Verificando Headers de Segurança...")
        
        url = self.target['base_url']
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            headers = response.headers
            
            # Headers de segurança recomendados
            security_headers = {
                'X-Frame-Options': {
                    'severity': 'medium',
                    'description': 'Protege contra clickjacking',
                    'recommendation': 'Adicione header: X-Frame-Options: DENY ou SAMEORIGIN'
                },
                'X-Content-Type-Options': {
                    'severity': 'low',
                    'description': 'Previne MIME type sniffing',
                    'recommendation': 'Adicione header: X-Content-Type-Options: nosniff'
                },
                'Strict-Transport-Security': {
                    'severity': 'high',
                    'description': 'Força uso de HTTPS',
                    'recommendation': 'Adicione header: Strict-Transport-Security: max-age=31536000; includeSubDomains'
                },
                'Content-Security-Policy': {
                    'severity': 'medium',
                    'description': 'Previne XSS e injeção de conteúdo',
                    'recommendation': 'Adicione header: Content-Security-Policy com política apropriada'
                },
                'X-XSS-Protection': {
                    'severity': 'low',
                    'description': 'Ativa proteção XSS do navegador',
                    'recommendation': 'Adicione header: X-XSS-Protection: 1; mode=block'
                },
                'Referrer-Policy': {
                    'severity': 'low',
                    'description': 'Controla informações de referrer',
                    'recommendation': 'Adicione header: Referrer-Policy: no-referrer ou strict-origin-when-cross-origin'
                },
                'Permissions-Policy': {
                    'severity': 'low',
                    'description': 'Controla recursos do navegador',
                    'recommendation': 'Adicione header: Permissions-Policy com política apropriada'
                }
            }
            
            for header, info in security_headers.items():
                if header not in headers:
                    self._add_issue(SecurityIssue(
                        severity=info['severity'],
                        category='configuration',
                        title=f'Header de Segurança Ausente: {header}',
                        description=info['description'],
                        url=url,
                        recommendation=info['recommendation'],
                        cwe_id='CWE-693'
                    ))
            
            # Verifica headers que expõem informações sensíveis
            sensitive_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in sensitive_headers:
                if header in headers:
                    self._add_issue(SecurityIssue(
                        severity='info',
                        category='information_disclosure',
                        title=f'Header Expõe Informações: {header}',
                        description=f'O header {header} expõe informações sobre a tecnologia do servidor.',
                        url=url,
                        evidence=f'{header}: {headers[header]}',
                        recommendation=f'Remova ou oculte o header {header}',
                        cwe_id='CWE-200'
                    ))
        
        except Exception as e:
            print(f"  Erro ao verificar headers: {e}")
        
        return self.issues
    
    def test_ssl_tls(self) -> List[SecurityIssue]:
        """Verifica configuração SSL/TLS"""
        print("\n[SECURITY] Verificando SSL/TLS...")
        
        url = self.target['base_url']
        
        # Verifica se usa HTTPS
        if not url.startswith('https://'):
            self._add_issue(SecurityIssue(
                severity='high',
                category='transport_security',
                title='HTTPS Não Utilizado',
                description='O sistema não utiliza HTTPS, expondo dados em texto claro.',
                url=url,
                recommendation='Configure certificado SSL/TLS e force redirecionamento para HTTPS',
                cwe_id='CWE-319'
            ))
            return self.issues
        
        # Extrai hostname e porta
        hostname = url.replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]
        port = 443
        
        if ':' in url.replace('https://', '').replace('http://', '').split('/')[0]:
            port = int(url.replace('https://', '').replace('http://', '').split('/')[0].split(':')[1])
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    # Verifica versão do protocolo
                    if version in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                        self._add_issue(SecurityIssue(
                            severity='high',
                            category='transport_security',
                            title='Protocolo SSL/TLS Inseguro',
                            description=f'O servidor suporta protocolo inseguro: {version}',
                            url=url,
                            evidence=f'Versão: {version}',
                            recommendation='Desabilite protocolos antigos e use apenas TLSv1.2 ou TLSv1.3',
                            cwe_id='CWE-326'
                        ))
                    
                    # Verifica cifras fracas
                    weak_ciphers = ['DES', 'RC4', 'MD5', 'NULL', 'EXPORT', 'anon']
                    cipher_name = cipher[0] if cipher else ''
                    
                    for weak in weak_ciphers:
                        if weak in cipher_name.upper():
                            self._add_issue(SecurityIssue(
                                severity='high',
                                category='transport_security',
                                title='Cifra SSL/TLS Fraca',
                                description=f'O servidor utiliza cifra fraca: {cipher_name}',
                                url=url,
                                evidence=f'Cipher: {cipher_name}',
                                recommendation='Configure apenas cifras fortes (AES-GCM, ChaCha20)',
                                cwe_id='CWE-327'
                            ))
                            break
        
        except Exception as e:
            print(f"  Aviso: Não foi possível verificar SSL/TLS completamente: {e}")
        
        return self.issues
    
    def test_cors(self) -> List[SecurityIssue]:
        """Verifica configuração de CORS"""
        print("\n[SECURITY] Verificando CORS (Cross-Origin Resource Sharing)...")
        
        url = self.target['base_url']
        
        try:
            # Testa com origem maliciosa
            headers = {'Origin': 'https://evil.com'}
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if 'Access-Control-Allow-Origin' in response.headers:
                allowed_origin = response.headers['Access-Control-Allow-Origin']
                
                if allowed_origin == '*':
                    self._add_issue(SecurityIssue(
                        severity='medium',
                        category='configuration',
                        title='CORS Configurado com Wildcard',
                        description='O servidor permite requisições de qualquer origem (*).',
                        url=url,
                        evidence=f'Access-Control-Allow-Origin: {allowed_origin}',
                        recommendation='Restrinja CORS apenas para origens confiáveis específicas',
                        cwe_id='CWE-942'
                    ))
                
                elif allowed_origin == 'https://evil.com':
                    self._add_issue(SecurityIssue(
                        severity='high',
                        category='configuration',
                        title='CORS Reflete Origem Não Confiável',
                        description='O servidor reflete a origem da requisição sem validação.',
                        url=url,
                        evidence=f'Origin enviada: https://evil.com, Permitida: {allowed_origin}',
                        recommendation='Valide origens contra uma whitelist de domínios confiáveis',
                        cwe_id='CWE-942'
                    ))
        
        except Exception as e:
            pass
        
        return self.issues
    
    def test_command_injection(self) -> List[SecurityIssue]:
        """Testa vulnerabilidades de Command Injection"""
        print("\n[SECURITY] Testando Command Injection...")
        
        endpoints = self.target.get('api_endpoints', [])
        base_url = self.target['base_url']
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            
            for payload in self.command_injection_payloads:
                test_url = f"{url}?cmd={urllib.parse.quote(payload)}"
                
                try:
                    response = self.session.get(test_url, timeout=self.timeout)
                    
                    # Procura por indicadores de execução de comando
                    indicators = [
                        'root:',
                        'bin/bash',
                        'uid=',
                        'gid=',
                        'groups=',
                        'volume serial number',
                        'directory of'
                    ]
                    
                    response_lower = response.text.lower()
                    for indicator in indicators:
                        if indicator in response_lower:
                            self._add_issue(SecurityIssue(
                                severity='critical',
                                category='injection',
                                title='Possível Command Injection',
                                description='O endpoint pode ser vulnerável a injeção de comandos do sistema.',
                                url=test_url,
                                evidence=f'Payload: {payload}, Indicator: {indicator}',
                                recommendation='Nunca execute comandos do sistema com entrada do usuário. '
                                             'Use APIs seguras ao invés de shell commands.',
                                cwe_id='CWE-78'
                            ))
                            break
                
                except Exception as e:
                    pass
        
        return self.issues
    
    def test_authentication(self) -> List[SecurityIssue]:
        """Testa vulnerabilidades de autenticação"""
        print("\n[SECURITY] Testando Autenticação...")
        
        base_url = self.target['base_url']
        
        # Testa senhas fracas comuns
        weak_passwords = ['password', '123456', 'admin', 'root', 'test', '']
        common_users = ['admin', 'administrator', 'root', 'user', 'test']
        
        login_endpoints = ['/login', '/api/login', '/auth/login', '/signin']
        
        for endpoint in login_endpoints:
            url = f"{base_url}{endpoint}"
            
            try:
                # Verifica se endpoint existe
                response = self.session.get(url, timeout=self.timeout)
                
                if response.status_code == 404:
                    continue
                
                # Testa algumas combinações de usuário/senha fraca
                for user in common_users[:2]:  # Limita para não fazer muitas requisições
                    for password in weak_passwords[:2]:
                        try:
                            login_response = self.session.post(
                                url,
                                json={'username': user, 'password': password},
                                timeout=self.timeout
                            )
                            
                            if login_response.status_code == 200:
                                self._add_issue(SecurityIssue(
                                    severity='critical',
                                    category='authentication',
                                    title='Credenciais Fracas Aceitas',
                                    description=f'O sistema aceita credenciais fracas: {user}/{password}',
                                    url=url,
                                    evidence=f'Login bem-sucedido com {user}/{password}',
                                    recommendation='Implemente política de senhas fortes. '
                                                 'Force alteração de senhas padrão.',
                                    cwe_id='CWE-521'
                                ))
                        
                        except Exception:
                            pass
            
            except Exception:
                pass
        
        return self.issues
    
    def test_rate_limiting(self) -> List[SecurityIssue]:
        """Testa se há rate limiting implementado"""
        print("\n[SECURITY] Testando Rate Limiting...")
        
        url = f"{self.target['base_url']}"
        if self.target.get('api_endpoints'):
            url = f"{self.target['base_url']}{self.target['api_endpoints'][0]}"
        
        try:
            # Faz múltiplas requisições rápidas
            responses = []
            for i in range(50):
                response = self.session.get(url, timeout=self.timeout)
                responses.append(response.status_code)
            
            # Verifica se alguma foi bloqueada (429 Too Many Requests)
            if 429 not in responses:
                self._add_issue(SecurityIssue(
                    severity='medium',
                    category='configuration',
                    title='Rate Limiting Não Detectado',
                    description='O sistema não parece implementar rate limiting, '
                              'permitindo potenciais ataques de força bruta ou DDoS.',
                    url=url,
                    evidence=f'50 requisições realizadas sem bloqueio',
                    recommendation='Implemente rate limiting para prevenir abuso. '
                                 'Use ferramentas como nginx rate limiting ou bibliotecas específicas.',
                    cwe_id='CWE-770'
                ))
        
        except Exception as e:
            print(f"  Erro ao testar rate limiting: {e}")
        
        return self.issues
    
    def scan_ports(self) -> List[SecurityIssue]:
        """Realiza scan básico de portas"""
        print("\n[SECURITY] Realizando Scan de Portas...")
        
        hostname = self.target['base_url'].replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]
        ports = self.sec_config.get('network_scan', {}).get('ports', [80, 443])
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((hostname, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    print(f"  [OK] Porta {port} está aberta")
            
            except Exception:
                pass
        
        # Verifica portas potencialmente inseguras
        risky_ports = {
            21: 'FTP (não criptografado)',
            23: 'Telnet (não criptografado)',
            3306: 'MySQL (não deve ser exposto)',
            5432: 'PostgreSQL (não deve ser exposto)',
            6379: 'Redis (não deve ser exposto)',
            27017: 'MongoDB (não deve ser exposto)'
        }
        
        for port in open_ports:
            if port in risky_ports:
                self._add_issue(SecurityIssue(
                    severity='high',
                    category='network',
                    title=f'Porta Potencialmente Insegura Aberta: {port}',
                    description=f'A porta {port} está aberta: {risky_ports[port]}',
                    evidence=f'Porta {port} acessível externamente',
                    recommendation='Feche portas desnecessárias ou restrinja acesso via firewall',
                    cwe_id='CWE-16'
                ))
        
        return self.issues
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de segurança habilitados"""
        results = {
            'test_suite': 'security',
            'target': self.target,
            'start_time': datetime.now().isoformat(),
            'tests_executed': []
        }
        
        web_vuln_config = self.sec_config.get('web_vulnerabilities', {})
        if web_vuln_config.get('enabled', True):
            tests = web_vuln_config.get('tests', [])
            
            if 'sql_injection' in tests:
                self.test_sql_injection()
                results['tests_executed'].append('sql_injection')
            
            if 'xss' in tests:
                self.test_xss()
                results['tests_executed'].append('xss')
            
            if 'security_headers' in tests:
                self.test_security_headers()
                results['tests_executed'].append('security_headers')
            
            if 'ssl_tls' in tests:
                self.test_ssl_tls()
                results['tests_executed'].append('ssl_tls')
            
            if 'cors' in tests:
                self.test_cors()
                results['tests_executed'].append('cors')
        
        injection_config = self.sec_config.get('injection_tests', {})
        if injection_config.get('enabled', False):
            if 'command_injection' in injection_config.get('types', []):
                self.test_command_injection()
                results['tests_executed'].append('command_injection')
        
        auth_config = self.sec_config.get('auth_tests', {})
        if auth_config.get('enabled', False):
            tests = auth_config.get('tests', [])
            
            if 'weak_passwords' in tests:
                self.test_authentication()
                results['tests_executed'].append('authentication')
            
            if 'rate_limiting' in tests:
                self.test_rate_limiting()
                results['tests_executed'].append('rate_limiting')
        
        network_config = self.sec_config.get('network_scan', {})
        if network_config.get('enabled', False):
            self.scan_ports()
            results['tests_executed'].append('port_scan')
        
        # Organiza issues por severidade
        issues_by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        for issue in self.issues:
            issues_by_severity[issue.severity].append(issue.to_dict())
        
        results['issues'] = issues_by_severity
        results['total_issues'] = len(self.issues)
        results['end_time'] = datetime.now().isoformat()
        
        # Calcula score de segurança
        severity_weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1, 'info': 0}
        total_score = sum(severity_weights[issue.severity] for issue in self.issues)
        max_score = 100
        security_score = max(0, max_score - total_score)
        
        results['security_score'] = security_score
        
        return results


if __name__ == '__main__':
    # Exemplo de uso standalone
    import yaml
    
    with open('../config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tester = SecurityTester(config)
    results = tester.run_all_tests()
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES DE SEGURANÇA")
    print("="*60)
    print(f"Score de Segurança: {results['security_score']}/100")
    print(f"\nTotal de Issues: {results['total_issues']}")
    for severity, issues in results['issues'].items():
        if issues:
            print(f"  {severity.upper()}: {len(issues)}")
