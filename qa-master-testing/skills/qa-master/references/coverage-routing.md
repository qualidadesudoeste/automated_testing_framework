# Roteamento obrigatório de cobertura

Passar estes IDs aos respectivos agentes. Um agente pode cobrir itens adicionais, mas nenhum ID pode ficar sem proprietário.

## Dimensões

- `qa-functional`: D01, D08, D09.
- `qa-security`: D02, D03, D04, D05, D06.
- `qa-privacy-lgpd`: D07.
- `qa-interface`: D10, D17, D21, D22.
- `qa-ui-ux`: D11, D12, D18, D19, D20.
- `qa-accessibility`: D13.
- `qa-performance`: D14.
- `qa-integrations`: D15.
- `qa-code-quality`: D16, D23, D24, D25.
- `qa-business`: revisar transversalmente D08, D10, D17 e D25 e registrar as facetas A01–H06.

## Testes adversariais

- `qa-interface`: ADV01, ADV02, ADV03, ADV04, ADV05, ADV14, ADV18, ADV19, ADV22, ADV23.
- `qa-security`: ADV06, ADV10, ADV13, ADV15, ADV20, ADV21.
- `qa-functional`: ADV07, ADV08, ADV09, ADV11, ADV12, ADV16, ADV17, ADV24.

## Suítes do framework

- `qa-api`: `SUITE:api`, `SUITE:openapi`.
- `qa-functional`: `SUITE:business_rules`.
- `qa-interface`: `SUITE:web_quality`, `SUITE:browser`.
- `qa-code-quality`: `SUITE:project_quality`.
- `qa-code-quality`: `SOURCE:AI-PROVENANCE`, cobrindo assinaturas e artefatos de autoria automatizada sem tratar heurística como prova.
- `qa-performance`: `SUITE:performance`.
- `qa-security`: `SUITE:security`, `SUITE:external_tools`.

## Seções integrais das fontes

- `qa-system-mapper`: `SRC:MASTER:0`, `SRC:BUSINESS:0`.
- `qa-code-quality`: `SRC:MASTER:1`, `SRC:MASTER:2`, `SRC:MASTER:3`, `SRC:MASTER:4`, `SRC:MASTER:5`.
- `qa-functional`, `qa-interface` e `qa-security`: dividir `SRC:MASTER:6`.
- `qa-consolidator`: aplicar `SRC:MASTER:7`; os especialistas devem registrar a preparação correspondente antes da consolidação.
- `qa-ui-ux`: `SRC:MASTER:8`, `SRC:MASTER:9`.
- `qa-business`: `SRC:BUSINESS:1` a `SRC:BUSINESS:9`.

Como o verificador anterior à consolidação exige a união dos 12 especialistas, atribuir `SRC:MASTER:7` ao `qa-code-quality` para confirmar que todos os campos necessários à entrega foram preparados; o `qa-consolidator` produz os arquivos.

## Regras de status

- Usar `complete` com ao menos uma evidência.
- Usar `blocked` somente com motivo e condição necessária para executar.
- Usar `not_applicable` somente depois de o agente avaliar o item e justificar por que o domínio não existe no escopo.
- O status do agente permanece `complete`; esses estados pertencem aos itens de cobertura.
