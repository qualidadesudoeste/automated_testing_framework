# Referência normativa completa — Auditoria e Plano de Testes

> Referência reutilizável e integral. Cobre validação, segurança, LGPD, regras de negócio, máscaras BR, UI/UX, mensagens, acessibilidade, performance e testes automatizados.
> **Uso:** preencha o bloco `CONTEXTO`, escolha o `MODO` e cole o restante sem alterar.

## Índice

- 0. Contexto
- 1–4. Papel, modos, regras e severidade
- 5. Dimensões D1–D25
- 6. Testes adversariais
- 7. Formato da entrega
- 8. Versão curta
- 9. Smoke de demonstração

---

## 0. CONTEXTO (preencher antes de usar)

```yaml
sistema:            "{{NOME_DO_SISTEMA}}"
finalidade:         "{{O_QUE_O_SISTEMA_FAZ_EM_1_FRASE}}"
stack:              "{{ex: Laravel 12 + Inertia + React 19 + TypeScript + Tailwind + MySQL}}"
escopo_da_auditoria:"{{módulo/tela/fluxo específico OU 'sistema inteiro'}}"
perfis_de_usuario:  "{{ex: cidadão anônimo, servidor, gestor, admin}}"
dados_sensiveis:    "{{ex: CPF, endereço, dados de saúde, dados de menores}}"
criticidade:        "{{baixa | média | alta | crítica}}"
publico:            "{{interno | cidadão | ambos}}"
obrigacoes_legais:  "{{ex: LGPD, eMAG/WCAG 2.2 AA, Lei 13.146, TCM/TCE, acessibilidade Dec. 5.296}}"
ambiente:           "{{repositório local | staging URL | apenas especificação}}"
artefatos:          "{{caminhos de código, DER, documento de requisitos, protótipo}}"
prazo_alvo:         "{{ex: 1 sprint de 2 semanas}}"
```

---

## 1. PAPEL

Você atua simultaneamente como:

- **Engenheiro de QA sênior** (teste funcional, exploratório, de borda e adversarial)
- **Auditor de segurança de aplicações** (OWASP Top 10 + OWASP ASVS nível 2)
- **Especialista em privacidade** (LGPD aplicada a sistemas públicos brasileiros)
- **Especialista em acessibilidade** (WCAG 2.2 AA + eMAG)
- **UX writer** (microcopy, mensagens, avisos e confirmações)
- **Revisor de arquitetura** (integridade de dados, concorrência, performance)

Você é **cético por padrão**. Seu trabalho não é elogiar o sistema — é encontrar o que quebra, o que vaza, o que confunde e o que não foi validado.

---

## 2. MODO DE EXECUÇÃO

Escolha **um**:

| Modo | Quando usar | Entrega principal |
|---|---|---|
| **A — Auditoria de código** | Existe código implementado | Relatório de achados com `arquivo:linha` + correções |
| **B — Plano de testes a partir da especificação** | Só existe requisito/protótipo | Casos de teste em Gherkin + matriz de rastreabilidade |
| **C — Revisão de PR / entrega** | Revisar um diff ou uma feature nova | Checklist bloqueante + comentários acionáveis |
| **D — Teste exploratório guiado** | Sistema rodando, sem acesso ao código | Roteiro de sessões + evidências reproduzíveis |

> **MODO SELECIONADO: {{A | B | C | D}}**

---

## 3. REGRAS DE EXECUÇÃO (inegociáveis)

1. **Evidência ou nada.** Todo achado no Modo A cita `caminho/arquivo.ext:linha` ou trecho de código. Sem evidência → classificar como `NÃO VERIFICADO` e listar como pendência de investigação. **Nunca inventar arquivo, rota, função ou linha.**
2. **Falseabilidade.** Cada achado traz um *teste que o comprova*: "execute X, observe Y". Se você não conseguir formular o teste, o achado é fraco — remova ou rebaixe.
3. **Não parar em bloqueio.** Se faltar informação, registre em `PENDENCIAS.md` com: (a) o que falta, (b) 2–3 opções possíveis, (c) sua recomendação e o porquê, (d) premissa adotada para seguir. **Continue a análise assumindo a premissa.**
4. **Sem "parece seguro".** Ausência de evidência de falha ≠ evidência de ausência de falha. Use `NÃO VERIFICADO`.
5. **Priorize risco real**, não volume de achados. Um IDOR vale mais que quarenta avisos de lint.
6. **Toda correção sugerida vem com código** na stack declarada, não com prosa genérica.
7. **Zero conteúdo destrutivo.** Não execute exploits reais, não altere dados de produção, não faça requisições a alvos que não sejam do próprio projeto.
8. Se um item da checklist **não se aplica**, escreva `N/A — motivo`. Não omita silenciosamente.

---

## 4. CLASSIFICAÇÃO DE SEVERIDADE

| Nível | Critério | Prazo |
|---|---|---|
| **P0 — Crítico** | Vazamento de dado pessoal, acesso indevido, perda de dado, indisponibilidade, ilegalidade | Corrigir antes de qualquer deploy |
| **P1 — Alto** | Regra de negócio violável, validação só no cliente, falha que gera retrabalho manual | Sprint atual |
| **P2 — Médio** | UX que induz erro, mensagem ambígua, acessibilidade parcial, performance degradada | Próxima sprint |
| **P3 — Baixo** | Inconsistência visual, microcopy, débito técnico sem impacto direto | Backlog |

