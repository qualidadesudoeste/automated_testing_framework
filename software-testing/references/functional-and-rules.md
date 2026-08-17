# Testes funcionais, API e regras

- Derivar cenários positivos, negativos, limites, ausência de dados, duplicidade, concorrência e transições de estado.
- Rastrear cada regra com um identificador e registrar esperado, observado e fonte do requisito.
- Para APIs, validar método, status, headers, schema, autorização, paginação, idempotência e compatibilidade.
- Declarar regras no YAML com `id`, `endpoint`, `path`, `operator` e `expected`. Usar também `matches`, `starts_with`, `ends_with`, `between`, `length_eq`, `is_null`, `not_null`, `sorted_asc`, `sorted_desc` e `unique` quando aplicável.
- Usar somente operadores suportados; nunca avaliar expressões arbitrárias recebidas da configuração.
- Cobrir permissões por perfil e confirmar que a negação ocorre no servidor, não apenas na interface.
- Para OpenAPI 3.x, configurar `openapi.spec`. A suíte executa automaticamente apenas operações GET sem parâmetros de caminho, valida status declarados e schemas JSON; operações mutáveis exigem casos explícitos.
