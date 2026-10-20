---
name: Depuração e diagnóstico
description: Use quando houver bug, falha de build, erro em runtime, comportamento inesperado ou problema de ambiente — método sistemático de causa raiz
---

## Método (naessa ordem)

1. **Reproduza.** Sem reprodução não há diagnóstico: comandos exatos, entrada e saída esperada/obtida. Se não reproduz, colete logs até que reproduza.
2. **Localize a origem do erro, não o sintoma.** Leia o stack trace completo: o primeiro frame **seu** (não de biblioteca) costuma apontar o lugar.
3. **Isole.** Reduza ao menor caso: um arquivo, uma função, um dado. Comente/metade o caminho até descobrir qual metade falha.
4. **Forme hipótese e teste-a** com um comando que possa refutá-la (`console.log` pontual, teste unitário, `git bisect`). Nunca troque várias coisas de uma vez.
5. **Corrija a causa.** Correção que só some com o sintoma vira dívida.
6. **Prove.** Rode o teste que falhava + a suíte completa + lint. Mostre a saída.

## Ferramentas por tipo de problema

| Problema | Primeiro passo |
| --- | --- |
| Build/compilação | `npm run build`, `flutter analyze`, `tsc --noEmit` — leia o **primeiro** erro |
| Teste falhando | rode só esse teste com reporter verboso; compare com baseline |
| Erro 5xx/404 em API | log do servidor + `curl -v` reproduzindo; confira rota e status |
| UI quebrada | Playwright MCP: console do navegador + screenshot do estado |
| lentidão | profile antes de otimizar (medir → hipótese → medir) |
| ambiente/PATH | `which <cmd>`, `echo $PATH`, versões (`node -v`, `flutter --version`) |
| Git | `git status`, `git log --oneline -10`, `git diff` |

## Regras

- **Nunca corrija o que não entendeu.** Se a causa não está clara, diga isso e continue investigando.
- Uma mudança por vez, com verificação entre elas.
- Erro novo = primeira leitura do stack trace inteiro, sem adivinhar.
- Registre a causa raiz no resumo final — é o que impede reincidência.
- Diagnóstico do próprio OpenCode: `opencode service status`, `opencode debug config`, log em `~/.local/share/opencode/log/opencode.log`.
