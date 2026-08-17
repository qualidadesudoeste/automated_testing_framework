# Catálogo integral de qualidade

Avaliar cada dimensão como `complete`, `blocked` ou `not_applicable`. Registrar evidência ou justificativa no manifesto. Adaptar exigências legais e de domínio ao contexto; não declarar conformidade jurídica automática.

## D01 — validação em quatro camadas

Comparar cliente, contrato do servidor, domínio e banco para cada campo/regra: obrigatoriedade, tipo, tamanho, faixa, formato, enum, unicidade e constraints. Testar requisição direta sem JavaScript e impedir corrida em unicidade.

## D02 — autenticação e sessão

Verificar senha, MFA administrativo, rate limit, enumeração por mensagem/tempo, recuperação de uso único, fixation, timeout com aviso, renovação, logout no servidor, cookies seguros, sessões ativas e SSO com assinatura, `state`, `nonce` e redirect allowlist.

## D03 — autorização

Testar IDOR/BOLA em IDs, escalada horizontal/vertical, Policy/Gate/middleware, mass assignment, escopo por órgão, ações em massa, exportações, relatórios, APIs, webhooks, preview e downloads. Menu oculto nunca substitui proteção do servidor.

## D04 — injeção e execução

Cobrir SQLi em filtros/ordenação, XSS refletido/armazenado/DOM, CSV formula injection, command/SSTI/LDAP/XXE, open redirect, desserialização insegura e SSRF. Usar payloads não destrutivos e alvo autorizado.

## D05 — upload e arquivos

Validar magic bytes, allowlist, tamanho, quantidade, nome/path traversal, armazenamento fora do webroot, SVG/PDF ativo, ZIP bomb, polyglot, quarentena, headers de download, autorização, progresso, cancelamento, falha de rede e limpeza de órfãos.

## D06 — configuração e infraestrutura

Verificar debug, arquivos sensíveis expostos, segredos e rotação, CSP/HSTS/frame protection/nosniff/referrer/permissions, CORS, CSRF, TLS, verbos HTTP, rate limit, CVEs e logs sem dados pessoais.

## D07 — LGPD e privacidade

Verificar minimização, finalidade, base legal, consentimento granular/revogável, aviso no ponto de coleta, direitos do titular, mascaramento por perfil, criptografia, dados anonimizados fora de produção, retenção/expurgo, trilha de acesso, compartilhamento, menores/sensíveis e cookies. Tratar como avaliação baseada em requisitos, não certificação.

## D08 — regras de negócio

Rastrear `RN-XX`; criar tabelas de decisão, valores-limite e máquinas de estado; testar concorrência, idempotência, chave natural, decimal/arredondamento, datas/fuso/dias úteis, transação atômica, relógio congelado e sequências sem colisão.

## D09 — dados brasileiros

Validar máscara, dígito verificador, normalização e exibição para CPF, CNPJ conforme norma vigente, CEP, telefone, datas, moeda, percentuais, RG, PIS/PASEP, título, CNH, Renavam, placa, processo CNJ, inscrições, NF-e, matrícula e INEP quando aplicáveis. Testar colar formatado/limpo, backspace, cursor, teclado móvel, autofill, trim, caixa, acentos, `ç`, apóstrofo, nomes extremos e UTF-8.

## D10 — UX de formulários

Validar label visível, indicador consistente, erro no blur e limpeza após correção, erro junto ao campo e resumo, foco no primeiro erro, ajuda anterior, bloqueio de duplo clique, loading explicado, mapeamento de erro do servidor, preservação de dados, aviso de alteração não salva, rascunho, TAB/Enter/fieldset, campos condicionais, autocomplete e confirmação específica com próximo passo.

## D11 — oito estados de interface

Cobrir vazio inicial, vazio após filtro com limpar, carregando sem layout shift, parcial, erro com recuperação, sem permissão explicado, offline/rede instável e sucesso persistente.

## D12 — mensagens e confirmações

Informar o que ocorreu, por quê e como resolver; usar voz ativa, linguagem simples, catálogo `MSG-XXX` e terminologia consistente. Usar canal/persistência adequados. Confirmar apenas ação irreversível/custosa; título e botão devem dizer a consequência/verbo; ação destrutiva não recebe foco inicial; ESC cancela; operação catastrófica exige confirmação reforçada; preferir desfazer quando reversível.

## D13 — acessibilidade

Cobrir WCAG 2.2 AA/eMAG aplicável: contraste, não depender só de cor, teclado, foco, skip link, landmarks, headings, labels, `aria-describedby`, `aria-invalid`, `aria-live`, modal acessível, tabelas, alt, nome de ícone, autocomplete, reduced motion, zoom 200%, reflow 320px, alvo de toque e teste real com leitor de tela.

## D14 — responsividade, performance e dados

Testar 320, 360, 768, 1024, 1366×768, 1440 e 1920; teclado virtual, rotação, notch e impressão. Medir LCP/INP/CLS, N+1, índices, paginação, debounce, virtualização, fila de exportação, bundle, imagens e cache. Verificar tipos, precisão, FK, delete, migrations, seeds, backup/restauração e importação linha a linha.

