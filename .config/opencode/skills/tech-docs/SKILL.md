---
name: Documentação técnica
description: Use quando precisar consultar documentação oficial de uma lib/framework/API, verificar versões, changelogs ou comparar soluções técnicas
---

## Ordem de fontes

1. **Doc oficial** do que está sendo usado (MDN, docs do framework, `docs/` do repo).
2. **Repositório/changelog/RELEASES** para saber em qual versão algo mudou.
3. **`node_modules/<pkg>/README.md`** ou o manifesto instalado — a versão **real** no projeto vale mais que a doc da última release.
4. Busca web apenas quando as fontes acima não respondem.

## Sempre ancorar na versão instalada

```bash
npm ls <pkg> --depth=0     # versão real
npm view <pkg> versions    # histórico publicado
pacman -Qi <pkg>           # pacotes do sistema
```
Comparar a versão instalada com a doc evita responder sobre API que não existe na sua versão.

## Ao comparar alternativas

Tabela com: manutenção (última release), licença, dependências/peso, compatibilidade com o stack do projeto, custo/cotas, risco de lock-in.

## Regras

- **Nunca invente** nome de API, número de versão, preço ou limite de cota: sem fonte, escreva "não verificado".
- Cite a URL consultada e, quando relevante, a data.
- Separe **fato** (da doc) de **avaliação** (sua).
- Responda direto: conclusão primeiro, detalhe depois. Evite colar textos longos de doc no contexto.
