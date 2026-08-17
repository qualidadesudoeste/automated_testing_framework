---
name: qa-code-quality
description: Auditar qualidade de código, arquitetura, testes, cobertura, CI, dependências, dados, migrações, release, rollback e governança, produzindo evidência estática e riscos de manutenção. Usar como especialista obrigatório do QA Mestre ou para avaliar maturidade técnica e prontidão de entrega.
---

# Auditar código e governança

## Executar

- Detectar sintaxe, erros, complexidade, arquivos extensos, duplicação, acoplamento, módulos, tratamento de erro e documentação pública.
- Avaliar separação de camadas, invariantes de domínio, transações, tipos, precisão, FK, constraints e migrations reversíveis.
- Executar testes existentes, cobertura e linters antes de introduzir ferramenta; avaliar cobertura por regra, não apenas linha.
- Verificar unidade > integração > E2E, factories BR válidas, autorização por rota, concorrência, idempotência, regressão e axe no CI.
- Verificar OpenAPI, logs, correlation ID, healthcheck, métricas, alertas e ausência de segredos.
- Procurar assinaturas explícitas de autoria automatizada, trailers de coautoria e arquivos de configuração de assistentes. Separar uso legítimo como funcionalidade do produto de indício de produção do código; registrar sempre como suspeita, nunca como prova de autoria.
- Avaliar migração legado: contagem, inválidos, de-para, encoding, sequência, idempotência, volume e rollback.
- Avaliar release: expand/contract, aba antiga, rollback testado, manutenção, monitoramento, critério de reversão, feature flag e plano B.
- Avaliar matriz de risco, DoR/DoD, gate, massa anonimizada, roteiro de homologação, aceite versionado, bug bash e causa raiz.
- Executar `project_quality` e ferramentas estáticas permitidas de `external_tools` após `--dry-run`.

## Entregar

Gravar `agents/qa-code-quality.json` com arquivo/linha, risco, impacto, evidência, teste de regressão e prioridade. Para sinais de autoria, incluir padrão detectado e confiança, sem inferir autoria pelo estilo do código. Não misturar estilo sem impacto com defeito funcional.
