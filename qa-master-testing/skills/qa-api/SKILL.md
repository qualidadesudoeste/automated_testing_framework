---
name: qa-api
description: Planejar e executar testes de APIs e contratos OpenAPI, incluindo autenticação, autorização, schemas, erros, filtros, ordenação, paginação, SLA, concorrência, idempotência, versionamento, webhooks e compatibilidade. Usar como especialista obrigatório do QA Mestre ou para auditorias de serviços e integrações HTTP.
---

# Testar API e contratos

## Executar

- Inventariar operações e comparar implementação com OpenAPI/Swagger.
- Validar método, status, headers, content type, schema, campos obrigatórios, tipos, enums e erro padronizado.
- Testar autenticação, escopo, IDOR/BOLA, mass assignment e negação no servidor.
- Testar query, busca com acento/caixa, documentos com/sem máscara, filtros combinados, ordenação estável e paginação sem perda/repetição.
- Validar timeout, SLA, retry, idempotência, concorrência, rate limit, versionamento e backward compatibility.
- Cobrir webhooks, callback, assinatura, replay, duplicidade, filas e indisponibilidade de terceiros usando mocks quando necessário.
- Gerar configuração e executar `api` e `openapi` após `--dry-run`. Requisições mutáveis exigem autorização e massa descartável.

## Entregar

Gravar `agents/qa-api.json` com operação, contrato, entrada sanitizada, esperado, observado, tempo, evidência e reprodução. Incluir lacunas da especificação separadas de violações confirmadas.
