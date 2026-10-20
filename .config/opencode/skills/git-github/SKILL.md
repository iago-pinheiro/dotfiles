---
name: Git e GitHub
description: Use quando for trabalhar com Git/GitHub — commits, branches, diffs, PRs, issues, revisão de histórico ou diagnóstico de conflito
---

## Inspecionar (sempre antes de alterar)

```bash
git status --short          # estado
git log --oneline -15       # histórico
git diff                    # não stageado
git diff --staged           # staged
git diff main...HEAD        # o que a branch inteira muda
git branch -vv              # branches e upstream
git show <sha> --stat       # um commit
```

Diffs grandes: leia por arquivo (`git diff -- <path>`) e evite imprimir o diff inteiro no contexto.

## Fluxo de contribuição

1. `git switch -c <tipo>/<descricao>` (ex.: `fix/login-timeout`).
2. Alterações pequenas → `git add <arquivos>` explícitos (nunca `git add .` cegamente).
3. Commit com mensagem no imperativo e escopo claro: `fix(auth): evita timeout em token expirado`.
4. `git push -u origin <branch>` — **exige confirmação**.
5. PR com `gh pr create --title --body` — também exige confirmação.

## Regras de segurança

- `push`, `merge`, `reset`, `rebase`, `restore`, `clean`, `branch -d/-D` e `gh api` **sempre pedem aprovação** — não tente contornar.
- Antes de push: `git log --oneline origin/<branch>..HEAD` para revisar o que sai.
- Nunca commite `.env`, chaves, tokens ou dados de usuário. Verifique com `git status` e `git diff --cached --stat`.
- Nunca use `--force` em branch compartilhada; se for inevitável, explique o risco e peça autorização.

## Diagnóstico rápido

| Problema | Comando |
| --- | --- |
| commit errado já commitado | `git commit --amend` (local) / `git revert <sha>` (publicado) |
| desfazer alteração não commitada | `git restore <path>` — destrutivo, pedir confirmação |
| branch atrasada | `git fetch origin && git rebase origin/<branch>` |
| conflito | `git status` → resolver → `git add <path>` → `git rebase --continue` |
| achar quem introduziu bug | `git log -S"<trecho>"` ou `git bisect start` |

Sempre confirme remoto com `git remote -v` antes de operações que afetam origin.
