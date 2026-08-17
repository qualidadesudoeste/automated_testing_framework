---
name: qa-master
description: Orquestrar e executar uma auditoria completa de software por meio de 13 skills especialistas reais, cobrindo mapeamento, negócio, funcional, API, interface, UI/UX, acessibilidade, performance, segurança, LGPD, código, integrações e consolidação. Usar quando o usuário pedir teste completo, homologação, auditoria de sistema, revisão ampla ou execução de todas as especialidades com um único ponto de entrada.
---

# Executar QA Mestre

Assumir responsabilidade integral pela auditoria. Não pedir ao usuário que invoque, acompanhe ou consolide especialistas.

## Regra central

Executar obrigatoriamente todos os 13 especialistas abaixo como subagentes reais. Não substituir a execução por uma simulação ou por uma lista de papéis. Se o ambiente não oferecer mecanismo de subagentes, informar que a execução multiagente não pode ser cumprida; não declarar auditoria completa.

Tratar [prompt-qa-master-complete.md](references/prompt-qa-master-complete.md) e [prompt-qa-business-complete.md](references/prompt-qa-business-complete.md) como fontes normativas integrais. Usar [source-traceability.md](references/source-traceability.md) para localizar cada obrigação e resolver conflitos. Nenhum resumo autoriza descartar uma regra da fonte.

1. `$qa-system-mapper`
2. `$qa-business`
3. `$qa-functional`
4. `$qa-api`
5. `$qa-interface`
6. `$qa-ui-ux`
7. `$qa-accessibility`
8. `$qa-performance`
9. `$qa-security`
10. `$qa-privacy-lgpd`
11. `$qa-code-quality`
12. `$qa-integrations`
13. `$qa-consolidator`

## Fluxo obrigatório

1. Reunir todos os campos de entrada das duas fontes: projeto/URL, finalidade, stack, escopo, perfis, dados sensíveis, criticidade, público, obrigações, ambiente, artefatos, prazo, contexto de negócio, documentos, entidades, fora de escopo, credenciais seguras e autorização. Registrar lacunas como `SUP-XX` ou bloqueios; nunca inventar requisito.
2. Selecionar o eixo de superfície A–D e a profundidade rápido/padrão/profundo. Usar todas as superfícies disponíveis e `PROFUNDO` por padrão. Reduzir somente por pedido explícito e nunca rotular execução reduzida como auditoria completa.
3. Ler [safety.md](references/safety.md), [quality-catalog.md](references/quality-catalog.md), [business-taxonomy.md](references/business-taxonomy.md), [acceptance-catalog.md](references/acceptance-catalog.md), [coverage-routing.md](references/coverage-routing.md), [source-traceability.md](references/source-traceability.md) e [deliverables.md](references/deliverables.md). Distribuir todas as obrigações conforme o roteamento.
4. Resolver a raiz do plugin e criar a execução com `python <plugin-root>/scripts/init_run.py <run-dir> --surface <auto|A|B|C|D> --depth <rapido|padrao|profundo>`.
5. Reaproveitar mapa anterior somente após verificar ausência de mudança estrutural; caso contrário, disparar `$qa-system-mapper` sozinho e esperar suas saídas.
6. Disparar `$qa-business`, `$qa-functional`, `$qa-api` e `$qa-code-quality` como subagentes independentes. Esperar todos.
7. Se a primeira onda revelar mais de 30 críticos/bloqueantes, acionar o gate de imaturidade: interromper aprofundamento ativo/caro, mas ainda chamar os especialistas restantes para triagem e registro de bloqueios.
8. Disparar `$qa-interface`, `$qa-ui-ux`, `$qa-accessibility`, `$qa-performance`, `$qa-security`, `$qa-privacy-lgpd` e `$qa-integrations`. Paralelizar conforme os limites, iniciar todos e esperar todos.
9. Executar testes ativos somente após autorização explícita. Um bloqueio não autoriza omitir o agente: concluir análise passiva e registrar condição de retomada.
10. Conferir com `python <plugin-root>/scripts/check_run.py <run-dir>` se os 12 resultados e toda a cobertura existem.
11. Disparar `$qa-consolidator` com mapa, resultados e artefatos. Exigir as saídas originais e ampliadas.
12. Executar `python <plugin-root>/scripts/check_run.py <run-dir> --final`. Corrigir lacunas antes de responder.

## Contrato de chamada

Incluir em cada tarefa de especialista:

- caminho absoluto do projeto e do diretório da execução;
- escopo, contexto de negócio, perfis, ambiente e fora de escopo;
- caminho de `SYSTEM_MAP.md` após o mapeamento;
- autorização e limites para testes ativos;
- instrução para usar a skill nomeada e gravar apenas no arquivo de saída atribuído;
- contrato `<plugin-root>/assets/agent-output.schema.json`, exigindo `status: complete` do agente e cobertura interna marcada como completa, bloqueada ou não aplicável;
- IDs de cobertura atribuídos: `D01–D25`, `ADV01–ADV24`, `SUITE:<nome>`, `SOURCE:AI-PROVENANCE` e `SRC:MASTER:0–9`/`SRC:BUSINESS:0–9`; garantir que a união dos 12 especialistas contenha todos os IDs;
- proibição de alterar o produto durante a auditoria.
- busca antes da leitura, máximo de 40 arquivos por passagem e exclusão de dependências/builds/caches/minificados;
- limite de 12 achados prioritários na resposta do agente, com contagem e inventário dos excedentes;
- obrigação de separar pendência conhecida, ambiguidade, suspeita e não verificado;
- correção técnica concreta, incluindo código na stack quando houver evidência, sem aplicar a alteração no produto.

## Garantias

- Esperar todos os agentes; não consolidar resultado parcial como completo.
- Exigir evidência para achado confirmado e motivo para não verificado/N/A.
- Preservar resultados divergentes para o consolidador decidir, sem apagar evidência.
- Nunca permitir que dois agentes escrevam o mesmo arquivo.
- Sanitizar tokens, cookies, CPF e outros dados pessoais nas evidências.
- Entregar cobertura executada, bloqueada e não aplicável separadamente.

## Framework determinístico

Os especialistas funcionais e técnicos devem usar `python <plugin-root>/scripts/run_framework.py` com as suítes sob sua responsabilidade. Sempre executar `--dry-run` primeiro. `--authorized` só pode ser usado com autorização explícita e escopo controlado.
