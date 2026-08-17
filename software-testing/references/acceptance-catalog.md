# Catálogo de critérios de aceitação

Usar este catálogo para selecionar testes por risco. Marcar cada item como automatizado, manual, não aplicável ou bloqueado, sempre anexando evidência. Não reprovar um sistema por preferência subjetiva sem requisito ou design system aplicável.

## Campos e formulários

- Validar obrigatoriedade, nulos, zero, numéricos, caracteres restritos, tamanho máximo e limites.
- Validar CPF/CNPJ, datas, partições válidas e inválidas e valores colados com Ctrl+V.
- Validar máscaras, indicação visual de obrigatório e mensagens específicas por campo.
- Garantir exclusividade de radio groups e clareza de estados desabilitados.
- Usar afirmações, sem ponto de interrogação, em checkbox e switch quando definido pelo padrão de conteúdo.
- Validar botão limpar, sucesso, erro, confirmação antes de excluir e loading durante processamento.
- Usar ações `validate_field`, `assert_required`, `assert_radio_exclusive`, `assert_disabled` e `assert_clear` nas jornadas de navegador.

## Regras, dados e CRUD

- Cobrir cadastro, consulta, alteração e exclusão, inclusive cancelamento e exceções.
- Usar valores-limite, partições de equivalência, tabelas de decisão e transições de estado.
- Confirmar persistência após reload, histórico, auditoria, usuário, data e hora.
- Comparar dados entre abas, relatórios, sistemas e dicionário de dados.
- Testar dois usuários alterando o mesmo registro e verificar conflito ou política de last-write.
- Validar importação, exportação, upload, download, compressão e arquivos maliciosos.
- Validar permissões por perfil e Broken Access Control no servidor.
- Usar regras declarativas com IDs para manter rastreabilidade.

## Pesquisa, filtros, tabelas e relatórios

- Validar combinações de filtros, substring, limpar filtros e resultados vazios.
- Validar paginação sem repetição ou perda, ordenação e agrupamento de dados repetidos.
- Validar títulos e conteúdos sem cortes, booleanos Sim/Não e listas conforme especificação.
- Medir pesquisas, filtros, lazy loading, cache e grandes volumes.
- Usar `json_assertions`, `assert_filter`, `assert_sorted`, `assert_pagination` e `max_response_ms` em APIs.
- Usar `assert_sorted`, `assert_not_truncated` e `measure_navigation` no navegador.

## UI, UX e conteúdo

- Revisar ortografia, nomenclatura, capitalização, mensagens, ícones e consistência entre telas.
- Comparar layout, alinhamento, molduras e posição com protótipo ou design system fornecido.
- Testar resoluções, responsividade, dark mode, atalhos e compatibilidade entre navegadores.
- Medir tempo de conclusão de tarefas críticas e registrar observação humana quando necessário.
- Tratar conformidade visual e ortografia como revisão humana quando não houver baseline ou glossário.

## Acessibilidade

- Validar WCAG 2.2 AA, teclado, ordem do TAB, foco, contraste, labels, alt, zoom 200% e leitores de tela.
- Executar axe-core local e complementar com verificação manual de teclado e leitor de tela.
- Testar Chromium, Firefox e WebKit conforme matriz de suporte.

## Performance e confiabilidade

- Validar SLA de carregamento, por exemplo menor que 2 segundos quando formalizado.
- Testar carga, stress, spike, endurance, usuários simultâneos e grande volume.
- Monitorar CPU, memória, filas, banco, cache e recursos do sistema.
- Validar timeout, retry, paginação eficiente, lazy loading e tempo de API.
- Comparar com baseline e repetir medições para distinguir regressão de ruído.

## Segurança e privacidade

- Cobrir SQL Injection, XSS, CSRF, CORS, HTTPS, headers, JWT, sessão, logout e login consecutivo.
- Validar política de senha, upload malicioso, IDOR/BOLA e autorização por perfil.
- Mascarar CPF e dados sensíveis em telas, relatórios, logs e evidências.
- Validar LGPD, consentimento, política de privacidade, retenção e auditoria contra requisitos jurídicos fornecidos.
- Tratar conformidade LGPD como avaliação apoiada por evidências, não como certificação automática.

## APIs, integrações e processamento assíncrono

- Validar OpenAPI/Swagger, versionamento, parâmetros, retornos, códigos HTTP e erros padronizados.
- Testar webhooks, filas, processamento assíncrono, duplicidade, retry e idempotência.
- Validar contratos, timeout, indisponibilidade e sincronização com serviços externos.
- Usar mocks quando executar falhas reais puder afetar terceiros.

## Código, observabilidade e governança

- Verificar modularidade, organização, documentação de símbolos públicos e tratamento de erros.
- Detectar testes existentes, cobertura configurada, contratos OpenAPI e artefatos obrigatórios.
- Confirmar logs compreensíveis e sem segredos, monitoramento e evidências anexadas.
- Usar `project_quality` para verificações estáticas e ferramentas externas para SAST, segredos e dependências.