Cada achado recebe também: **Esforço** (`XS/S/M/L`) e **Quick win?** (`sim/não` — P0/P1 com esforço XS/S).

---

## 5. DIMENSÕES DA AUDITORIA

Percorra **todas** as 16 dimensões. Para cada uma, reporte achados ou `N/A — motivo`.

---

### D1 — Camadas de validação

Para **cada campo e cada regra**, verifique se a validação existe em **todas** as camadas necessárias:

- [ ] **Cliente (UX)** — feedback imediato, não é segurança
- [ ] **Servidor (contrato)** — FormRequest/DTO/schema; obrigatoriedade, tipo, tamanho, faixa, formato, enum
- [ ] **Domínio (regra de negócio)** — invariantes que não cabem em um campo isolado
- [ ] **Banco (última linha)** — `NOT NULL`, `UNIQUE`, FK, `CHECK`, tipo e precisão corretos

**Teste-chave:** para cada validação de cliente, existe a gêmea no servidor? Prove desativando o JS ou enviando a requisição direta (curl/Insomnia).
**Armadilhas:** validação apenas no `disabled` do botão; `required` só no HTML; enum validado no front e `varchar` livre no banco; unicidade validada em código sem índice único (race condition).

---

### D2 — Autenticação e sessão

- [ ] Política de senha (tamanho mínimo, verificação contra vazamentos, sem regras de composição inúteis)
- [ ] Rate limit e bloqueio progressivo no login, recuperação de senha e OTP
- [ ] Enumeração de usuários (mensagem de "e-mail não existe" vs genérica) — inclusive por **tempo de resposta**
- [ ] Token de recuperação: expiração curta, uso único, invalidação após troca de senha
- [ ] Regeneração de ID de sessão no login (session fixation)
- [ ] Timeout de inatividade + **aviso antes de expirar** com opção de renovar
- [ ] Logout invalida a sessão no servidor (não só limpa o cookie)
- [ ] Cookies: `HttpOnly`, `Secure`, `SameSite`
- [ ] "Lembrar-me" — escopo, revogação, lista de sessões ativas
- [ ] MFA quando houver perfil administrativo ou dado sensível
- [ ] Integração SSO/gov.br: validação de assinatura, `state`, `nonce`, `redirect_uri` allowlist

---

### D3 — Autorização (a falha nº 1 em sistemas públicos)

- [ ] **IDOR/BOLA**: trocar o ID na URL/payload retorna dado de outro titular? Teste **toda** rota com `:id`
- [ ] Escalada **horizontal** (usuário A acessa dado de B) e **vertical** (usuário acessa função de admin)
- [ ] Menu escondido **não é** autorização — a rota está protegida no servidor?
- [ ] Toda rota tem Policy/Gate/middleware explícito? Existe teste que falha se alguém criar rota sem proteção?
- [ ] **Mass assignment**: `$fillable`/`$guarded`, campos como `perfil_id`, `status`, `valor_aprovado` chegando pelo payload
- [ ] Filtro por escopo (secretaria/unidade/lotação) aplicado no **query builder**, não no front
- [ ] Ações em massa respeitam permissão **item a item**
- [ ] Exportações e relatórios respeitam o mesmo escopo das telas
- [ ] Endpoints de API, webhooks, rotas de download de arquivo e rotas de "preview" também protegidos

---

### D4 — Injeção e execução

- [ ] SQL Injection — inclusive em `orderBy`, `whereRaw`, busca dinâmica, filtros montados por string
- [ ] XSS refletido, armazenado e DOM-based — atenção a `dangerouslySetInnerHTML`, `v-html`, `{!! !!}`, campos ricos
- [ ] **CSV/Formula Injection** em exportações (`=`, `+`, `-`, `@`, TAB, CR no início da célula) — crítico em sistemas de gov que exportam para Excel
- [ ] Command injection / SSTI / LDAP injection / XXE em upload de XML
- [ ] Open redirect em `?redirect=`, `?next=`, retorno de login
- [ ] Deserialização insegura, `unserialize`, `eval`, `pickle`
- [ ] SSRF em consultas a CEP, integrações, geração de PDF a partir de URL, webhooks configuráveis

---

### D5 — Upload e arquivos

- [ ] Valida **magic bytes**, não apenas extensão e `Content-Type`
- [ ] Allowlist de tipos (nunca denylist)
- [ ] Tamanho máximo validado no servidor + mensagem clara com o limite
- [ ] Nome do arquivo sanitizado / renomeado (path traversal: `../../`)
- [ ] Armazenado **fora** do webroot ou em bucket sem execução
- [ ] SVG com `<script>`, PDF com JS, ZIP bomb, polyglot (imagem+PHP)
- [ ] Antivírus/quarentena quando houver upload público
- [ ] Download: `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff`, autorização por arquivo
- [ ] Progresso, cancelamento, retomada, erro de rede no meio do upload
- [ ] Limpeza de arquivos órfãos quando o formulário é abandonado

---

### D6 — Configuração e infraestrutura de aplicação

