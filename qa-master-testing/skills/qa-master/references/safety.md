# Segurança operacional

- Classificar o alvo como local, privado ou externo antes da execução.
- Usar `--dry-run` para validar plano, DNS, suítes e limites sem acessar o sistema.
- Exigir autorização formal para carga, stress, spike, scan, injeção, força bruta ou jornadas mutáveis.
- Manter produção bloqueada por padrão; preferir ambiente isolado e dados descartáveis.
- Definir allowlist, janela, taxa, duração, usuários máximos, contato de emergência e critério de interrupção.
- Interromper diante de degradação não prevista, impacto em terceiros ou escopo ambíguo.
- Sanitizar tokens, cookies, PII e corpos de resposta antes de salvar evidências.

