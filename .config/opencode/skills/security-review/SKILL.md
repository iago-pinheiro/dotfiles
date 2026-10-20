---
name: Revisão de segurança
description: Use para revisar código, dependências ou configuração sob a ótica de segurança — vulnerabilidades, vazamento de segredos, autenticação e permissões
---

## Checklist permanente

**Segredos**
- `.env` ou chaves commitados? Procure `API_KEY`, `password`, `BEGIN PRIVATE KEY`, `ghp_`, `sk-`.
- Segredo em log, resposta de API ou mensagem de erro? Isso é vazamento.
- `.gitignore` cobre `.env` e `*.pem`? Histórico já contém segredo (`git log -p -S"chave"`)? — se sim, trocar a credencial é prioridade.

**Entrada e injeção**
- SQL com string concatenada? Use query parametrizada.
- `exec`/`system`/`eval` com dado do usuário? Injeção de comando.
- HTML renderizado sem escape? XSS (`dangerouslySetInnerHTML`, `|safe`, `innerHTML`).
- Upload sem validação de tipo/tamanho/caminho?

**Autenticação e autorização**
- Autorização checada **no servidor** em toda rota (não só no cliente)?
- Sessão/token com expiração, revogação e comparação em tempo constante?
- Rate limiting em login/reset de senha?
- IDOR: usuário consegue ler alterando o `id` na URL?

**Dados e transporte**
- HTTPS obrigatório; cookies `HttpOnly`/`Secure`/`SameSite`.
- Validação de schema de toda entrada; massa de dados exposta (`mass assignment`)?
- Informação sensível em URL (query string vai para logs).

**Dependências e infra**
- Dependências com CVE conhecido? `npm audit`, `pip-audit`, `flutter pub outdated`.
- Container rodando como root? Porta exposta sem necessidade?
- Permissões amplas (`chmod 777`, CORS `*` com credenciais, policy admin de mais).

## Formato do relatório

1. **Severidade**: Crítico / Alto / Médio / Baixo.
2. **Achado**: `arquivo:linha` — o que é possível fazer com isso (explorabilidade).
3. **Correção sugerida**: trecho concreto.
4. **Evidência**: como reproduzir/verificar.

Não corrija sozinho em revisões: reporte. Só corrija quando o pedido for correção, e com teste.
