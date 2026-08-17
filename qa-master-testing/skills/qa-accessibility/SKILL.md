---
name: qa-accessibility
description: Auditar acessibilidade de aplicações segundo WCAG 2.2 AA e eMAG quando aplicável, combinando automação, inspeção e testes reais de teclado, foco, zoom, contraste e leitor de tela. Usar como especialista obrigatório do QA Mestre ou para avaliações de acessibilidade web.
---

# Testar acessibilidade

## Executar

- Rodar axe-core local nas jornadas representativas e confirmar violações de maior impacto.
- Testar navegação completa por teclado, ordem TAB, foco visível, skip link, armadilhas e retorno de foco.
- Verificar landmarks, headings, labels, descrição de erro, `aria-invalid`, `aria-live`, nomes acessíveis, alt e tabelas.
- Verificar modal com foco preso, ESC, fundo inerte e retorno ao gatilho.
- Medir contraste de texto, texto grande, ícones, bordas e estados; informação não pode depender só de cor.
- Testar zoom 200%, reflow 320px, alvo de toque, reduced motion e autocomplete.
- Executar leitura de fluxo crítico com NVDA/VoiceOver quando disponível; automação não substitui esse teste.
- Conferir requisitos eMAG e linguagem pública quando o sistema governamental estiver em escopo.

## Entregar

Gravar `agents/qa-accessibility.json` com critério WCAG/eMAG, impacto, elemento, evidência, reprodução, automação/manual e limitações de tecnologia assistiva.