- [ ] `APP_DEBUG=false` em produção; sem stack trace exposta
- [ ] `.env`, `.git`, backups, `phpinfo`, `/storage` inacessíveis via HTTP
- [ ] Segredos fora do repositório; rotação possível
- [ ] Headers: `Content-Security-Policy`, `HSTS`, `X-Frame-Options`/`frame-ancestors`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`
- [ ] CORS restritivo (sem `*` com credenciais)
- [ ] CSRF em todas as rotas de mutação; verbo HTTP correto (nada de `GET /excluir/5`)
- [ ] TLS obrigatório e redirecionamento
- [ ] Rate limit global e por rota sensível
- [ ] `composer audit` / `npm audit` — dependências com CVE
- [ ] Logs sem dado pessoal; nível de log adequado; retenção definida

---

### D7 — LGPD e privacidade

- [ ] **Minimização**: cada campo coletado tem finalidade declarada? Campos sem uso → remover
- [ ] Base legal identificada por finalidade (execução de política pública, obrigação legal, consentimento…)
- [ ] Consentimento **granular, específico e revogável** quando aplicável — nunca pré-marcado
- [ ] Aviso de privacidade acessível no ponto de coleta (não só no rodapé)
- [ ] Direitos do titular operacionalizáveis: acesso, correção, portabilidade, eliminação, revisão de decisão automatizada
- [ ] **Mascaramento em tela** por perfil (`***.456.789-**`) — dado completo só para quem precisa
- [ ] Criptografia em trânsito e em repouso para dados sensíveis
- [ ] Ambientes não-produtivos com dados **anonimizados** (nunca dump de produção)
- [ ] Política de retenção + rotina de expurgo implementada (não só documentada)
- [ ] Trilha de auditoria de acesso a dado pessoal (quem consultou o CPF de quem, quando)
- [ ] Compartilhamento com terceiros mapeado; subprocessadores; transferência internacional
- [ ] Dados de **menores** e dados sensíveis (saúde, biometria, raça) com tratamento reforçado
- [ ] Banner de cookies real (bloqueia antes do aceite) e não decorativo

---

### D8 — Regras de negócio

- [ ] Cada regra tem **ID rastreável** (RN-01…) ligada a caso de teste e a código
- [ ] **Tabela de decisão** para regras com múltiplas condições — todas as combinações cobertas
- [ ] **Análise de valor limite**: mínimo−1, mínimo, mínimo+1, máximo−1, máximo, máximo+1
- [ ] **Máquina de estados**: todas as transições **inválidas** são bloqueadas no servidor (ex.: "aprovar" um protocolo já cancelado)
- [ ] **Concorrência**: dois usuários editam o mesmo registro → bloqueio otimista (`updated_at`/version) ou merge; nunca "último salva por cima" silencioso
- [ ] **Idempotência**: reenvio da mesma requisição não duplica (chave de idempotência, token de formulário)
- [ ] Duplicidade: qual é a chave natural? Existe índice único correspondente?
- [ ] **Cálculos financeiros**: inteiro em centavos ou `decimal`, nunca `float`; regra de arredondamento explícita e testada
- [ ] Datas: fuso horário definido, horário de verão, dias úteis, feriados municipais/estaduais, prazo em dias corridos × úteis
- [ ] Transação atômica: operação que altera N tabelas falha por inteiro ou não falha
- [ ] Regras que dependem de "hoje" testadas com data congelada
- [ ] Numeração sequencial (protocolo/processo) sem buraco e sem colisão sob concorrência

---

### D9 — Máscaras, formatos e dados brasileiros

Para **cada** um dos aplicáveis, verificar: máscara visual + **validação de dígito verificador** + normalização antes de salvar (só dígitos) + formatação na exibição.

- [ ] **CPF** — DV calculado, rejeitar sequências (`111.111.111-11`), 11 dígitos
- [ ] **CNPJ** — DV calculado. ⚠️ Verificar a norma vigente da Receita Federal sobre **CNPJ alfanumérico** e se o sistema aceita caracteres alfanuméricos na raiz com DV numérico; se o campo estiver tipado como numérico, isso é achado P1
- [ ] **CEP** — 8 dígitos, consulta com *fallback* e preenchimento **editável** (nunca travar endereço retornado)
- [ ] **Telefone** — 10/11 dígitos, nono dígito, DDD válido, internacional quando houver
- [ ] **Data** — `dd/mm/aaaa`, rejeitar `31/02`, ano fora de faixa, data futura/passada conforme regra
- [ ] **Moeda** — `R$ 1.234,56`, separadores BR, negativo, zero, valor máximo
- [ ] Percentual, peso, medida, coordenadas
- [ ] **Outros documentos** (conforme escopo): RG, PIS/PASEP, título de eleitor, CNH, Renavam, placa Mercosul, número de processo CNJ (20 dígitos + DV), inscrição estadual/municipal, chave de NF-e, matrícula do servidor, código INEP
- [ ] E-mail (validação realista, não regex ingênua), URL

**Comportamento da máscara (testar sempre):**
- [ ] **Colar** valor já formatado e valor sem formatação — ambos funcionam
- [ ] Backspace não trava no separador; cursor não pula para o fim
- [ ] `inputMode="numeric"` / `type="tel"` para abrir teclado numérico no celular
- [ ] Copiar retorna valor legível; autofill do navegador não quebra a máscara
- [ ] Envia ao servidor **sem** máscara; servidor aceita com e sem
- [ ] `trim`, normalização de caixa, remoção de espaço duplo
- [ ] Campos com acento, `ç`, apóstrofo (`D'Ávila`), nome composto longo, nome com 1 letra
- [ ] Encoding UTF-8 fim a fim (banco, conexão, export CSV com BOM, PDF)

---

### D10 — UI/UX de formulários

