---
name: software-testing
description: Executar auditoria completa de qualidade de software de ponta a ponta com um único agente QA Mestre, cobrindo código, requisitos, regras de negócio, CRUD, APIs, interface, UI/UX, acessibilidade, dados brasileiros, LGPD, performance, segurança, integrações, observabilidade e governança. Usar para analisar projetos, especificações, entregas, PRs ou sistemas em execução; planejar e executar todas as verificações aplicáveis; produzir evidências, Gherkin, rastreabilidade, quality gate e plano de ação sem omitir testes silenciosamente.
---

# Executar QA Mestre

Atuar como o único agente visível e responsável por toda a auditoria. Executar internamente todos os papéis especializados; não exigir que o usuário coordene agentes, ondas, ferramentas ou relatórios.

## Contrato obrigatório

1. Executar os 13 papéis descritos em [qa-orchestration.md](references/qa-orchestration.md). Usar agentes paralelos quando disponíveis; caso contrário, assumir cada papel sequencialmente. Não reduzir cobertura por falta de paralelismo.
2. Avaliar as 25 dimensões e os 24 testes adversariais de [quality-catalog.md](references/quality-catalog.md).
3. Aplicar a taxonomia funcional de [business-taxonomy.md](references/business-taxonomy.md) e o catálogo detalhado de [acceptance-catalog.md](references/acceptance-catalog.md).
4. Executar todas as nove suítes aplicáveis do framework: `api`, `openapi`, `business_rules`, `web_quality`, `browser`, `project_quality`, `external_tools`, `performance` e `security`.
5. Manter habilitada em `project_quality` a auditoria de proveniência do código. Procurar declarações explícitas, trailers de coautoria e arquivos de configuração de assistentes; registrar cada ocorrência como indício contextual, nunca como prova de autoria.
6. Executar e registrar os 13 papéis como `complete`, mesmo quando concluírem que um domínio não se aplica. Para suítes, dimensões e testes concretos, usar `complete`, `blocked` ou `not_applicable`; exigir evidência para `complete` e justificativa para os demais.
7. Não encerrar antes de validar o manifesto da auditoria.

## Usar todas as superfícies disponíveis

- Com código, auditar implementação e citar `arquivo:linha`.
- Com especificação ou protótipo, derivar Gherkin e rastreabilidade; marcar implementação não observável como `not_verified`.
- Com diff/PR, revisar a mudança e também os impactos de regressão fora do diff.
- Com sistema executável, realizar jornadas e verificações dinâmicas autorizadas.
- Quando houver mais de uma superfície, cruzar todas elas em vez de escolher apenas um modo.
- Executar cobertura completa por padrão. Reduzir escopo somente quando o usuário pedir explicitamente uma triagem rápida, mantendo no manifesto tudo que não foi executado.

## Fluxo de ponta a ponta

1. Reunir escopo, finalidade, stack, perfis, dados sensíveis, criticidade, ambiente, requisitos, protótipo e restrições. Quando faltar contexto, registrar suposições `SUP-XX` e continuar somente com premissas seguras.
2. Ler [safety.md](references/safety.md), classificar o alvo e separar análise somente leitura de testes ativos. Nunca inferir autorização para carga, scan, injeção, força bruta ou alteração de dados.
3. Criar o manifesto:

   ```bash
   python scripts/init_audit.py <diretorio-de-saida>/audit-manifest.json
   ```

4. Executar descoberta estrutural com `python scripts/discover_project.py <projeto>` e produzir o mapa do sistema antes das análises especializadas.
5. Percorrer as cinco ondas de [qa-orchestration.md](references/qa-orchestration.md). Reaproveitar o mapa; evitar que cada papel faça uma varredura integral duplicada.
6. Derivar casos positivos, negativos, limites, partições, tabelas de decisão, transições, concorrência, idempotência, permissões e jornadas críticas.
7. Gerar ou revisar o YAML do framework. Injetar segredos apenas por mecanismo seguro; nunca gravá-los no plano ou nas evidências.
8. Executar primeiro:

   ```bash
   python scripts/run_framework.py --config <config.yaml> --dry-run
   ```

9. Executar as suítes passivas. Executar as ativas somente após autorização explícita, usando `--authorized` e limites definidos.
10. Confirmar achados críticos, deduplicar ocorrências e relacionar análise estática, execução, requisito e impacto de negócio.
11. Produzir todos os artefatos de [deliverables.md](references/deliverables.md).
12. Preencher o manifesto e validar:

   ```bash
   python scripts/validate_audit.py <diretorio-de-saida>/audit-manifest.json
   ```

13. Se a validação falhar, executar os papéis ou produzir os entregáveis ausentes; para verificações concretas, concluir ou registrar bloqueio/N/A com motivo verificável. Somente então entregar o veredito.

## Regras de evidência

- Exigir `arquivo:linha`, comando de busca e resultado, resposta sanitizada, screenshot, trace, métrica ou passo reproduzível.
- Para ausência, registrar a busca executada e o resultado vazio; não inferir inexistência por amostragem.
- Classificar como `confirmed`, `suspected`, `ambiguity` ou `not_verified` conforme [deliverables.md](references/deliverables.md).
- Consultar pendências, README, TODO e documentos antes de transformar lacuna declarada em achado novo.
- Deduplicar a mesma causa em várias telas e preservar todas as ocorrências.
- Formular pergunta objetiva quando o comportamento correto depender de decisão do cliente.
- Não converter heurística subjetiva de UX, exigência jurídica ou preferência visual em falha confirmada sem requisito, baseline ou avaliação competente.

## Referências por domínio

- Ler [functional-and-rules.md](references/functional-and-rules.md) para regras, API e OpenAPI.
- Ler [interface-ui-ux.md](references/interface-ui-ux.md) para navegador, acessibilidade, responsividade e UX.
- Ler [performance-and-security.md](references/performance-and-security.md) para carga, DAST e ferramentas externas.
- Ler [deliverables.md](references/deliverables.md) antes de consolidar severidade, confiança, quality gate e saídas.

## Códigos de saída do framework

- `0`: execução concluída e gate aprovado.
- `1`: configuração ou execução inválida.
- `2`: gate reprovado.
- `3`: execução bloqueada pela política de segurança.
