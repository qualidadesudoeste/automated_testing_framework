# Orquestração do QA Mestre

Executar todos os papéis abaixo em toda auditoria completa. Paralelizar somente papéis da mesma onda quando houver suporte e quando os escopos forem independentes. Sem paralelismo, executar na ordem apresentada. O QA Mestre continua responsável por acompanhar, revisar e consolidar tudo.

## Onda 0 — mapa compartilhado

1. `system-mapper`: detectar stack; inventariar entidades, tabelas, migrations, rotas, controllers, telas, APIs, estados, perfis, permissões, jobs, integrações, testes e documentos. Produzir o mapa do sistema e suposições `SUP-XX`; não produzir achados.

## Onda 1 — cobertura estrutural

2. `crud-lifecycle`: construir matriz entidade × criar, listar, detalhar, editar, excluir/inativar e restaurar. Verificar duplicidade, órfãos, soft delete, consulta e efeito da inativação.
3. `interactive-ui`: localizar filtros decorativos, botões mortos, busca/ordenação falsas, KPI estático, label enganosa, confirmação ineficaz, estados vazios, feedback e telas órfãs.
4. `roles-access`: ligar perfis e permissões à proteção efetiva de rota, API, download, relatório, exportação e escopo de dados. Verificar primeiro administrador, último administrador e autoexclusão.

## Onda 2 — coerência das regras

5. `state-machines`: reconstruir estados, transições, guardas, reversões, prazos e etapas obrigatórias.
6. `data-integrity`: verificar FKs, unicidade, constraints, cascatas, transações, cálculos, concorrência, idempotência e ciclo de vida.
7. `validation-layers`: comparar cliente, servidor, domínio e banco para obrigatoriedade, tipo, tamanho, faixa, enum, formato e documentos brasileiros.
8. `critical-journeys`: simular primeiro acesso, cadastro completo, operação diária, correção de erro, caminhos alternativos, falhas e recuperação.

## Onda 3 — especialidades

9. `search-reporting`: verificar busca, filtros, URL, retorno do detalhe, ordenação, paginação, ações em massa, exportação, impressão e documentos.
10. `audit-privacy`: verificar logs, histórico, autoria, antes/depois, imutabilidade, minimização, base legal, consentimento, mascaramento, retenção e direitos do titular.
11. `edge-reliability`: testar vazio, extremos, datas, último registro/admin, duas abas, dois usuários, rede instável, sessão expirada, arquivos e integrações indisponíveis.
12. `semantics-accessibility`: verificar nomenclatura, microcopy, mensagens, linguagem cidadã, i18n, labels, teclado, foco, contraste, leitor de tela, zoom e reflow.

## Onda 4 — consolidação

13. `consolidator`: reunir achados estáticos e dinâmicos; deduplicar causa raiz; calibrar severidade e confiança; relacionar requisitos e casos; calcular cobertura; produzir entregáveis e validar o manifesto.

## Contrato de cada papel

- Consumir o mapa do sistema e limitar a leitura ao próprio escopo.
- Buscar antes de abrir arquivos extensos; ignorar dependências, builds, caches, minificados e arquivos gerados.
- Registrar evidência positiva ou negativa. Achado de ausência exige consulta reproduzível com resultado vazio.
- Verificar pendências conhecidas antes de reportar uma lacuna.
- Entregar no máximo 12 achados prioritários por papel; registrar a quantidade excedente para triagem posterior.
- Não editar o produto durante auditoria, salvo quando o usuário pedir explicitamente correções após o relatório.
- Não executar ações ativas sem autorização e limites operacionais.

## Condição de conclusão

Concluir somente quando os 13 papéis estiverem `complete` com evidência no manifesto. Um papel que conclui que seu domínio não se aplica ainda foi executado e deve registrar essa conclusão como evidência. A indisponibilidade de agentes auxiliares muda apenas a forma de execução, não a cobertura.