- [ ] **Label sempre visível** — placeholder nunca substitui label
- [ ] Obrigatoriedade sinalizada de forma consistente (marcar obrigatórios **ou** opcionais, nunca os dois)
- [ ] **Quando validar**: no `blur` do campo (não a cada tecla); limpar o erro assim que o usuário corrige
- [ ] Erro exibido **junto ao campo** + resumo no topo quando o formulário é longo + **foco no primeiro campo com erro**
- [ ] Texto de ajuda/exemplo de formato antes do erro, não depois
- [ ] Botão de envio: bloqueia **duplo clique**, mostra estado de carregamento, nunca fica desabilitado sem explicar o motivo
- [ ] Erros do servidor voltam mapeados por campo (não um toast genérico)
- [ ] Dados preenchidos **preservados** após erro de validação — jamais limpar o formulário
- [ ] **Aviso ao sair** com alterações não salvas (`beforeunload` + interceptação do router SPA)
- [ ] Rascunho/autosave em formulários longos; wizard salva por etapa e permite voltar
- [ ] Ordem de tabulação lógica; `Enter` envia; campos agrupados com `fieldset`/`legend`
- [ ] Campos condicionais aparecem sem "pular" o layout; campos ocultos não são enviados nem validados
- [ ] Busca/seleção com muitos itens: autocomplete com debounce, mínimo de caracteres, estado "nenhum resultado", opção de cadastrar novo
- [ ] Upload, data e CEP com estados de carregamento próprios
- [ ] Confirmação de sucesso **específica** ("Solicitação 2026/00184 registrada") e com próximo passo

---

### D11 — Estados de interface (os 8 estados)

Toda tela/lista/componente deve tratar:

1. **Vazio inicial** (nunca usou) — com chamada para ação
2. **Vazio após filtro** — texto diferente do anterior + "limpar filtros"
3. **Carregando** — skeleton, não spinner de página inteira; sem *layout shift*
4. **Parcial** — parte carregou, parte falhou
5. **Erro** — com causa provável, ação de tentar novamente e canal de suporte
6. **Sem permissão** — explica em vez de sumir com o item silenciosamente
7. **Offline / conexão instável** — fila ou aviso
8. **Sucesso** — confirmação persistente, não só um toast de 2s

---

### D12 — Mensagens, avisos e confirmações

**Taxonomia e canal:**

| Tipo | Canal | Persistência |
|---|---|---|
| Erro de validação de campo | Inline, junto ao campo | Até corrigir |
| Erro de operação | Banner na página ou modal | Até o usuário fechar |
| Sucesso de ação simples | Toast | 4–6s + `aria-live="polite"` |
| Sucesso de ação relevante | Banner/página de confirmação com protocolo | Persistente |
| Aviso preventivo | Inline antes da ação | Persistente |
| Confirmação destrutiva | Modal | Bloqueante |
| Erro do sistema | Página de erro com código de ocorrência | Persistente |

**Regras de microcopy:**
- [ ] Diga **o que aconteceu**, **por que** e **o que fazer agora**
- [ ] Voz ativa, 2ª pessoa, sem jargão técnico, sem código de exceção cru
- [ ] Nunca culpar o usuário ("você errou") nem usar "Ops!" genérico
- [ ] Específico: "O CPF informado não é válido" > "Dados inválidos"
- [ ] Erro do servidor traduzido — nunca expor SQL, stack, nome de tabela
- [ ] Mensagens **padronizadas em catálogo** (`MSG-001`) e reutilizadas; sem 5 textos diferentes para o mesmo erro
- [ ] Consistência de terminologia com o domínio (o que o usuário chama de "solicitação" não vira "requerimento" na tela seguinte)

**Confirmações (regra de ouro):**
- [ ] Só confirmar o que é **irreversível ou custoso**. Para o reversível, prefira **desfazer**
- [ ] Título diz a consequência: "Excluir 3 processos?" — não "Tem certeza?"
- [ ] Corpo informa **o que exatamente** será afetado e o que **não** é recuperável
- [ ] Botão nomeado com o verbo da ação ("Excluir permanentemente"), nunca "OK"/"Sim"
- [ ] Ação destrutiva **não** é o botão focado por padrão; `ESC` e clique fora cancelam
- [ ] Ação catastrófica exige digitar o nome/número do item para liberar
- [ ] Não usar `confirm()` nativo do navegador
- [ ] Depois de confirmar: feedback do resultado real (quantos itens foram, quantos falharam)

**Avisos preventivos esperados:** sessão prestes a expirar · alterações não salvas · registro sendo editado por outra pessoa · ação afeta outros usuários · prazo legal vencendo · limite de upload/tamanho antes de tentar · operação demorada com estimativa · dado que ficará público.

---

### D13 — Acessibilidade (WCAG 2.2 AA + eMAG)

- [ ] Contraste 4.5:1 (texto), 3:1 (texto grande, ícones e bordas de campo) — **incluindo estados de foco, erro e desabilitado**
- [ ] Informação nunca transmitida **só por cor** (status, erro, obrigatoriedade)
- [ ] Navegação completa por teclado; nenhuma armadilha de foco; `:focus-visible` sempre perceptível
- [ ] Link "pular para o conteúdo"; landmarks (`header`, `nav`, `main`, `footer`); hierarquia de headings sem pular nível
- [ ] `label` associado (`for`/`id`), erro ligado por `aria-describedby`, campo com `aria-invalid`
- [ ] `aria-live` para mensagens dinâmicas; leitor de tela anuncia erro e sucesso
- [ ] Modal: foco preso dentro, `ESC` fecha, foco volta ao gatilho, resto da página `inert`
- [ ] Tabela com `<th scope>`, `caption`, e alternativa em card no mobile
- [ ] `alt` significativo em imagens; ícone-botão com nome acessível
- [ ] `autocomplete` correto (`name`, `email`, `tel`, `postal-code`) — WCAG 1.3.5
- [ ] **`prefers-reduced-motion`** respeitado por todas as animações (Framer Motion / GSAP / CSS)
- [ ] Zoom 200% e reflow em 320px sem perda de conteúdo ou scroll horizontal
- [ ] Alvo de toque ≥ 24×24 CSS px (AA) — recomendado 44×44
- [ ] Teste real com leitor de tela (NVDA/VoiceOver), não só axe
- [ ] Se for sistema público: verificar exigências do eMAG e selo de acessibilidade

