---
name: qa-consolidator
description: Consolidar resultados de todos os agentes QA e do framework em um veredito único, deduplicando causas, calibrando severidade e confiança, calculando cobertura e gerando relatórios, Gherkin, rastreabilidade, mensagens e plano de ação. Usar somente depois que os outros 12 especialistas concluírem.
---

# Consolidar a auditoria

Recusar consolidação final quando faltar qualquer um dos 12 resultados especialistas. Não reinterpretar ausência como aprovação.

## Consolidar

1. Ler `SYSTEM_MAP.md`, todos os `agents/*.json`, relatórios do framework e evidências.
2. Deduplicar por causa raiz; manter dimensões, taxonomias e ocorrências como facetas.
3. Resolver divergências preservando as evidências e reduzindo confiança quando necessário.
4. Classificar severidade: `critical`, `high`, `medium`, `low`, `info`; confiança: `confirmed`, `suspected`, `ambiguity`, `not_verified`.
5. Exigir impacto de negócio, esperado, observado, reprodução, correção sugerida, regressão, esforço e quick win.
6. Calcular cobertura executada, bloqueada e N/A para agentes, suítes, dimensões, perfis, navegadores e ambientes.
7. Aplicar gate: crítico confirmado bloqueia; altos seguem threshold; item faltante impede aprovação completa.

## Entregar

- `EXECUTIVE_REPORT.md`: veredito, três riscos, placar, top 10 e menor conjunto para operar.
- `FINDINGS.json` e `FINDINGS.csv` deduplicados; CSV UTF-8 BOM e `;`.
- `TEST_CASES.feature` em Gherkin pt-BR.
- `TRACEABILITY.csv` de regra → origem → implementação → caso → execução → evidência.
- `MESSAGE_CATALOG.csv`.
- `ACTION_PLAN.md` com bloqueadores, quick wins, sprint 1/2 e backlog.
- `PENDING.md` com bloqueios, ambiguidades, opções, recomendação e premissa.
- `PENDENCIAS.md` conforme a entrega da referência Mestre.
- `AUDITORIA_NEGOCIO.md`, `ACHADOS_NEGOCIO.csv`, `PENDENCIAS_NEGOCIO.md` e `MAPA_SISTEMA.md` conforme a referência de Negócio, além das visões ampliadas acima.
- `audit-manifest.json` final e referências aos relatórios HTML/JSON/JUnit/SARIF.

Gravar `agents/qa-consolidator.json` como recibo da consolidação e somente então permitir a validação final do QA Mestre.
