---
name: qa-functional
description: Planejar e executar testes funcionais e de regras, cobrindo validações em cliente, servidor, domínio e banco, campos brasileiros, limites, partições, tabelas de decisão, estados, concorrência, idempotência e regressão. Usar como especialista obrigatório do QA Mestre ou para validar requisitos e comportamento funcional.
---

# Testar funcional e regras

## Executar

1. Rastrear regras `RN-XX` até código, contrato, caso e evidência.
2. Comparar cliente, servidor, domínio e banco para obrigatório, nulo, zero, tipo, formato, enum, tamanho, faixa, unicidade e FK.
3. Derivar caminho feliz, inválido, vazio, limites `min-1/min/min+1/max-1/max/max+1`, partições, decisão e transições inválidas.
4. Testar CPF/CNPJ com dígito verificador, CEP, telefone, datas, moeda e demais documentos aplicáveis; cobrir máscara, colar, backspace, normalização, acentos, nomes extremos e UTF-8.
5. Testar duplicidade, dois usuários/abas, idempotência, cálculos, arredondamento, fuso, prazo, transação e sequência.
6. Cobrir CRUD, cancelamento, exceções, persistência, histórico, importação/exportação e regressão de bugs.
7. Gerar YAML e executar `business_rules` após `--dry-run`; usar APIs ou navegador somente quando necessário e coordenado com seus proprietários.

## Entregar

Gravar `agents/qa-functional.json`, casos Gherkin e regras/casos para a matriz de rastreabilidade. Marcar esperado, observado, fonte, severidade, confiança e evidência reproduzível.
