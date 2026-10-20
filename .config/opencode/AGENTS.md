# Regras globais de trabalho — OpenCode

Vale para todos os projetos. Projetos podem acrescentar o seu `AGENTS.md` no raiz.

## Idioma e comunicação

- Responda **preferencialmente em português brasileiro**, salvo pedido contrário.
- Responda de forma direta. Não repita o enunciado nem reescreva o que já foi dito.

## Antes de agir

- **Planeje antes de mudanças complexas**: múltiplos arquivos, refatorações, mudanças de dependência, esquema de banco ou infraestrutura.
- **Investigue a estrutura do projeto antes de editar**: leia `AGENTS.md` local, `package.json`, estrutura de pastas e o código envolvido. Nunca suponha o formato.
- Identifique a **causa de um erro antes de corrigi-lo**. Corrigir apenas o sintoma é proibido.

## Como alterar

- Faça **alterações pequenas e verificáveis**. Prefira vários blocos pequenos a uma reescrita grande.
- **Evite reescritas desnecessárias**: não "melhore" código que não precisa mudar para a tarefa.
- Não toque em arquivos gerados, lockfiles ou código que você não foi instruído a alterar.
- **Preserve `.env`, credenciais, tokens e dados sensíveis.** Nunca os copie, imprima ou comita.
- Peça **aprovação antes de alterações destrutivas** (apagar dados, resetar histórico, sobrescrever trabalho não commitado).
- **Não execute comandos remotos desconhecidos sem inspeção**: baixe, leia o conteúdo e só depois execute.

## Verificação

- Execute **testes e linters** sempre que existirem (`npm test`, `npm run lint`, `pytest`, etc.) após mudanças relevantes.
- **Não declare sucesso sem testes ou evidências.** Se não foi possível testar, diga isso explicitamente.
- Quando algo falhar, mostre o comando executado e a saída relevante, não apenas a conclusão.

## Resumo

- Ao final de cada tarefa, **resuma o que foi modificado**: arquivos, motivo e como validar.
- Evite consumir contexto e tokens desnecessariamente: não releia o que já leu, não imprima arquivos inteiros sem necessidade, não rode buscas redundantes.

## Operações que sempre exigem confirmação

Push, merge, exclusão/renomeação de branches, `gh api`, publicação de pacotes, `sudo`, remoção de arquivos e qualquer alteração em serviços externos. As permissões do `opencode.jsonc` já forçam essa confirmação — não tente contorná-las.
