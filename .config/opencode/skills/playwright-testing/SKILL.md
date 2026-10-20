---
name: Playwright e testes de UI
description: Use para automatizar navegador, testar apps em localhost, validar formulários/fluxos, capturar erros de UI e gerar relatório de problemas
---

Ferramentas do servidor MCP `playwright` (já configurado globalmente). Use `codemode: false` — screenshots chegam como imagem.

## Setup

- App local: suba o dev server (ex.: `npm run dev`) em segundo plano e **aguarde** responder antes de navegar: `http://localhost:3000`.
- Espere elementos com o método de espera próprio (`wait_for` / `expect`), nunca `sleep` fixo.
- Navegador padrão: Chromium, instalado em `~/.cache/ms-playwright`.

## Fluxo de verificação

1. Navegar para a URL inicial.
2. Capturar erros de console e requisições falhas (isso revela 500/404/CORS).
3. Interagir: clicar, preencher **apenas com dados fictícios** (`teste@teste.dev`, `123456`).
4. Verificar o estado esperado (texto, visibilidade, URL, conteúdo do store).
5. Screenshot ao final de cada passo crítico — é a evidência que vai no relatório.

## Boas práticas

- Teste fluxos ponta a ponta (login → ação → resultado), não só elementos isolados.
- Ao falhar, registre: URL, passo, seletor esperado, o que apareceu, screenshot e erro de console.
- Nunca use credenciais reais nem toque em ambientes de produção.
- Prefira seletores por `getByRole`/`getByLabel`/`getByText` a `css`/`xpath` frágeis.
- Feche o navegador ao terminar.

## Relatório de problemas (padrão)

```
[BLOQUEADOR|ALTO|MÉDIO|BAIXO] título
- Reprodução: passo a passo
- Esperado / Obtido
- Evidência: screenshot + erro de console
- Arquivo provável: caminho:linha
```

Limite: o MCP não altera código — correções ficam com o usuário/Developer.
