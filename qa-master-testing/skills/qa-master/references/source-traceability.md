# Rastreabilidade integral dos prompts-fonte

Esta matriz torna as duas referências completas normativas e demonstra onde cada seção é executada. Os resumos da skill ajudam a navegação, mas não substituem as fontes.

## Referência Mestre

| Seção | Conteúdo | Implementação |
|---|---|---|
| 0 | Contexto completo | Entrada obrigatória do `qa-master` e `run-manifest.json` |
| 1 | QA, segurança, privacidade, acessibilidade, UX e arquitetura | Skills especialistas correspondentes |
| 2 | Modos A–D | Seleção de superfície no `qa-master`; combinar modos quando houver vários artefatos |
| 3 | Oito regras de execução | Contrato do mestre e de todos os subagentes |
| 4 | P0–P3, esforço e quick win | `qa-consolidator`, com mapeamento de escalas abaixo |
| 5 / D1–D25 | Todas as dimensões e checklists | `quality-catalog.md`, `coverage-routing.md` e especialistas proprietários |
| 6 | 24 testes adversariais | IDs ADV01–ADV24 e agentes funcional, interface e segurança |
| 7 | Oito blocos da entrega | `qa-consolidator` e entregáveis expandidos |
| 8 | Versão curta | Perfil de invocação rápida, sem remover obrigações do manifesto |
| 9 | Smoke de 10 minutos | Interface, UI/UX, performance e segurança; saída separada |

## Referência de Negócio

| Seção | Conteúdo | Implementação |
|---|---|---|
| 0 | Entrada de escopo e contexto | Entrada do `qa-master`; suposições `SUP-XX` quando necessário |
| 1 | Seis regras invioláveis | Contrato de evidência, somente leitura e deduplicação |
| 2 | Taxonomia A01–H06 | `business-taxonomy.md` e `qa-business` |
| 3 | Severidade e confiança | `qa-consolidator`, com mapeamento abaixo |
| 4 | 13 responsabilidades e cinco ondas | Mapeamento de responsabilidades abaixo e ondas do `qa-master` |
| 5 | Briefing dos subagentes | Contrato de chamada do `qa-master` |
| 6 | Formato completo do achado | Schema dos agentes e consolidador |
| 7 | Quatro entregáveis originais | Gerados junto dos entregáveis ampliados |
| 8 | Custos, reaproveitamento e limite de maturidade | Controles obrigatórios do `qa-master` |
| 9 | Checklist de encerramento | `check_run.py` e validação do consolidador |

## Responsabilidades originais preservadas

| Responsabilidade original | Skills atuais responsáveis |
|---|---|
| mapeador | `qa-system-mapper` |
| crud-matrix | `qa-business`, revisão por `qa-functional` |
| ui-interativa | `qa-interface`, `qa-ui-ux` |
| perfis-acesso | `qa-business`, `qa-security` |
| estados | `qa-business`, `qa-functional` |
| integridade-dados | `qa-functional`, `qa-code-quality` |
| validação | `qa-functional` |
| jornadas | `qa-business`, `qa-interface` |
| consulta-listagem | `qa-api`, `qa-interface`, `qa-ui-ux` |
| auditoria-lgpd | `qa-privacy-lgpd`, `qa-code-quality` |
| casos-limite | `qa-functional`, `qa-interface`, `qa-performance`, `qa-security` |
| semântica | `qa-ui-ux`, `qa-accessibility` |
| consolidador | `qa-consolidator` |

## Resolução de conflitos sem perda

| Conflito | Regra combinada |
|---|---|
| Auditoria somente leitura × correção com código | Não editar o produto durante auditoria; incluir correção concreta e trecho de código na stack quando houver evidência suficiente. Implementar somente em etapa de remediação solicitada. |
| P0–P3 × BLOQUEANTE–BAIXA × critical–info | Preservar a classificação original e registrar também a canônica: P0/BLOQUEANTE/CRÍTICA→critical; P1/ALTA→high; P2/MÉDIA→medium; P3/BAIXA→low; observação→info. |
| Quatro entregáveis × conjunto ampliado | Produzir ambos. Os quatro originais são visões específicas de negócio; os ampliados cobrem técnica, automação e CI. |
| Modos A–D × rápido/padrão/profundo | Tratar como eixos independentes: A–D define a superfície; rápido/padrão/profundo define profundidade. Padrão do plugin: todas as superfícies disponíveis + profundo. |
| Rápido/padrão reduzem agentes × exigência de executar todos | Usar profundo por padrão. Se o usuário pedir redução, preservar as estimativas originais, mas registrar agentes não executados no manifesto e não chamar o resultado de auditoria completa. |
| Parar com mais de 30 críticos × executar todos | Acionar gate de imaturidade: parar testes ativos/caros, chamar os agentes restantes para triagem baseada no mapa e registrar bloqueios; não ocultar nenhum agente. |
| Não parar por falta de informação × segurança operacional | Continuar análises passivas com `SUP-XX`; bloquear apenas ação ativa insegura e registrar condição para retomada. |

## Controles que não podem desaparecer

- Buscar antes de ler; ignorar dependências, builds, caches, minificados e testes quando o papel exigir análise de produção.
- Limitar cada especialista a 40 leituras de arquivo por passagem; sinalizar ao atingir o limite.
- Entregar até 12 achados prioritários por agente e registrar quantos ficaram fora, sem perder o inventário para o consolidador.
- Reaproveitar `MAPA_SISTEMA.md` quando não houver mudança estrutural, registrando a origem e validade.
- Interromper aprofundamento caro quando a primeira onda revelar mais de 30 críticos/bloqueantes.
- Produzir evidência negativa para ausência e separar pendências conhecidas da contagem.
