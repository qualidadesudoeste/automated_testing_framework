---
name: qa-business
description: Auditar coerência de negócio, CRUD, ciclo de vida, perfis, estados, jornadas e operação real, detectando telas e processos que não fecham o fluxo mesmo quando o código funciona tecnicamente. Usar como especialista obrigatório do QA Mestre ou isoladamente em homologação funcional e análise de regras.
---

# Auditar negócio

Consumir `SYSTEM_MAP.md`, requisitos e pendências. Não inventar regra; classificar decisão ausente como ambiguidade e formular pergunta objetiva.

## Verificar

- Matriz entidade × criar, listar, detalhar, editar, excluir/inativar e restaurar.
- Cadastro-fantasma, registro imortal, exclusão cega, edição amputada, soft delete inconsistente, duplicidade, órfão, cadastro sem consulta e inativação sem efeito.
- Filtro/botão/ordenação/busca/KPI/label/confirmacão decorativos, estado vazio e feedback.
- Gestão de perfis, permissão aplicada, menu versus rota, primeiro/último administrador, autodestruição e escopo por órgão.
- Estados inalcançáveis, terminais precoces, transições sem guarda, prazos sem motor, regra só documentada, ação sem reversão e ordem quebrada.
- Dependência circular, beco sem saída, pré-requisito invisível, obrigatoriedade invertida, caminhos divergentes, perda de contexto e tela órfã.
- Primeiro acesso, cadastro completo, operação diária, correção de erro e processo de ponta a ponta.
- Paginação, ações em massa, concorrência, histórico, anexos, auditoria consultável e operação em volume real.

## Evidência e saída

Para ausência, registrar busca e resultado vazio. Separar pendência conhecida de achado novo. Gravar `agents/qa-business.json` com taxonomia `A01–H06`, impacto em linguagem de gestor, critério BDD, confiança e ocorrências deduplicadas.