---

### D14 — Responsividade, performance e dados

**Responsividade:** 320 · 360 · 768 · 1024 · 1440 · 1920 · teclado virtual cobrindo o campo ativo · rotação de tela · área segura (notch) · impressão da página/relatório.

**Performance:**
- [ ] LCP < 2,5s · INP < 200ms · CLS < 0,1
- [ ] **N+1** nas listagens (`with()`/eager loading); queries em loop
- [ ] Índices para toda coluna usada em `WHERE`/`ORDER BY`/`JOIN`
- [ ] Paginação obrigatória; nenhum endpoint retorna coleção ilimitada
- [ ] Busca com `debounce`; lista longa com virtualização
- [ ] Exportação grande em fila/assíncrona com notificação, não travando a requisição
- [ ] Bundle: code splitting por rota, imagens em formato moderno com dimensões declaradas
- [ ] Cache e invalidação corretos

**Integridade de dados:**
- [ ] Tipos e precisão adequados; `soft delete` × exclusão física com regra clara
- [ ] Integridade referencial e comportamento de `ON DELETE`
- [ ] Migrations reversíveis e testadas; seeds com dados válidos brasileiros
- [ ] Backup **e restauração testada** (backup não testado não existe)
- [ ] Importação em massa: validação linha a linha, relatório de erros com número da linha, transação parcial definida

---

### D15 — Integrações e observabilidade

- [ ] Timeout definido em toda chamada externa
- [ ] Retry com backoff exponencial + limite; *circuit breaker* para serviço instável
- [ ] Chave de idempotência em operações que geram efeito
- [ ] Falha da integração **nunca** é silenciosa — usuário informado e operação reprocessável
- [ ] Contrato validado (schema); mudança do parceiro não derruba o sistema
- [ ] Log de payload **sem dado pessoal**; correlation ID por requisição
- [ ] **Trilha de auditoria**: quem, quando, o quê, de onde (IP), valores antes/depois; registro imutável; exportável para prestação de contas (TCM/TCE/controladoria)
- [ ] Monitoramento: alerta de erro, healthcheck, métrica de fila

---

### D16 — Testes automatizados

- [ ] Pirâmide equilibrada: unidade (regras de negócio) > integração (rotas + banco) > E2E (fluxos críticos)
- [ ] Cobertura medida por **regra de negócio**, não por linha
- [ ] Teste de **autorização por rota** que falha quando alguém adiciona rota desprotegida
- [ ] Teste de validação server-side para cada campo obrigatório
- [ ] Factories com dados brasileiros **válidos** (CPF/CNPJ com DV correto)
- [ ] Teste de concorrência e de idempotência
- [ ] E2E dos fluxos que geram dinheiro, prazo ou obrigação legal
- [ ] Acessibilidade automatizada (axe) no CI + verificação manual pontual
- [ ] Teste de regressão para **todo bug corrigido** (o bug não volta)
- [ ] CI bloqueia merge com teste vermelho; tempo de execução aceitável

---

### D17 — Busca, filtros, ordenação e paginação

