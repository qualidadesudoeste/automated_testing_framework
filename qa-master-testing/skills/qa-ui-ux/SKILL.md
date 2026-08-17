---
name: qa-ui-ux
description: Auditar UI, UX, conteúdo e linguagem cidadã, cobrindo estados de tela, mensagens, confirmações, responsividade, consistência visual, filtros, exportações, notificações, i18n e facilidade de conclusão de tarefas. Usar como especialista obrigatório do QA Mestre ou para revisão heurística e comparação com protótipo/design system.
---

# Auditar UI e UX

## Verificar

- Oito estados: vazio inicial, vazio filtrado, carregando, parcial, erro recuperável, sem permissão, offline e sucesso persistente.
- Labels visíveis, indicação de obrigatório, ajuda antes do erro, foco no erro, preservação de dados, rascunho, loading e próximo passo.
- Mensagens dizendo o que ocorreu, por quê e como resolver; voz ativa, terminologia única e catálogo `MSG-XXX`.
- Confirmação apenas para irreversível/custoso, consequência no título, verbo no botão, foco seguro, ESC e preferência por desfazer.
- Ortografia, nomenclatura, capitalização, ícones, alinhamento, truncamento, dark mode e aderência ao baseline fornecido.
- Busca/filtro compreensíveis, estado na URL, retorno preservado, contagem e exportação do resultado filtrado.
- CSV/PDF/impressão, protocolo/autenticidade, texto longo, zeros à esquerda e Excel pt-BR.
- Notificações, ambiente de homologação, e-mail/SMS, links, histórico, bounce e opt-out.
- I18n, expansão de texto, locale, `lang`, linguagem simples e instruções para cidadão.
- Tempo, taxa de conclusão e hesitação em tarefas críticas quando houver usuários de teste.

## Entregar

Gravar `agents/qa-ui-ux.json`. Separar defeito mensurável de recomendação heurística. Não reprovar preferência subjetiva sem requisito, protótipo, design system, glossário ou observação humana.
