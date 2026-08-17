---
name: qa-integrations
description: Auditar integrações, filas, webhooks, notificações, serviços externos e observabilidade, cobrindo contrato, timeout, retry, idempotência, falha, reprocessamento, sincronização e comunicação ao usuário. Usar como especialista obrigatório do QA Mestre ou para validar ecossistemas distribuídos.
---

# Testar integrações e processamento assíncrono

## Executar

- Mapear produtor, consumidor, protocolo, schema, autenticação, dado pessoal, SLA e proprietário.
- Validar timeout, retry com backoff/limite, circuit breaker, idempotência, deduplicação e ordem.
- Testar indisponibilidade, resposta lenta, contrato incompatível, payload inválido, duplicado, replay e recuperação.
- Verificar DLQ, reprocessamento, poison message, concorrência, consistência eventual e reconciliação.
- Verificar webhook: assinatura, timestamp, replay, allowlist, resposta, retry e observabilidade.
- Verificar sincronização, conflito, estado parcial e comunicação clara ao usuário.
- Verificar notificações em fila, não envio real em homologação, template, link/token, bounce, opt-out e histórico.
- Verificar logs sanitizados, correlation ID, healthcheck, métricas, alertas e trilha auditável.
- Usar mocks/fakes quando falhar o terceiro real puder causar impacto ou custo.

## Entregar

Gravar `agents/qa-integrations.json` com integração, cenário, contrato, esperado, observado, evidência, retry/reprocessamento e impacto.
