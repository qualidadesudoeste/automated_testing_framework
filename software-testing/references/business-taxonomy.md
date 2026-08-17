# Taxonomia de coerência funcional

Aplicar os códigos como facetas do achado. Um problema pode ter várias facetas, mas deve aparecer uma única vez quando a causa raiz for a mesma.

## A — CRUD e ciclo de vida

- `A01` cadastro-fantasma; `A02` registro imortal; `A03` exclusão cega.
- `A04` edição amputada; `A05` soft delete inconsistente; `A06` duplicidade permitida.
- `A07` órfão por design; `A08` cadastro sem consulta; `A09` inativação sem efeito.

## B — interface que promete e não entrega

- `B01` filtro decorativo; `B02` botão morto; `B03` ordenação falsa.
- `B04` busca ilusória; `B05` KPI estático; `B06` label enganosa.
- `B07` confirmação sem efeito; `B08` estado vazio ausente; `B09` feedback ausente.

## C — perfis, permissões e acesso

- `C01` perfil engessado; `C02` permissão não aplicada; `C03` menu protegido, rota exposta.
- `C04` primeiro administrador impossível; `C05` autodestruição/último admin; `C06` escopo de dados ausente.

## D — estados e tempo

- `D01` estado inalcançável; `D02` estado terminal precoce; `D03` transição sem guarda.
- `D04` prazo sem motor; `D05` regra apenas documentada; `D06` ação sem reversão; `D07` ordem quebrada.

## E — fluxo de uso

- `E01` dependência circular; `E02` beco sem saída; `E03` pré-requisito invisível.
- `E04` obrigatoriedade invertida; `E05` caminhos divergentes; `E06` perda de contexto; `E07` tela órfã.

## F — validação e integridade

- `F01` validação somente no cliente; `F02` divergência entre camadas; `F03` limite ausente.
- `F04` erro técnico exposto; `F05` operação sem transação; `F06` cálculo divergente.

## G — auditoria e privacidade

- `G01` ação sensível sem log; `G02` log incompleto; `G03` auditoria não consultável.
- `G04` auditoria mutável; `G05` dado pessoal sem controle; `G06` coleta excessiva.

## H — escala e operação

- `H01` lista sem paginação; `H02` ação em massa ausente; `H03` relatório preso à tela.
- `H04` concorrência ignorada; `H05` histórico ausente; `H06` anexo sem regra.

## Uso correto

- Não inventar requisito para enquadrar um padrão.
- Classificar como ambiguidade quando depender de decisão de negócio.
- Escrever impacto em linguagem compreensível para gestor, evitando jargão de implementação.
- Incluir critério de aceite em BDD e pergunta ao cliente quando houver ambiguidade.
