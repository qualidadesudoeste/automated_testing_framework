#!/usr/bin/env python3
"""
Módulo de Testes de Segurança
Realiza testes de vulnerabilidades web, autenticação, injeção e análise de rede.

Não execute este módulo diretamente — use
`software-test --suite security --authorized -c <config>`, que aplica
`testing_framework.safety.validate_execution()` (gate --authorized, allowlist de
origem e limites de segurança) antes de qualquer chamada ativa.
"""

import socket
import ssl
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from urllib.parse import urlparse

import requests

from testing_framework.http import assert_same_origin_response, create_session, target_url


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

    def to_dict(self) -> dict[str, Any]:
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

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.target = config.get('target', {})
        self.sec_config = config.get('security', {})
        self.timeout = config.get('general', {}).get('timeout', 30)
        self.session = create_session(config)
        self.issues: list[SecurityIssue] = []
        # Teto configurável de requisições por sondagem (rate-limit e loops de payload) —
        # evita que a suíte security gere carga descontrolada contra o alvo autorizado.
        self.max_requests_per_probe = int(config.get('safety', {}).get('max_requests_per_probe', 50))

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

    def _get(self, url: str, **kwargs) -> requests.Response:
        """GET com validação de origem em toda a cadeia de redirecionamento."""
        response = self.session.get(url, timeout=self.timeout, **kwargs)
        assert_same_origin_response(self.target['base_url'], response)
        return response

    def _post(self, url: str, **kwargs) -> requests.Response:
        """POST com validação de origem em toda a cadeia de redirecionamento."""
        response = self.session.post(url, timeout=self.timeout, **kwargs)
        assert_same_origin_response(self.target['base_url'], response)
        return response

    # ------------------------------------------------------------------
    # Injeção: helper único para os testes baseados em payload por parâmetro GET
    # ------------------------------------------------------------------

    @staticmethod
    def _signature_check(signatures: list[str]) -> Callable[[requests.Response, str], str | None]:
        def check(response: requests.Response, _payload: str) -> str | None:
            response_lower = response.text.lower()
            for signature in signatures:
                if signature in response_lower:
                    return signature
            return None
        return check

    @staticmethod
    def _reflection_check(response: requests.Response, payload: str) -> str | None:
        if payload in response.text or payload.replace('"', '&quot;') in response.text:
            return payload
        return None

    def _probe_query_param(
        self, url: str, param_name: str, payloads: list[str],
        check: Callable[[requests.Response, str], str | None],
        *, category: str, severity: str, cwe_id: str, title: str, description: str, recommendation: str,
    ) -> None:
        limit = min(len(payloads), self.max_requests_per_probe)
        for payload in payloads[:limit]:
            try:
                response = self._get(url, params={param_name: payload})
            except (requests.RequestException, ValueError):
                continue
            evidence = check(response, payload)
            if evidence:
                self._add_issue(SecurityIssue(
                    severity=severity, category=category, title=title, description=description,
                    url=response.url, evidence=f'Payload: {payload}, Indicador: {evidence}',
                    recommendation=recommendation, cwe_id=cwe_id,
                ))
                break

    def test_sql_injection(self) -> list[SecurityIssue]:
        """Testa vulnerabilidades de SQL Injection"""
        print("\n[SECURITY] Testando SQL Injection...")
        endpoints = self.target.get('api_endpoints', []) + self.target.get('web_endpoints', [])
        sql_errors = [
            'sql syntax', 'mysql_fetch', 'postgresql', 'ora-', 'sqlite',
            'syntax error', 'unclosed quotation', 'quoted string not properly terminated',
        ]
        for endpoint in endpoints:
            try:
                url = target_url(self.target['base_url'], str(endpoint))
            except ValueError:
                continue
            self._probe_query_param(
                url, 'id', self.sql_payloads, self._signature_check(sql_errors),
                category='injection', severity='critical', cwe_id='CWE-89',
                title='Possível SQL Injection',
                description='O endpoint pode ser vulnerável a SQL Injection. Erro de banco de dados detectado na resposta.',
                recommendation='Utilize prepared statements ou ORM para prevenir SQL injection. Valide e sanitize todas as entradas do usuário.',
            )
        return self.issues

    def test_nosql_injection(self) -> list[SecurityIssue]:
        """Testa vulnerabilidades de NoSQL Injection"""
        print("\n[SECURITY] Testando NoSQL Injection...")
        endpoints = self.target.get('api_endpoints', [])
        nosql_signatures = ['bson', '$where', 'mongoerror', 'mongodb', 'nosqlmap']
        for endpoint in endpoints:
            try:
                url = target_url(self.target['base_url'], str(endpoint))
            except ValueError:
                continue
            self._probe_query_param(
                url, 'id', self.nosql_payloads, self._signature_check(nosql_signatures),
                category='injection', severity='critical', cwe_id='CWE-943',
                title='Possível NoSQL Injection',
                description='O endpoint pode ser vulnerável a NoSQL Injection. Indicador de banco não relacional detectado na resposta.',
                recommendation='Valide o tipo e a estrutura de toda entrada antes de usá-la em consultas; evite montar filtros diretamente a partir de entrada do usuário.',
            )
        return self.issues

    def test_xss(self) -> list[SecurityIssue]:
        """Testa vulnerabilidades de Cross-Site Scripting (XSS)"""
        print("\n[SECURITY] Testando XSS (Cross-Site Scripting)...")
        endpoints = self.target.get('web_endpoints', [])
        for endpoint in endpoints:
            try:
                url = target_url(self.target['base_url'], str(endpoint))
            except ValueError:
                continue
            self._probe_query_param(
                url, 'q', self.xss_payloads, self._reflection_check,
                category='injection', severity='high', cwe_id='CWE-79',
                title='Possível XSS Refletido',
                description='O endpoint pode refletir entrada do usuário sem sanitização adequada.',
                recommendation='Encode todas as saídas HTML. Use Content Security Policy (CSP). Valide e sanitize entradas do usuário.',
            )
        return self.issues

    def test_command_injection(self) -> list[SecurityIssue]:
        """Testa vulnerabilidades de Command Injection"""
        print("\n[SECURITY] Testando Command Injection...")
        endpoints = self.target.get('api_endpoints', [])
        indicators = ['root:', 'bin/bash', 'uid=', 'gid=', 'groups=', 'volume serial number', 'directory of']
        for endpoint in endpoints:
            try:
                url = target_url(self.target['base_url'], str(endpoint))
            except ValueError:
                continue
            self._probe_query_param(
                url, 'cmd', self.command_injection_payloads, self._signature_check(indicators),
                category='injection', severity='critical', cwe_id='CWE-78',
                title='Possível Command Injection',
                description='O endpoint pode ser vulnerável a injeção de comandos do sistema.',
                recommendation='Nunca execute comandos do sistema com entrada do usuário. Use APIs seguras ao invés de shell commands.',
            )
        return self.issues

    def test_json_body_injection(self) -> list[SecurityIssue]:
        """Envia os mesmos payloads de injeção no corpo JSON de endpoints de API.

        Opt-in via ``security.injection_tests.json_fields``; reaproveita os payloads e
        checagens de assinatura já usados nos testes baseados em query string.
        """
        injection_config = self.sec_config.get('injection_tests', {})
        json_fields = injection_config.get('json_fields', [])
        if not json_fields:
            return self.issues
        types = set(injection_config.get('types', []))
        variants: list[tuple[list[str], Callable, str, str, str, str]] = []
        if 'sql_injection' in types:
            variants.append((self.sql_payloads, self._signature_check(['sql syntax', 'mysql_fetch', 'postgresql', 'ora-', 'sqlite', 'syntax error']), 'critical', 'CWE-89', 'Possível SQL Injection (corpo JSON)', 'Utilize prepared statements ou ORM; valide também campos do corpo JSON.'))
        if 'command_injection' in types:
            variants.append((self.command_injection_payloads, self._signature_check(['root:', 'bin/bash', 'uid=', 'gid=', 'groups=']), 'critical', 'CWE-78', 'Possível Command Injection (corpo JSON)', 'Nunca execute comandos do sistema com entrada do usuário, inclusive vinda do corpo JSON.'))
        if 'nosql_injection' in types:
            variants.append((self.nosql_payloads, self._signature_check(['bson', '$where', 'mongoerror', 'mongodb']), 'critical', 'CWE-943', 'Possível NoSQL Injection (corpo JSON)', 'Valide o tipo e a estrutura de campos do corpo JSON antes de usá-los em consultas.'))
        if not variants:
            return self.issues
        endpoints = self.target.get('api_endpoints', [])
        for endpoint in endpoints:
            try:
                url = target_url(self.target['base_url'], str(endpoint))
            except ValueError:
                continue
            for field_name in json_fields:
                for payloads, check, severity, cwe_id, title, recommendation in variants:
                    limit = min(len(payloads), self.max_requests_per_probe)
                    for payload in payloads[:limit]:
                        try:
                            response = self._post(url, json={field_name: payload})
                        except (requests.RequestException, ValueError):
                            continue
                        evidence = check(response, payload)
                        if evidence:
                            self._add_issue(SecurityIssue(
                                severity=severity, category='injection', title=title,
                                description=f"O campo JSON '{field_name}' pode ser vulnerável a injeção.",
                                url=response.url, evidence=f'Payload: {payload}, Indicador: {evidence}',
                                recommendation=recommendation, cwe_id=cwe_id,
                            ))
                            break
        return self.issues

    def test_security_headers(self) -> list[SecurityIssue]:
        """Verifica presença de headers de segurança importantes"""
        print("\n[SECURITY] Verificando Headers de Segurança...")
        url = self.target['base_url']
        try:
            response = self._get(url)
            headers = response.headers

            security_headers = {
                'X-Frame-Options': {'severity': 'medium', 'description': 'Protege contra clickjacking', 'recommendation': 'Adicione header: X-Frame-Options: DENY ou SAMEORIGIN'},
                'X-Content-Type-Options': {'severity': 'low', 'description': 'Previne MIME type sniffing', 'recommendation': 'Adicione header: X-Content-Type-Options: nosniff'},
                'Strict-Transport-Security': {'severity': 'high', 'description': 'Força uso de HTTPS', 'recommendation': 'Adicione header: Strict-Transport-Security: max-age=31536000; includeSubDomains'},
                'Content-Security-Policy': {'severity': 'medium', 'description': 'Previne XSS e injeção de conteúdo', 'recommendation': 'Adicione header: Content-Security-Policy com política apropriada'},
                'X-XSS-Protection': {'severity': 'low', 'description': 'Ativa proteção XSS do navegador', 'recommendation': 'Adicione header: X-XSS-Protection: 1; mode=block'},
                'Referrer-Policy': {'severity': 'low', 'description': 'Controla informações de referrer', 'recommendation': 'Adicione header: Referrer-Policy: no-referrer ou strict-origin-when-cross-origin'},
                'Permissions-Policy': {'severity': 'low', 'description': 'Controla recursos do navegador', 'recommendation': 'Adicione header: Permissions-Policy com política apropriada'},
            }

            for header, info in security_headers.items():
                if header not in headers:
                    self._add_issue(SecurityIssue(
                        severity=info['severity'], category='configuration',
                        title=f'Header de Segurança Ausente: {header}', description=info['description'],
                        url=url, recommendation=info['recommendation'], cwe_id='CWE-693',
                    ))

            sensitive_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in sensitive_headers:
                if header in headers:
                    self._add_issue(SecurityIssue(
                        severity='info', category='information_disclosure',
                        title=f'Header Expõe Informações: {header}',
                        description=f'O header {header} expõe informações sobre a tecnologia do servidor.',
                        url=url, evidence=f'{header}: {headers[header]}',
                        recommendation=f'Remova ou oculte o header {header}', cwe_id='CWE-200',
                    ))
        except (requests.RequestException, ValueError) as exc:
            print(f"  Erro ao verificar headers: {exc}")
        return self.issues

    def test_ssl_tls(self) -> list[SecurityIssue]:
        """Verifica configuração SSL/TLS"""
        print("\n[SECURITY] Verificando SSL/TLS...")
        url = self.target['base_url']
        parsed = urlparse(url)

        if parsed.scheme != 'https':
            self._add_issue(SecurityIssue(
                severity='high', category='transport_security', title='HTTPS Não Utilizado',
                description='O sistema não utiliza HTTPS, expondo dados em texto claro.', url=url,
                recommendation='Configure certificado SSL/TLS e force redirecionamento para HTTPS', cwe_id='CWE-319',
            ))
            return self.issues

        hostname = parsed.hostname
        port = parsed.port or 443
        if not hostname:
            return self.issues

        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher = ssock.cipher()
                    version = ssock.version()

                    if version in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                        self._add_issue(SecurityIssue(
                            severity='high', category='transport_security', title='Protocolo SSL/TLS Inseguro',
                            description=f'O servidor suporta protocolo inseguro: {version}', url=url,
                            evidence=f'Versão: {version}', recommendation='Desabilite protocolos antigos e use apenas TLSv1.2 ou TLSv1.3',
                            cwe_id='CWE-326',
                        ))

                    weak_ciphers = ['DES', 'RC4', 'MD5', 'NULL', 'EXPORT', 'anon']
                    cipher_name = cipher[0] if cipher else ''
                    for weak in weak_ciphers:
                        if weak in cipher_name.upper():
                            self._add_issue(SecurityIssue(
                                severity='high', category='transport_security', title='Cifra SSL/TLS Fraca',
                                description=f'O servidor utiliza cifra fraca: {cipher_name}', url=url,
                                evidence=f'Cipher: {cipher_name}', recommendation='Configure apenas cifras fortes (AES-GCM, ChaCha20)',
                                cwe_id='CWE-327',
                            ))
                            break
        except OSError as exc:
            print(f"  Aviso: Não foi possível verificar SSL/TLS completamente: {exc}")
        return self.issues

    def test_cors(self) -> list[SecurityIssue]:
        """Verifica configuração de CORS"""
        print("\n[SECURITY] Verificando CORS (Cross-Origin Resource Sharing)...")
        url = self.target['base_url']
        try:
            response = self._get(url, headers={'Origin': 'https://evil.com'})
            if 'Access-Control-Allow-Origin' in response.headers:
                allowed_origin = response.headers['Access-Control-Allow-Origin']
                if allowed_origin == '*':
                    self._add_issue(SecurityIssue(
                        severity='medium', category='configuration', title='CORS Configurado com Wildcard',
                        description='O servidor permite requisições de qualquer origem (*).', url=url,
                        evidence=f'Access-Control-Allow-Origin: {allowed_origin}',
                        recommendation='Restrinja CORS apenas para origens confiáveis específicas', cwe_id='CWE-942',
                    ))
                elif allowed_origin == 'https://evil.com':
                    self._add_issue(SecurityIssue(
                        severity='high', category='configuration', title='CORS Reflete Origem Não Confiável',
                        description='O servidor reflete a origem da requisição sem validação.', url=url,
                        evidence=f'Origin enviada: https://evil.com, Permitida: {allowed_origin}',
                        recommendation='Valide origens contra uma whitelist de domínios confiáveis', cwe_id='CWE-942',
                    ))
        except (requests.RequestException, ValueError):
            pass
        return self.issues

    def test_exposed_files(self) -> list[SecurityIssue]:
        """Sonda um pequeno conjunto curado de caminhos sensíveis (env, VCS, backups)."""
        print("\n[SECURITY] Verificando arquivos sensíveis expostos...")
        base_url = self.target['base_url']
        control_signature = None
        try:
            control = self._get(target_url(base_url, '/__qa_probe_nonexistent__'))
            control_signature = (control.status_code, control.headers.get('content-type', ''), len(control.text))
        except (requests.RequestException, ValueError):
            pass
        sensitive_paths = ['/.env', '/.git/HEAD', '/.git/config', '/config.php.bak', '/.DS_Store']
        for path in sensitive_paths:
            try:
                response = self._get(target_url(base_url, path))
            except (requests.RequestException, ValueError):
                continue
            if response.status_code != 200:
                continue
            content_type = response.headers.get('content-type', '')
            signature = (response.status_code, content_type, len(response.text))
            if control_signature is not None and signature == control_signature:
                continue  # provavelmente a mesma página padrão de "não encontrado"
            if 'text/html' in content_type.lower():
                continue
            self._add_issue(SecurityIssue(
                severity='high', category='configuration', title=f'Arquivo sensível possivelmente exposto: {path}',
                description='O caminho retornou 200 com conteúdo que não parece ser a página padrão de não encontrado.',
                url=response.url, evidence=f'status={response.status_code} content-type={content_type}',
                recommendation='Bloquear acesso público a arquivos de configuração e metadados de VCS.', cwe_id='CWE-538',
            ))
        return self.issues

    def test_http_methods(self) -> list[SecurityIssue]:
        """Sonda métodos HTTP permissivos (TRACE/CONNECT) via OPTIONS."""
        print("\n[SECURITY] Verificando métodos HTTP permissivos...")
        base_url = self.target['base_url']
        for endpoint in self.target.get('api_endpoints', []):
            try:
                url = target_url(base_url, str(endpoint))
                response = self.session.options(url, timeout=self.timeout)
                assert_same_origin_response(base_url, response)
            except (requests.RequestException, ValueError):
                continue
            allow = f"{response.headers.get('Allow', '')} {response.headers.get('Access-Control-Allow-Methods', '')}".upper()
            risky = {method for method in ('TRACE', 'CONNECT') if method in allow}
            if risky:
                self._add_issue(SecurityIssue(
                    severity='medium', category='configuration', title=f'Métodos HTTP permissivos em {endpoint}',
                    description=f'O endpoint anuncia métodos potencialmente perigosos: {", ".join(sorted(risky))}.',
                    url=response.url, evidence=allow.strip(),
                    recommendation='Desabilitar TRACE/CONNECT no servidor ou proxy reverso.', cwe_id='CWE-749',
                ))
        return self.issues

    def test_authentication(self) -> list[SecurityIssue]:
        """Testa vulnerabilidades de autenticação"""
        print("\n[SECURITY] Testando Autenticação...")
        base_url = self.target['base_url']
        weak_passwords = ['password', '123456', 'admin', 'root', 'test', '']
        common_users = ['admin', 'administrator', 'root', 'user', 'test']
        login_endpoints = ['/login', '/api/login', '/auth/login', '/signin']

        for endpoint in login_endpoints:
            try:
                url = target_url(base_url, endpoint)
                response = self._get(url)
            except (requests.RequestException, ValueError):
                continue
            if response.status_code == 404:
                continue
            for user in common_users[:2]:
                for password in weak_passwords[:2]:
                    try:
                        login_response = self._post(url, json={'username': user, 'password': password})
                        if login_response.status_code == 200:
                            self._add_issue(SecurityIssue(
                                severity='critical', category='authentication', title='Credenciais Fracas Aceitas',
                                description=f'O sistema aceita credenciais fracas: {user}/{password}',
                                url=url, evidence=f'Login bem-sucedido com {user}/{password}',
                                recommendation='Implemente política de senhas fortes. Force alteração de senhas padrão.',
                                cwe_id='CWE-521',
                            ))
                    except (requests.RequestException, ValueError):
                        pass
        return self.issues

    def test_rate_limiting(self) -> list[SecurityIssue]:
        """Testa se há rate limiting implementado"""
        print("\n[SECURITY] Testando Rate Limiting...")
        url = self.target['base_url']
        if self.target.get('api_endpoints'):
            try:
                url = target_url(self.target['base_url'], str(self.target['api_endpoints'][0]))
            except ValueError:
                pass
        try:
            responses = []
            for _ in range(self.max_requests_per_probe):
                response = self._get(url)
                responses.append(response.status_code)
            if 429 not in responses:
                self._add_issue(SecurityIssue(
                    severity='medium', category='configuration', title='Rate Limiting Não Detectado',
                    description='O sistema não parece implementar rate limiting, permitindo potenciais ataques de força bruta ou DDoS.',
                    url=url, evidence=f'{len(responses)} requisições realizadas sem bloqueio',
                    recommendation='Implemente rate limiting para prevenir abuso. Use ferramentas como nginx rate limiting ou bibliotecas específicas.',
                    cwe_id='CWE-770',
                ))
        except (requests.RequestException, ValueError) as exc:
            print(f"  Erro ao testar rate limiting: {exc}")
        return self.issues

    def scan_ports(self) -> list[SecurityIssue]:
        """Realiza scan básico de portas"""
        print("\n[SECURITY] Realizando Scan de Portas...")
        hostname = urlparse(self.target['base_url']).hostname
        if not hostname:
            return self.issues
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
            except OSError:
                pass

        risky_ports = {
            21: 'FTP (não criptografado)',
            23: 'Telnet (não criptografado)',
            3306: 'MySQL (não deve ser exposto)',
            5432: 'PostgreSQL (não deve ser exposto)',
            6379: 'Redis (não deve ser exposto)',
            27017: 'MongoDB (não deve ser exposto)',
        }
        for port in open_ports:
            if port in risky_ports:
                self._add_issue(SecurityIssue(
                    severity='high', category='network', title=f'Porta Potencialmente Insegura Aberta: {port}',
                    description=f'A porta {port} está aberta: {risky_ports[port]}',
                    evidence=f'Porta {port} acessível externamente',
                    recommendation='Feche portas desnecessárias ou restrinja acesso via firewall', cwe_id='CWE-16',
                ))
        return self.issues

    def run_all_tests(self) -> dict[str, Any]:
        """Executa todos os testes de segurança habilitados"""
        results: dict[str, Any] = {
            'test_suite': 'security',
            'target': self.target,
            'start_time': datetime.now().isoformat(),
            'tests_executed': [],
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
            types = injection_config.get('types', [])
            if 'command_injection' in types:
                self.test_command_injection()
                results['tests_executed'].append('command_injection')
            if 'nosql_injection' in types:
                self.test_nosql_injection()
                results['tests_executed'].append('nosql_injection')
            if injection_config.get('json_fields'):
                self.test_json_body_injection()
                results['tests_executed'].append('json_body_injection')

        auth_config = self.sec_config.get('auth_tests', {})
        if auth_config.get('enabled', False):
            tests = auth_config.get('tests', [])
            if 'weak_passwords' in tests:
                self.test_authentication()
                results['tests_executed'].append('authentication')
            if 'rate_limiting' in tests:
                self.test_rate_limiting()
                results['tests_executed'].append('rate_limiting')

        misconfig_config = self.sec_config.get('misconfiguration_tests', {})
        if misconfig_config.get('enabled', False):
            if misconfig_config.get('exposed_files', True):
                self.test_exposed_files()
                results['tests_executed'].append('exposed_files')
            if misconfig_config.get('http_methods', True):
                self.test_http_methods()
                results['tests_executed'].append('http_methods')

        network_config = self.sec_config.get('network_scan', {})
        if network_config.get('enabled', False):
            self.scan_ports()
            results['tests_executed'].append('port_scan')

        issues_by_severity: dict[str, list[dict[str, Any]]] = {
            'critical': [], 'high': [], 'medium': [], 'low': [], 'info': [],
        }
        for issue in self.issues:
            issues_by_severity[issue.severity].append(issue.to_dict())

        results['issues'] = issues_by_severity
        results['total_issues'] = len(self.issues)
        results['end_time'] = datetime.now().isoformat()

        severity_weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1, 'info': 0}
        total_score = sum(severity_weights[issue.severity] for issue in self.issues)
        results['security_score'] = max(0, 100 - total_score)

        return results
