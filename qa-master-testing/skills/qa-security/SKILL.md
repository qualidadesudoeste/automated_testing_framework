---
name: qa-security
description: Auditar segurança de aplicação com análise estática e testes dinâmicos autorizados, cobrindo autenticação, sessão, autorização, OWASP, upload, configuração, dependências, segredos e infraestrutura. Usar como especialista obrigatório do QA Mestre ou em avaliações de segurança e preparação para entrega.
---

# Auditar segurança

## Segurança operacional

Executar análise passiva sempre. Exigir autorização formal para DAST, injeção, força bruta, scan, portas ou ações mutáveis. Usar payloads não destrutivos, limites baixos e alvo allowlisted.

## Verificar

- Senhas, MFA, rate limit, enumeração, recovery, fixation, timeout, logout e cookies.
- IDOR/BOLA, escalada horizontal/vertical, policies, escopo, mass assignment, exportação, download e webhook.
- SQLi, XSS, fórmula CSV, command/SSTI/LDAP/XXE, redirect, desserialização e SSRF.
- Upload por magic bytes, allowlist, tamanho, traversal, webroot, SVG/PDF ativo, ZIP bomb e quarentena.
- Debug, arquivos sensíveis, segredos, TLS, CSP, HSTS, frame, nosniff, referrer, permissions, CORS e CSRF.
- Dependências, containers e IaC; logs e evidências sem segredos ou PII.
- Logout/voltar, cache de dado pessoal, token antigo, sessão longa e rota direta com perfil restrito.
- Executar `security` e Semgrep/Gitleaks/Trivy/ZAP de `external_tools` após `--dry-run`; confirmar achado heurístico crítico.

## Entregar

Gravar `agents/qa-security.json` com categoria, ativo, pré-condição, impacto, evidência sanitizada, confiança, reprodução segura e correção. Diferenciar vulnerabilidade confirmada de suspeita.
