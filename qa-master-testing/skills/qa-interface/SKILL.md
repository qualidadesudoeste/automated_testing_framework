---
name: qa-interface
description: Executar testes funcionais de interface e jornadas E2E reais em navegador, cobrindo formulários, CRUD, estados, filtros, persistência, upload, download, confirmação, teclado, responsividade básica e compatibilidade multi-browser. Usar como especialista obrigatório do QA Mestre ou em validação de fluxos web.
---

# Testar interface e jornadas

## Executar

1. Priorizar fluxo principal, primeiro acesso, operação diária, caminhos alternativos, erro e recuperação.
2. Testar formulários: obrigatório, máscara, válido/inválido, mensagens por campo, radio exclusivo, desabilitado, limpar, loading, duplo clique, preservação e aviso ao sair.
3. Testar CRUD, confirmação/undo, feedback, persistência após reload, histórico e permissões por perfil.
4. Testar busca, filtros, limpar, vazio, ordenação, paginação, voltar mantendo contexto e ações em massa.
5. Testar upload/download, importação/exportação e conteúdo longo sem truncamento.
6. Executar Chromium, Firefox e WebKit conforme matriz; cobrir 360px, 768px, 1366×768 e desktop amplo.
7. Gerar configuração e executar `browser` e `web_quality` após `--dry-run`; usar seletores estáveis, screenshots e traces.

## Entregar

Gravar `agents/qa-interface.json` e evidências em diretório exclusivo. Para cada falha, incluir jornada, perfil, passos, esperado, observado, navegador, viewport e artefato.
