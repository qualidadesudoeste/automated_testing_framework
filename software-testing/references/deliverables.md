# Evidências, classificação e entregáveis

## Severidade canônica

- `critical` (`P0`/bloqueante): vazamento, acesso indevido relevante, corrupção/perda, indisponibilidade importante ou ilegalidade explícita; bloquear entrega.
- `high` (`P1`/alta): regra essencial violável, validação de segurança ausente ou retrabalho obrigatório; corrigir na sprint atual.
- `medium` (`P2`/média): fricção relevante, inconsistência ou alternativa limitada; planejar próxima sprint.
- `low` (`P3`/baixa): problema localizado/cosmético ou dívida com impacto pequeno.
- `info`: observação, oportunidade ou item não verificado sem falha demonstrada.

Registrar também esforço `XS/S/M/L`, quick win e prioridade. Não inflar severidade pelo nome da categoria; usar impacto, alcance, probabilidade, explorabilidade e evidência.

## Confiança

- `confirmed`: evidência direta ou reprodução bem-sucedida.
- `suspected`: indício forte ainda dependente de contexto ou confirmação dinâmica.
- `ambiguity`: resultado correto depende de decisão do cliente; incluir pergunta objetiva.
- `not_verified`: não foi possível testar; não implica aprovação.

## Formato mínimo do achado

- ID `QA-XXX`, título orientado à ação, dimensão e facetas PN.
- Severidade, confiança, esforço e quick win.
- Entidade/tela e todas as ocorrências.
- Evidência sanitizada com `arquivo:linha`, busca negativa ou artefato reproduzível.
- Comportamento atual, impacto em linguagem de negócio e comportamento esperado.
- Como comprovar, correção sugerida e teste de regressão.
- Critério de aceite BDD; pergunta quando ambíguo.

Durante auditoria, não alterar o produto. Incluir solução técnica ou trecho ilustrativo quando útil, mas somente implementar correções se o usuário solicitar uma etapa de remediação.

## Artefatos obrigatórios

O diretório de saída fica **sempre fora do repositório do projeto auditado** — nunca na raiz nem
em subpastas do projeto-alvo, e nunca versionado junto com o código testado (`init_audit.py`/
`init_run.py` exigem `--project-root` e recusam qualquer saída dentro dele). Produzir no
diretório de saída:

1. `EXECUTIVE_REPORT.md`: veredito `release`, `release_with_caveats` ou `do_not_release`, três maiores riscos, placar, top 10 e menor conjunto de correções para tornar o processo operável.
2. `FINDINGS.json` e `FINDINGS.csv`: achados deduplicados, UTF-8; CSV para Excel pt-BR usa `;` e BOM.
3. `TEST_CASES.feature`: cenários Gherkin em pt-BR para regras e fluxos críticos.
4. `TRACEABILITY.csv`: requisito/regra, origem, implementação, caso, execução, evidência e status.
5. `MESSAGE_CATALOG.csv`: código, tipo, contexto, texto e canal.
6. `ACTION_PLAN.md`: bloqueadores, quick wins, sprint 1, sprint 2 e backlog com critérios BDD.
7. `PENDING.md`: não verificados, bloqueios, ambiguidades, opções, recomendação e premissa.
8. `SYSTEM_MAP.md`: mapa compartilhado produzido pelo papel `system-mapper`.
9. `audit-manifest.json`: cobertura dos papéis, suítes, dimensões e testes adversariais.
10. Relatórios do framework em HTML/JSON/JUnit/SARIF e diretório de evidências quando gerados.

## Quality gate

- Reprovar com qualquer `critical` confirmado.
- Reprovar conforme limite configurado de `high` confirmado.
- Não aprovar auditoria com item `pending` no manifesto.
- Bloqueios e N/A não desaparecem do denominador: publicar cobertura executada, bloqueada e não aplicável separadamente.
- Declarar ferramentas ausentes, ambiente, massa, perfis, navegadores e integrações não cobertos.
