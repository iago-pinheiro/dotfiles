---
name: Fluxo React e Node.js
description: Use em projetos JavaScript/TypeScript com React e Node — estrutura, build, testes, tipos, performance de render e APIs Express/Fastify
---

## Antes de mexer

Leia `package.json` (scripts e versões), `tsconfig.json`, config do bundler (Vite/Next), `AGENTS.md` local e a pasta de testes. Identifique package manager pelo lockfile (`package-lock.json` → npm, `yarn.lock` → yarn, `pnpm-lock.yaml` → pnpm, `bun.lockb` → bun) e **use o mesmo**.

## Node/TypeScript

- `npm run build` ou `npx tsc --noEmit` para checar tipos após mudanças.
- Prefira `import` ESM e tipos explícitos em fronteiras de API (`zod`/`TypeScript` nos dados externos).
- Evite `any`; use `unknown` + narrowing em dados vindos de fora.
- Endpoint: valide entrada, trate erro com middleware centralizado, nunca pare com processo em erro não tratado.

## React

- Estado local no componente; compartilhado via contexto/store; servidor via query cache (React Query/SWR) — não duplique fonte da verdade.
- `useEffect` só para sincronizar com sistemas externos; dependências completas no array.
- Listas: `key` estável e única (nunca índice em lista reordenável).
- Performance: memoize só com medição (`React DevTools Profiler`) — otimização cega é desperdício.
- Extraia componentes por responsabilidade, não por tamanho.

## Testes

- Lógica pura: unitário (Vitest/Jest). Componentes: Testing Library comportamental. Fluxo crítico: Playwright E2E.
- Rode `npm test` e `npm run lint` ao final e **mostre a saída**.

## Checklist de saída

Build compila → tipos OK → lint OK → testes OK → resumo do que mudou e como validar.