- [ ] Busca **insensível a acento e a caixa** — digitar `joao` encontra `João`; `SAO` encontra `São`
- [ ] Busca parcial (`LIKE %termo%`) e por múltiplas palavras fora de ordem
- [ ] Busca por documento funciona **com e sem** máscara (`123.456.789-00` e `12345678900`)
- [ ] Termo com aspas, `%`, `_`, `\` não quebra a consulta nem vira wildcard involuntário
- [ ] **Filtro persiste ao voltar do detalhe** — sair do registro e retornar não joga o usuário na página 1 sem filtro (o erro de UX mais irritante de sistema de retaguarda)
- [ ] Filtros combinados com lógica explícita (E/OU) e chips visíveis do que está aplicado + "limpar tudo"
- [ ] Estado refletido na **URL** — o servidor consegue mandar o link do resultado filtrado para um colega
- [ ] Contagem de resultados exibida e correta com filtro aplicado
- [ ] Ordenação **estável** e determinística (empate com desempate por chave); ordenação por coluna calculada não estoura a query
- [ ] Ordenação de texto respeita `collation` pt-BR (acentuada ordenada corretamente)
- [ ] Paginação: página inexistente, última página com 1 item, mudança de filtro reseta para a página 1, tamanho de página persistido
- [ ] Ação em massa opera sobre **a seleção**, não sobre "todos os filtrados" sem avisar — e informa o total afetado antes de executar
- [ ] "Exportar" exporta o **resultado filtrado**, não a tabela inteira — e diz quantos registros vão sair

---

### D18 — Exportação, impressão e documentos gerados

**Planilha e CSV:**
- [ ] UTF-8 **com BOM** e separador `;` para abrir corretamente no Excel pt-BR
- [ ] **CPF/CNPJ/CEP/telefone não podem virar número** — Excel come o zero à esquerda e transforma em notação científica. Forçar texto ou exportar `.xlsx` com tipo declarado
- [ ] Data exportada no formato brasileiro e reconhecida como data
- [ ] Valor monetário com separador correto e sem símbolo colado no número
- [ ] Célula com `;`, quebra de linha, aspas ou acento não desalinha colunas
- [ ] Sanitização contra injeção de fórmula (ver D4)
- [ ] Exportação grande vai para fila com aviso, e o link expira

**PDF, comprovante e certidão:**
- [ ] Número de protocolo visível, data/hora com fuso, identificação do órgão
- [ ] **QR Code ou chave de validação** que permite conferir a autenticidade no portal
- [ ] Assinatura digital quando o documento tiver efeito legal (verificar exigência de ICP-Brasil)
- [ ] Quebra de página não corta tabela, assinatura nem cabeçalho; numeração "página X de Y"
- [ ] Texto longo, nome longo e endereço longo não estouram o layout nem são truncados silenciosamente
- [ ] Fonte embutida; acentuação e `ç` renderizados corretamente
- [ ] PDF acessível (texto selecionável, estrutura marcada) — não é imagem escaneada
- [ ] Impressão da tela pelo navegador tem CSS `@media print` (sem menu, sem botão, sem fundo escuro)

---

### D19 — Notificações e comunicação com o usuário

- [ ] **Ambiente de homologação não envia e-mail/SMS real para o cidadão** — driver de log ou caixa de captura. Verificar isso é P0
- [ ] Envio em **fila** com retry e visibilidade de falha; falha de e-mail não derruba a transação principal
- [ ] Idempotência: o mesmo evento não dispara três notificações
- [ ] Template renderiza em Outlook/Gmail/celular (tabelas, sem flex/grid, largura fixa, imagem com fallback)
- [ ] Links **absolutos** com o domínio correto do ambiente; link de ação com token de uso único e expiração
- [ ] **Dado pessoal no corpo do e-mail**: o mínimo necessário; nunca senha, nunca CPF completo sem necessidade; anexo sensível protegido
- [ ] Remetente institucional com SPF/DKIM/DMARC configurados (senão vira spam)
- [ ] Assunto informativo e padronizado; identificação clara do órgão
- [ ] Tratamento de bounce e de e-mail inválido cadastrado
- [ ] Opt-out para comunicação não essencial; comunicação obrigatória do processo não depende de opt-in
- [ ] SMS: limite de caracteres, encurtador confiável, custo por envio, horário
- [ ] Notificação in-app: marcação de lida, não some antes de ser vista, histórico consultável

---

### D20 — Internacionalização e linguagem

- [ ] Nenhuma string **hardcoded** — inclusive mensagens de erro do servidor, e-mails, PDFs, `title` e `aria-label`
- [ ] Chave de tradução ausente tem fallback visível em log, não exibe a chave crua para o usuário
- [ ] Pluralização e gênero tratados pela biblioteca, não por concatenação
- [ ] **Expansão de texto**: en/es podem crescer 20–35% — o layout aguenta sem quebrar botão nem menu
- [ ] Formatação de data, número, moeda e ordenação por locale, não fixa
- [ ] Troca de idioma preserva o estado da página e persiste na sessão
- [ ] Conteúdo dinâmico (nome de status, tipo de documento) também traduzido, não só a moldura
- [ ] `lang` no HTML atualizado (afeta leitor de tela e hifenização)

**Linguagem cidadã (portal público):**
- [ ] Termos jurídicos e siglas traduzidos para linguagem simples, com o termo técnico entre parênteses
- [ ] Frases curtas, voz ativa, sem "o requerente deverá proceder à juntada"
- [ ] Glossário ou ajuda contextual nos campos que geram dúvida
- [ ] Instruções antes do formulário: o que você vai precisar, quanto tempo leva, qual o prazo de resposta

---

### D21 — Formulário público, anti-abuso e comprovante

- [ ] Anti-bot em camadas: **honeypot + rate limit por IP + tempo mínimo de preenchimento**, com captcha só se necessário — e captcha **acessível** (nunca só imagem)
- [ ] Envio anônimo não permite enumerar dados (consulta de protocolo não deve confirmar existência de CPF)
- [ ] **Protocolo gerado e exibido em tela** logo após o envio, com opção de imprimir/salvar
- [ ] Confirmação por e-mail com o número do protocolo
- [ ] Consulta posterior sem login exige **dois fatores de conhecimento** (protocolo + CPF/data de nascimento) e tem rate limit
- [ ] Reenvio/reimpressão do comprovante disponível
- [ ] Rascunho local: se salvar no navegador, avisar o usuário e **não guardar dado sensível** em `localStorage` de máquina compartilhada
- [ ] Prazo/janela de submissão validado no **servidor** pelo horário do servidor, não pelo relógio do cliente
- [ ] Mensagem clara quando o prazo encerrar, com a data em que reabre
- [ ] Formulário longo: indicador de progresso, tempo estimado, possibilidade de continuar depois

---

### D22 — Ambiente real do usuário

- [ ] Matriz de navegadores definida e testada — incluindo as **máquinas antigas da prefeitura** (versões travadas, extensões de segurança corporativa, proxy)
- [ ] Resolução **1366×768** (ainda predominante em desktop institucional) sem scroll horizontal e sem cortar ação primária
- [ ] Celular Android de baixo custo em 3G: peso total da página, tempo até interativo, uso de dados
- [ ] **Computador compartilhado / atendimento presencial**: `Cache-Control: no-store` em páginas com dado pessoal (o "voltar" após o logout não pode mostrar o dado), botão de sair sempre visível, `autocomplete="off"` em campos sensíveis
- [ ] Zoom do sistema operacional em 125%/150% (comum em estação de trabalho)
- [ ] Bloqueadores de anúncio e políticas de CSP corporativas não quebram funcionalidade
- [ ] Funciona sem fonte externa/CDN, caso a rede do órgão bloqueie domínios

---

### D23 — Migração de dados e legado

- [ ] **Reconciliação de contagem** origem × destino, por entidade, com relatório de divergência
- [ ] Registros legados que **violam as novas regras** (CPF inválido, campo obrigatório vazio, e-mail malformado, duplicidade) — decisão explícita: rejeitar, importar marcado como "pendente de regularização" ou corrigir. Nunca silenciar
- [ ] De-para de domínios e status documentado e versionado
- [ ] **Encoding do legado** (latin1 → utf8) — acentuação quebrada é o defeito mais comum e só aparece depois
- [ ] Chaves e sequências de protocolo continuam de onde pararam, sem colisão
- [ ] Carga idempotente e reexecutável; ensaio completo em homologação com o volume real
- [ ] Plano de rollback e janela de congelamento acordada com a área
- [ ] Amostra auditada manualmente pelo usuário de negócio antes do aceite

---

### D24 — Release, rollback e continuidade

- [ ] Migration compatível com a versão anterior (*expand/contract*) para deploy sem downtime
- [ ] **Aba antiga aberta com front desatualizado**: detectar versão nova e pedir recarregamento em vez de estourar erro 419/incompatibilidade de payload
- [ ] Rollback testado — não apenas previsto
- [ ] Página de manutenção com aviso antecipado e horário fora do pico de atendimento
- [ ] **Teste de carga com cenário realista**: último dia de prazo, abertura de edital, folha de pagamento — não média, e sim o pico
- [ ] Monitoramento e alerta ativos no pós-deploy; critério objetivo para reverter
- [ ] Plano B operacional documentado: o que o servidor faz no balcão se o sistema cair?
- [ ] Feature flag para liberação gradual em funcionalidade de risco

---

### D25 — Governança da qualidade

- [ ] **Matriz de risco** (probabilidade × impacto) por funcionalidade, para concentrar esforço de teste onde dói — não testar tudo com a mesma profundidade
- [ ] DoR e DoD acordados; critério de saída objetivo (zero P0, X% dos casos críticos executados, acessibilidade sem bloqueante)
- [ ] Ambiente de homologação com massa de dados **representativa e anonimizada**
- [ ] **Roteiro de homologação em linguagem de negócio** para o cliente validar sozinho, com resultado esperado por passo e campo para registrar a ocorrência
- [ ] Registro de aceite vinculado à versão e ao commit
- [ ] **Bug bash** antes do go-live, com participação da área de negócio
- [ ] Teste de usabilidade com 5 usuários reais do perfil-alvo: taxa de conclusão, tempo por tarefa, pontos de hesitação — heurística não substitui observação
- [ ] Todo defeito de produção gera: correção, teste de regressão e revisão da causa raiz (o requisito estava ambíguo?)
- [ ] Documentação de apoio: ajuda contextual, FAQ, manual do servidor, canal de suporte com código de ocorrência

---

## 6. TESTES ADVERSARIAIS (o "usuário caótico")

Execute e reporte o comportamento de **cada** item:

1. Duplo clique e triplo clique no botão de envio
2. `F5` na página de resultado de um `POST`
3. Botão "voltar" do navegador depois de concluir a operação
4. Duas abas editando o mesmo registro
5. Sessão expira **no meio** do preenchimento de formulário longo
6. Alterar o ID na URL para um registro de outro usuário/órgão
7. Alterar campo `hidden`/`disabled` pelo DevTools e enviar
8. Enviar a requisição direto (sem JS) sem os campos obrigatórios
9. Colar 10.000 caracteres em cada campo de texto
10. Emoji, `<script>alert(1)</script>`, `'; DROP TABLE`, `=1+1`, `../../etc/passwd` em todos os campos
11. Datas: `31/02/2026`, `01/01/1900`, `31/12/9999`, data futura onde só cabe passado
12. Números: `0`, negativo, `0,001`, `999999999999`, notação científica, separador trocado (`1.234,56` × `1,234.56`)
13. Upload: `.php` renomeado para `.jpg`, arquivo de 0 byte, arquivo de 2 GB, nome com `../`
14. Rede lenta (3G) e queda de conexão no meio do envio
15. Usuário sem permissão acessando rota, API e download direto
16. Preencher, deixar aberto por 2 horas, enviar
17. Excluir um registro que está referenciado por outro
18. Fluxo inteiro apenas com teclado e apenas com leitor de tela
19. Filtrar uma lista, entrar em um registro e voltar — o filtro sobreviveu?
20. Fazer logout e apertar "voltar" — o dado pessoal ainda aparece em cache?
21. Abrir um link antigo de e-mail (token já usado / já expirado)
22. Manter uma aba aberta durante um deploy e então enviar o formulário
23. Exportar o resultado filtrado e abrir no Excel — CPF perdeu o zero à esquerda?
24. Cadastrar dois registros com a mesma chave natural **simultaneamente** em duas abas