## D15 — integrações e observabilidade

Verificar timeout, retry/backoff, circuit breaker, idempotência, falha visível/reprocessável, schema de contrato, log sanitizado, correlation ID, trilha imutável/exportável, healthcheck, métricas de fila e alertas.

## D16 — automação

Avaliar pirâmide, cobertura por regra, autorização por rota, validação server-side, factories BR válidas, concorrência, idempotência, E2E crítico, axe no CI, regressão por bug e gate de merge.

## D17 — busca, filtro, ordenação e paginação

Testar caixa/acento, parcial/múltiplas palavras, documentos com/sem máscara, caracteres especiais sem wildcard/injeção, persistência ao voltar, filtros combinados/chips/limpar, estado na URL, contagem, ordenação estável pt-BR, páginas-limite, reset por filtro, tamanho persistido, seleção em massa e exportação do resultado filtrado.

## D18 — exportação, impressão e documentos

Validar CSV UTF-8 BOM e `;`, documentos como texto para preservar zeros, datas/moedas, escape, fórmula, volume em fila e expiração. Em PDF/comprovante: protocolo, fuso, órgão, autenticidade/QR, assinatura quando exigida, paginação, texto longo, fonte/acentos, acessibilidade e CSS de impressão.

## D19 — notificações

Impedir homologação de contatar cidadão real. Verificar fila/retry, idempotência, templates em clientes reais, links absolutos e tokens, minimização de dados, SPF/DKIM/DMARC, assunto/remetente, bounce, opt-out, SMS e histórico de notificações in-app.

## D20 — internacionalização e linguagem cidadã

Verificar strings, fallback de tradução, plural/gênero, expansão 20–35%, locale, persistência de idioma, conteúdo dinâmico, `lang`, linguagem simples, glossário/ajuda e instruções com documentos, tempo e prazo.

## D21 — formulário público e antiabuso

Cobrir honeypot, rate limit, tempo mínimo e captcha acessível; antienumeração; protocolo e comprovante; consulta com dois conhecimentos; reenvio; rascunho sem dado sensível; prazo pelo servidor; mensagem de janela; progresso e continuação.

## D22 — ambiente real

Testar matriz de navegadores e máquinas institucionais, 1366×768, Android econômico/3G, computador compartilhado com `no-store`, logout/voltar, zoom 125/150%, proxy/extensões/CSP e funcionamento sem CDN externa.

## D23 — migração e legado

Reconciliar contagens; tratar dados inválidos/duplicados explicitamente; versionar de-para; validar encoding; preservar sequências; tornar carga idempotente; ensaiar volume; definir rollback/congelamento e amostra homologada pelo negócio.

## D24 — release e continuidade

Verificar migration expand/contract, aba antiga após deploy, rollback testado, manutenção comunicada, carga de pico real, monitoramento pós-deploy, critério de reversão, plano operacional alternativo e feature flags.

## D25 — governança

Produzir matriz de risco, DoR/DoD, critério de saída, massa representativa anonimizada, roteiro de homologação, aceite ligado à versão, bug bash, teste com cinco usuários quando aplicável, regressão/causa raiz e documentação de suporte. Auditar assinaturas e artefatos de autoria automatizada, separando indício contextual de prova.

## Testes adversariais obrigatórios

Registrar `ADV01` a `ADV24` no manifesto:

1. Duplo/triplo clique no envio.
2. F5 após POST.
3. Voltar após concluir.
4. Duas abas editando o mesmo registro.
5. Sessão expirar durante formulário longo.
6. Trocar ID por registro de outro usuário/órgão.
7. Alterar campo hidden/disabled e enviar.
8. Requisição sem JavaScript e sem obrigatórios.
9. Colar 10.000 caracteres.
10. Enviar emoji e payloads não destrutivos de XSS, SQLi, fórmula e traversal.
11. Datas impossíveis e extremas.
12. Zero, negativo, fração, extremo, notação e locale numérico trocado.
13. Upload disfarçado, vazio, excessivo e nome com traversal, sem material malicioso real.
14. Rede 3G e queda durante envio.
15. Perfil sem permissão em rota, API e download.
16. Enviar após longa inatividade.
17. Excluir registro referenciado.
18. Fluxo por teclado e leitor de tela.
19. Filtro → detalhe → voltar.
20. Logout → voltar e cache de dado pessoal.
21. Token antigo, usado e expirado.
22. Aba antiga durante deploy.
23. Exportar filtro e conferir zeros no Excel.
24. Criar simultaneamente a mesma chave natural.

## Smoke antes de demonstração

Executar fluxo feliz; login/logout por perfil; erro de formulário; vazios; 360px e 1366×768; F5 crítico; console/CORS/CSP; 3G; acentos/nome longo/valor alto; IDOR com perfil restrito. O smoke não substitui a auditoria completa.
