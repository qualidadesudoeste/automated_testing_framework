# Framework Completo de Testes Automatizados

Framework Python e pacotes portáteis de automação para planejar, executar e reportar testes de API, regras de negócio, interface, UI/UX, acessibilidade, performance, segurança e qualidade de código. Pode ser usado diretamente pela linha de comando ou incorporado a agentes compatíveis com skills em Markdown.

## Capacidades

| Suíte | Cobertura |
|---|---|
| `api` | Contratos, asserções JSON, filtros, ordenação, paginação, SLA e concorrência |
| `openapi` | OpenAPI 3.x, status declarados e validação recursiva de schemas JSON |
| `business_rules` | Regras declarativas rastreáveis, sem uso de `eval` |
| `web_quality` | HTML, responsividade, headings, labels, idioma, campos obrigatórios e conteúdo |
| `browser` | Jornadas multi-browser, formulários, CPF/CNPJ, teclado, downloads e evidências |
| `project_quality` | Sintaxe, modularidade, testes, documentação, cobertura, OpenAPI, arquivos obrigatórios e indícios de autoria automatizada |
| `external_tools` | Semgrep, Gitleaks, Trivy, Lighthouse, k6 e ZAP com comandos allowlisted |
| `performance` | Carga, stress, spike, percentis, erro, throughput e thresholds |
| `security` | Headers, TLS, CORS, injeções, autenticação, rate limiting e portas, conforme configuração |

Todos os resultados são convertidos para um modelo comum, deduplicados e avaliados por quality gate. Os relatórios podem ser gerados em HTML, JSON, texto, JUnit XML e SARIF.

## Instalação

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

No Linux ou macOS, usar `.venv/bin/python`.

Para jornadas reais de navegador e comparação visual:

```bash
python -m pip install "playwright>=1.45.0"
python -m pip install "Pillow>=10.0.0"
python -m playwright install chromium
```

## Uso seguro

Validar o plano sem acessar o alvo:

```bash
python run_tests.py --dry-run
```

Executar suítes passivas contra a aplicação local configurada:

```bash
python run_tests.py --suite api --suite business_rules --suite web_quality
```

Executar testes ativos autorizados:

```bash
python run_tests.py --suite performance --authorized
python run_tests.py --suite security --authorized
```

Chamadas mutantes, concorrência, navegador, carga e segurança exigem `--authorized`. Os códigos de saída são:

- `0`: execução concluída e quality gate aprovado;
- `1`: configuração ou execução inválida;
- `2`: quality gate reprovado;
- `3`: execução bloqueada pela política de segurança.

## Política de segurança

O arquivo padrão aponta para `127.0.0.1`. Alvos externos são bloqueados por padrão. As suítes `browser`, `performance` e `security` são consideradas ativas e exigem `--authorized` quando a política padrão estiver habilitada.

Antes de testar staging ou outro alvo autorizado:

1. obter autorização formal;
2. definir allowlist e janela de execução;
3. limitar usuários, duração e workers;
4. executar `--dry-run`;
5. monitorar o alvo e manter um critério de interrupção.

Nunca habilitar carga, scan ou injeção em produção apenas para experimentar o framework.

## Configuração

O arquivo principal é `config/config.yaml`. Exemplo de contrato de API:

```yaml
api:
  enabled: true
  endpoints:
    - path: /api/health
      method: GET
      expected_status: 200
      content_type: application/json
      required_json_fields: [status, timestamp]
```

Exemplo de regra de negócio:

```yaml
business_rules:
  enabled: true
  rules:
    - id: HEALTH-001
      endpoint: /api/health
      path: status
      operator: eq
      expected: healthy
      severity: high
```

Operadores suportados: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `not_contains`, `is_true`, `is_false`, `exists`, `matches`, `starts_with`, `ends_with`, `between`, `length_eq`, `is_null`, `not_null`, `sorted_asc`, `sorted_desc` e `unique`.

Exemplo de filtro, ordenação, paginação e SLA de API:

```yaml
api:
  endpoints:
    - path: /api/customers
      params: {q: Ana, sort: name}
      max_response_ms: 500
      assert_filter: {items_path: items, field: name, contains: Ana}
      assert_sorted: {items_path: items, field: name, direction: asc}
      assert_pagination: {items_path: items, id_path: id, pages: [1, 2]}
```

Exemplo de jornada de navegador:

```yaml
browser:
  enabled: true
  journeys:
    - name: login
      steps:
        - action: goto
          path: /login
        - action: fill
          selector: "[name=email]"
          value: "${TEST_USER}"
        - action: click
          selector: "button[type=submit]"
        - action: check_text
          selector: main
          value: Dashboard
        - action: screenshot
```

Para formulários, as jornadas também aceitam `validate_field` (perfis `cpf`, `cnpj`, `numeric` e `required`), `assert_required`, `assert_disabled`, `assert_radio_exclusive`, `assert_clear`, `assert_sorted`, `assert_persistence`, `assert_tab_order`, `assert_not_truncated`, `upload`, `download`, `assert_confirmation` e `measure_navigation`.

O framework não expande segredos automaticamente. Injete credenciais por uma camada segura ou gere o YAML temporário no pipeline sem versioná-lo.

A opção `project_quality.detect_ai_authorship` procura declarações explícitas, trailers de coautoria e arquivos de configuração associados a assistentes. Os resultados são sempre classificados como suspeitos: a presença é um indício a revisar, enquanto a ausência não comprova autoria humana. Use `ai_authorship_exclude` para excluir caminhos e `ai_authorship_allowlist` para exceções deliberadamente aceitas.

## Estrutura

```text
testing_framework/       núcleo, segurança, orquestração e relatórios
performance/             executor de carga, stress e spike
security/                verificações dinâmicas de segurança
software-testing/        distribuição universal para um único agente
qa-master-testing/       distribuição multiagente com QA Mestre e 13 especialistas
schemas/                 contratos JSON de plano, achado e relatório
test/                    testes do próprio framework
config/config.yaml       configuração segura de exemplo
examples/sample_app.py   aplicação local intencionalmente vulnerável
run_tests.py             CLI principal
```

## Distribuições para agentes

A pasta `software-testing/` contém uma skill autocontida para ambientes que executam um único agente. O QA Mestre assume internamente todos os papéis e mantém a cobertura integral mesmo sem paralelismo.

A pasta `qa-master-testing/` contém a distribuição multiagente: uma skill coordenadora e 13 skills especialistas reais para ambientes capazes de iniciar agentes auxiliares e aguardar seus resultados.

As duas distribuições carregam o mesmo framework determinístico em `assets/` e executam as mesmas nove suítes. A distribuição multiagente é canônica quando o ambiente suporta agentes auxiliares; a distribuição de agente único é a alternativa universal.

## Pacote multiagente QA Mestre

O manifesto neutro fica em `plugin/plugin.json`. O pacote contém uma skill `qa-master` e 13 skills especialistas reais. Os dois prompts-fonte completos são referências normativas, com matriz de rastreabilidade para que nenhuma regra seja perdida durante a reorganização. O QA Mestre cria os subagentes, espera cada resultado, verifica modos, controles, 25 dimensões, 24 testes adversariais, proveniência do código e nove suítes, e só então chama `qa-consolidator`. A ausência de qualquer agente ou obrigação bloqueia a conclusão.

Inicializar e validar o contrato de uma auditoria completa:

```bash
python qa-master-testing/scripts/init_run.py qa-results/execucao
python qa-master-testing/scripts/check_run.py qa-results/execucao
python qa-master-testing/scripts/check_run.py qa-results/execucao --final
```

O validador exige resultados reais dos 13 agentes, cobertura das nove suítes, 25 dimensões, 24 testes adversariais e todos os entregáveis.

Validar o pacote multiagente:

```bash
python qa-master-testing/scripts/validate_bundle.py qa-master-testing
```

## Desenvolvimento e validação

```bash
python -m unittest discover -s test -v
python -m compileall -q run_tests.py testing_framework performance security test
```

Inicie a aplicação local somente para testes controlados:

```bash
python examples/sample_app.py
python run_tests.py --suite api --suite business_rules --suite web_quality
```

Os artefatos em `reports/` e caches Python são ignorados pelo controle de versão.

## Limitações conhecidas

- A auditoria `web_quality` é estrutural; contraste calculado e testes completos de teclado exigem Playwright/axe.
- Achados do módulo dinâmico de segurança são marcados como suspeitos até confirmação.
- Performance de frontend e Core Web Vitals devem ser complementados com Lighthouse.
- Observabilidade de servidor depende de integração com a plataforma do ambiente-alvo.
- Conformidade com protótipo, ortografia sem glossário, experiência subjetiva e LGPD sem requisitos jurídicos continuam exigindo baseline ou revisão humana.