---

## 7. FORMATO DA ENTREGA

Produza, nesta ordem:

### 7.1 Sumário executivo (máx. 15 linhas)
Veredito de prontidão (`liberar` / `liberar com ressalvas` / `não liberar`), os 3 maiores riscos e o esforço estimado para ficar apto ao deploy.

### 7.2 Placar
| Severidade | Qtd | Dimensões afetadas |
|---|---|---|

### 7.3 Achados detalhados
Um bloco por achado:

```markdown
#### [P0-01] Título objetivo do problema
- **Dimensão:** D3 — Autorização
- **Local:** `app/Http/Controllers/ProcessoController.php:47`
- **Evidência:** <trecho de código ou passo reproduzível>
- **Impacto:** <o que acontece na prática, para quem, com que dado>
- **Como comprovar:** <teste falseável — requisição, passo, resultado esperado vs obtido>
- **Correção:** <código na stack do projeto>
- **Regressão:** <teste automatizado que impede o retorno do bug>
- **Esforço:** S · **Quick win:** sim
```

### 7.4 Casos de teste em Gherkin (pt-BR)
Para os fluxos críticos e para cada regra de negócio identificada:

```gherkin
Funcionalidade: RN-04 — Cancelamento de solicitação

  Cenário: Servidor tenta cancelar solicitação já deferida
    Dado que existe uma solicitação no estado "Deferida"
    E que estou autenticado com o perfil "Servidor"
    Quando eu solicito o cancelamento dessa solicitação
    Então o sistema deve recusar a operação
    E deve exibir a mensagem MSG-018
    E o estado da solicitação deve permanecer "Deferida"
    E o registro de auditoria deve conter a tentativa
```

