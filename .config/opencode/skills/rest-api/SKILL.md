---
name: Boas práticas de API REST
description: Use ao projetar, implementar ou revisar endpoints REST, contratos de API, versionamento, erros, paginação ou integração com bancos
---

## Contrato

- **URLs são substantivos** (`/produtos/123/variacoes`); **ações no verbo HTTP**: `GET` lê, `POST` cria, `PUT/PATCH` altera, `DELETE` remove.
- Status corretos: `200/201/204`, `400` (entrada inválida), `401` (sem autenticação), `403` (sem permissão), `404`, `409` (conflito), `422`, `429`, `500`.
- Versione desde o início (`/v1/...` ou header) — nunca quebre contrato sem aviso.

## Erros

Formato único e previsível:

```json
{ "error": { "code": "produto_nao_encontrado", "message": "...", "details": [] } }
```
Nunca vaze stack trace, SQL ou segredo em resposta. Logue o erro no servidor com um `request-id`.

## Segurança

- Valide **toda** entrada no servidor (tipos, faixas, formato) — o cliente não é confiável.
- Parameterize queries (nunca concatener SQL); proteja-se contra mass assignment (whitelist de campos).
- Autenticação por token/Bearer; **rate limiting** em login e endpoints caros; CORS restrito.
- Segredos só em variáveis de ambiente — nunca no código nem no `.env` versionado.

## Performance

- Paginação sempre (`cursor` > `offset` para dados grandes); filtre campos com `?fields=`.
- Evite N+1: resolva relacionamentos em lote.
- Cache com `ETag`/`Cache-Control` em recursos imutáveis.
- `POST` de criação devolve `201` + `Location`.

## Banco

- Migrations versionadas; nada de `ALTER` manual em produção sem plano de rollback.
- Transação em operações múltiplas; idempotência em `POST` de cobrança (chave de idempotência).

## Antes de declarar pronto

Teste o contrato: `curl` em cada endpoint com caso válido **e** inválido, conferindo status e corpo.
