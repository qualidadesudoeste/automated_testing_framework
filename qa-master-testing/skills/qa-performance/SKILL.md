---
name: qa-performance
description: Planejar e executar testes de performance e confiabilidade, incluindo frontend, APIs, carga, stress, spike, endurance, concorrência, filas e recursos, com baseline e thresholds objetivos. Usar como especialista obrigatório do QA Mestre ou para investigar lentidão, escala e capacidade.
---

# Testar performance e confiabilidade

## Segurança operacional

Exigir autorização explícita, ambiente controlado, janela, usuários, workers, duração, allowlist, contato e critério de interrupção. Não executar carga em produção por inferência.

## Executar

- Definir cenário real, baseline e orçamento antes de medir; registrar aquecimento e repetição.
- Medir P50/P95/P99, erro, throughput e saturação; correlacionar com CPU, memória, banco, cache, filas e dependências.
- Separar carga, stress, spike e endurance; testar pico de prazo e volume representativo.
- Medir SLA de API, concorrência, pool, timeout, retry/backoff, circuit breaker e idempotência.
- Medir LCP, INP, CLS, bundle, imagens, cache e rede móvel com Lighthouse quando disponível.
- Inspecionar N+1, índices de WHERE/ORDER/JOIN, paginação, debounce, virtualização e exportação em fila.
- Executar `performance` e adaptadores k6/Lighthouse de `external_tools` após `--dry-run` e autorização.

## Entregar

Gravar `agents/qa-performance.json` com ambiente, massa, cenário, amostras, percentis, threshold, baseline, erro, recursos, limitações e artefatos. Não reduzir resultado a um score único.
