# Performance e segurança

- Definir baseline e orçamento antes da execução; avaliar P95, P99, erro e throughput em conjunto.
- Separar carga, stress, spike e endurance; repetir medições para reduzir ruído.
- Correlacionar latência com CPU, memória, banco, filas e dependências quando houver observabilidade.
- Integrar ferramentas especializadas quando disponíveis: k6/JMeter, Lighthouse, Semgrep, Gitleaks, Trivy e ZAP.
- Confirmar manualmente achados heurísticos críticos antes de tratá-los como vulnerabilidade comprovada.
- Cobrir autenticação, autorização, IDOR/BOLA, sessão, segredos, dependências, containers e infraestrutura como código.
- Não usar um score simples como substituto para impacto, explorabilidade, confiança e cobertura.
- Habilitar `external_tools` somente após conferir executáveis e argumentos. Os adaptadores aceitos são Semgrep, Gitleaks, Trivy, Lighthouse, k6 e ZAP; a suíte inteira exige autorização explícita.
