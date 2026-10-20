---
name: Busca de código
description: Use para localizar arquivos, símbolos, trechos de código ou "onde isso é usado" em um projeto sem ler tudo
---

Obtenha a estrutura antes do conteúdo: leia o manifesto (`package.json`, `pubspec.yaml`, `pyproject.toml`) e `AGENTS.md` do projeto.

## Ordem de preferência

1. **`glob`** para caminhos: `src/**/*.test.ts`, `**/routes/*.py`, `**/*.{ts,tsx}`.
2. **`grep`** para conteúdo: identificador, string de erro, chamada de API.
3. **`read`** com offset/limit em trechos — nunca arquivos inteiros "só por via das dúvidas".

## Idiomas úteis de padrão

| Objetivo | Padrão |
| --- | --- |
| rotas/endpoints | `router\.(get\|post\|put\|delete)\(` |
| defs/exportações | `export (function\|const\|class)` |
| chamadas de função | `\bhandleSubmit\b` |
| config de framework | `defineConfig\|createBrowserRouter` |
| erros/strings | `throw new .*Error` |
| testes | `**/*.{test,spec}.{ts,tsx,py,dart}` |
| TODO/FIXME | `TODO\|FIXME\|HACK` |

## Regras

- Sempre informe **arquivo + linha** nas conclusões (`caminho:linha`).
- Restrinja o caminho de busca (`path`) para não varrer `node_modules`, `build`, `.dart_tool`.
- Busque também os **testes** de um arquivo — eles documentam o comportamento esperado.
- Se a busca devolver nada, generalize o padrão antes de concluir que "não existe".
- Evite repetir a mesma busca; anote o que já foi descartado.
