# Interface, UI/UX e acessibilidade

- Automatizar jornadas críticas com Playwright e seletores estáveis orientados a papel ou test-id.
- Registrar screenshot e trace quando uma jornada falhar.
- Testar teclado, foco, labels, idioma, headings, contraste, zoom e estados de erro.
- Cobrir breakpoints móveis e desktop, overflow, truncamento e mudança de orientação.
- Validar loading, vazio, sucesso, falha, prevenção de erro e recuperação.
- Tratar heurísticas de UX como recomendações até existir requisito mensurável ou validação humana.
- Usar baseline aprovada para regressão visual e tolerância documentada para conteúdo dinâmico.
- Configurar `engines` para Chromium, Firefox e WebKit conforme o risco. Usar `axe_script` com uma cópia local de `axe.min.js`; não carregar auditoria de acessibilidade de CDN durante o teste.
- Atualizar baseline somente em execução deliberada e revisar o diff antes de aprovar a mudança.
