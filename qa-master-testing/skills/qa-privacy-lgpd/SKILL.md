---
name: qa-privacy-lgpd
description: Avaliar privacidade e controles LGPD de sistemas, cobrindo inventário de dados, finalidade, base legal, minimização, consentimento, direitos do titular, mascaramento, retenção, auditoria e compartilhamento. Usar como especialista obrigatório do QA Mestre ou em revisões de tratamento de dados pessoais, sem substituir parecer jurídico.
---

# Avaliar privacidade e LGPD

## Executar

1. Inventariar dado pessoal/sensível, titular, origem, finalidade, base, acesso, armazenamento, terceiros e retenção.
2. Localizar campo coletado sem uso e uso não declarado; verificar minimização e coleta excessiva.
3. Verificar aviso no ponto de coleta, consentimento granular/revogável quando aplicável e ausência de opção pré-marcada.
4. Verificar acesso, correção, portabilidade, eliminação, oposição e revisão de decisão automatizada conforme requisitos.
5. Verificar mascaramento por perfil, criptografia, ambientes não produtivos anonimizados e cache/log/evidência.
6. Verificar retenção e expurgo implementados, trilha de acesso a dado pessoal e imutabilidade.
7. Mapear compartilhamento, subprocessadores, transferência internacional, menores, saúde, biometria e cookies.
8. Verificar computador compartilhado, `Cache-Control: no-store`, logout/voltar e armazenamento local.

## Entregar

Gravar `agents/qa-privacy-lgpd.json` com dado/finalidade/base/retenção/controle/evidência/risco e perguntas jurídicas. Não declarar certificação ou ilegalidade sem requisito e avaliação competente; marcar ambiguidade.