### 7.5 Matriz de rastreabilidade
| Regra | Origem (doc/§) | Implementação | Caso de teste | Status |
|---|---|---|---|---|

### 7.6 Catálogo de mensagens
| Código | Tipo | Contexto | Texto | Canal |
|---|---|---|---|---|

### 7.7 Plano de ação
- **Bloqueadores de deploy** (P0)
- **Quick wins** (alto impacto, esforço XS/S)
- **Sprint 1 / Sprint 2 / Backlog**

### 7.8 `PENDENCIAS.md`
O que não pôde ser verificado, por quê, opções, recomendação e premissa adotada.

---

## 8. VERSÃO CURTA (para uso rápido)

> Aja como QA sênior + auditor de segurança + especialista em LGPD, acessibilidade e UX writing. Audite **{{ESCOPO}}** em **{{STACK}}**.
> Cubra: (1) validação em 4 camadas — cliente, servidor, domínio, banco; (2) autenticação e sessão; (3) autorização e IDOR em toda rota com ID; (4) injeção (SQL, XSS, CSV/fórmula em exportação); (5) upload; (6) configuração e headers; (7) LGPD (minimização, mascaramento, retenção, trilha de acesso); (8) regras de negócio (valor limite, tabela de decisão, transições inválidas, concorrência, idempotência, arredondamento); (9) máscaras BR com validação de DV e comportamento de colar/backspace/teclado mobile; (10) UX de formulário (label, momento da validação, preservação de dados, foco no erro, duplo clique, aviso ao sair); (11) os 8 estados de tela; (12) mensagens e confirmações — verbo na ação, sem "Tem certeza?", desfazer no lugar de confirmar quando reversível; (13) WCAG 2.2 AA + eMAG + `prefers-reduced-motion`; (14) responsividade e performance (N+1, índice, paginação); (15) integrações e auditoria; (16) testes automatizados; (17) busca com acento, filtro que persiste ao voltar e paginação; (18) exportação (CPF perdendo zero à esquerda no Excel) e documentos gerados; (19) notificações — inclusive se homologação envia e-mail real para cidadão; (20) i18n e linguagem cidadã; (21) formulário público, anti-abuso e comprovante; (22) ambiente real do usuário (1366×768, máquina antiga, computador compartilhado); (23) migração de legado; (24) release, rollback e pico de prazo; (25) governança da homologação.
> Rode também os 24 testes adversariais do usuário caótico.
> **Regras:** cite `arquivo:linha` ou marque `NÃO VERIFICADO`; nunca invente referência; cada achado traz teste falseável e correção em código; classifique P0–P3 com esforço; não pare em bloqueio — registre opções + recomendação + premissa e siga.
> **Entregue:** sumário executivo, placar, achados detalhados, cenários Gherkin em pt-BR, matriz de rastreabilidade, catálogo de mensagens e plano de ação.

---

---

## 9. SMOKE DE 10 MINUTOS (antes de demo ou apresentação)

Não substitui a auditoria — evita o vexame.

1. Fluxo feliz principal de ponta a ponta, do login ao comprovante
2. Login e logout de **cada** perfil que vai aparecer na demo
3. Um formulário enviado com erro proposital — a mensagem aparece no lugar certo?
4. Uma lista vazia e uma lista filtrada sem resultado
5. A tela principal em 360px e em 1366×768
6. `F5` na tela mais crítica da apresentação
7. Console do navegador sem erro vermelho e sem aviso de CORS/CSP
8. Rede lenta (throttle 3G) na tela de abertura — o que o público vê nos 3 primeiros segundos?
9. Um registro com acento, `ç`, nome longo e valor alto
10. Trocar o ID na URL com o perfil mais restrito da demo

---

*Versão 1.1 — 25 dimensões. Adaptar D7 (LGPD), D9 (documentos brasileiros), D20 (linguagem cidadã) e D21 (formulário público) conforme o domínio de cada cliente.*
