# Changelog

## 2.1.0 — Portabilidade, correções de segurança do próprio framework e cobertura OWASP/Nielsen

Refatoração para tornar o framework integrável a qualquer projeto (não apenas ao próprio
repositório), corrigir inconsistências de segurança no código do framework e ampliar a
cobertura de OWASP Top 10 (Web) 2021, OWASP API Security Top 10 2023 e das heurísticas de
usabilidade de Nielsen.

### ⚠️ Mudança que quebra compatibilidade

- **`safety.py`**: endereços link-local (`169.254.0.0/16`, `fe80::/10` — inclui o metadata IP
  de nuvem `169.254.169.254`) agora são classificados como **`external`**, não mais `private`.
  Qualquer config existente que aponte um alvo autorizado para um endereço link-local passa a
  exigir `safety.allow_external_targets: true` além de `--authorized`. Mitigação deliberada de
  SSRF para roubo de credenciais de nuvem — não é uma regressão a ser contornada.

### Portabilidade

- `project_quality`/`external_tools`: o `project_root` padrão passou de "dois níveis acima do
  config" para "diretório do próprio config" — comportamento correto para qualquer projeto que
  não replique a estrutura interna deste repositório. Configs que já definem `project_root`
  explicitamente (como `config/config.yaml` deste repositório) não são afetadas.
- `software-testing/scripts/run_framework.py`: removido o atalho que fixava `cwd` de volta no
  repositório do framework sempre que a skill estava aninhada dentro dele, o que forçava toda
  execução de volta para este repo mesmo mirando outro projeto.
- Novo `examples/config.template.yaml` (também em `software-testing/assets/` e
  `qa-master-testing/assets/`) como ponto de partida para configurar um projeto-alvo.
- Nova chave opcional `reporting.output_dir_base` (`"cwd"` default / `"config"`) para gravar
  relatórios ao lado do config, independentemente do diretório de onde `software-test` foi
  invocado.
- Removido o pacote `utils/` (gerador de relatório com logo): código morto, não importado por
  nada, não empacotado no wheel. Histórico da funcionalidade permanece em `CHANGELOG_LOGO.md`.
- Documentado no `README.md` o fluxo de instalação como dependência (`pip install` + `software-test -c /caminho/absoluto/config.yaml`).

### Segurança do próprio framework

- `security/security_tester.py` reescrito para usar `testing_framework.http.create_session`/`target_url`
  (mesmo allowlist de origem que as demais suítes) em vez de `requests.Session()` cru e
  concatenação de string.
- Removidos os blocos `if __name__ == "__main__"` de `security/security_tester.py` e
  `performance/performance_tester.py`, que permitiam rodar essas suítes ativas diretamente,
  ignorando totalmente `testing_framework.safety.validate_execution()`/`--authorized`.
- Nova função `testing_framework.http.assert_same_origin_response` valida toda a cadeia de
  redirecionamento contra a origem autorizada (não só a URL inicial) — evita que um alvo
  comprometido use um 3xx para desviar a chamada para outra origem.
- Nova revalidação (`testing_framework.safety.revalidate_or_raise`) imediatamente antes de
  despachar cada suíte ativa, mitigando parcialmente TOCTOU de DNS rebinding.
- `models.py`: nova regra de redação para pares usuário/senha citados em texto livre (ex.:
  achados de credenciais fracas), que antes escapavam da sanitização de relatórios.
- Novo teto configurável `safety.max_requests_per_probe` (padrão 50, igual ao valor anterior
  fixo no código) limitando rajadas de requisição em sondagens de rate-limit e payloads.

### Cobertura OWASP ampliada

- Nova suíte `access_control` (opt-in): BOLA/IDOR (API1:2023), mass assignment (API3:2023) e
  BFLA (API5:2023) via identidades declarativas com tokens distintos.
- `security`: payloads de NoSQL injection (antes definidos mas nunca usados) agora ativos via
  `injection_tests.types: [nosql_injection]`; novo `injection_tests.json_fields` para enviar os
  mesmos payloads no corpo JSON; novo `misconfiguration_tests` para arquivos sensíveis expostos
  e métodos HTTP permissivos.
- `api`: novo `assert_resource_limits` por endpoint (API4:2023 — consumo irrestrito de recursos).

### Heurísticas de Nielsen

- `browser`: novas ações `assert_loading_state` (H1 — visibilidade do status do sistema) e
  `assert_unsaved_changes_warning` (H3 — controle e liberdade do usuário).
- `validate_field` aceita `error_contains` por caso para checar o conteúdo da mensagem de erro,
  não só sua visibilidade (H9).
- `web_quality`: nova checagem de página sem `<h1>` ou com múltiplos `<h1>` (WCAG 1.3.1).
- `browser`: ausência de `axe_script` agora gera um achado `info` visível em vez de pular a
  checagem de acessibilidade silenciosamente (`browser.warn_on_missing_axe`, default `true`).

Todas as adições acima (exceto a reclassificação de link-local) são opt-in e preservam o
comportamento de `config/config.yaml` e `examples/example_config.yaml` deste repositório.
