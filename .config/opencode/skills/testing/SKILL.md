---
name: Testes automatizados
description: Use para executar, criar ou corrigir testes unitários/integração/E2E e para validar mudanças com evidência
---

## Antes de escrever qualquer teste

1. Descubra o runner já usado pelo projeto: `package.json` (`scripts.test`), `pytest.ini`/`pyproject.toml`, `pubspec.yaml`, `Makefile`, CI (`.github/workflows`).
2. Rode a suíte **antes** da mudança para ter o baseline: se já falhava, você não causou.
3. Use o framework existente — **nunca introduza outro sem pedido**.

## Comandos comuns

| Stack | Unitário | Lint/Formato |
| --- | --- | --- |
| Node/JS | `npm test` | `npm run lint` |
| Vitest | `npx vitest run` | `npx prettier --check .` |
| Python | `pytest -q` | `ruff check .` |
| Flutter/Dart | `flutter test` | `flutter analyze` |
| API (E2E) | `npm run test:e2e` | — |

## Ao criar testes

- Cubra o **comportamento observável**, não a implementação.
- Priorize: caminho feliz → caso de borda → erro/timeout.
- Um teste por afirmação clara; nome descreva o cenário (`deve rejeitar token expirado`).
- Nunca altere o teste só para fazer passar; se o teste estiver errado, justifique e mostre o diff.

## Evidência obrigatória

- Mostre o **comando exato** e a **saída** (passou: `X passed`).
- Se não rodou (sem dependência, sem ambiente), escreva isso explicitamente — nunca diga "está funcionando" sem execução.
- Após corrigir bug: teste que reproduce o bug **falhando antes** e **passando depois**.
