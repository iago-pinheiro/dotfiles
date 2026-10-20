---
name: Pacotes do sistema (sudo sem senha para pacman/paru)
description: Use quando precisar instalar, atualizar ou remover pacotes no CachyOS (pacman/paru) com sudo — o usuário liberou NOPASSWD apenas para esses binários
---

## O que está liberado

O usuário criou `/etc/sudoers.d/opencode-pacman` liberando **sem senha** apenas:

```
iago ALL=(ALL) NOPASSWD: /usr/bin/pacman, /usr/bin/paru
```

Nada além disso é liberado (por exemplo, `cat /etc/shadow` continua pedindo senha).
A senha do usuário **não** é guardada em nenhum lugar: nunca a coloque em skills, scripts ou arquivos.

## Como usar

- Use sempre `sudo -n` (não interativo). Se falhar, peça ao usuário — não peça a senha.
- Pacotes oficiais: `sudo -n pacman -S --needed --noconfirm <pkgs>`
- Pacotes do AUR: `paru -S --needed --noconfirm <pkgs>` (o paru chama o sudo internamente)
- Atualizar índices/banco: `sudo -n pacman -Sy`
- Conferir depois: `pacman -Q <pkg>` e o binário com `command -v <cmd>`

## Cuidados

- Atualização total (`-Syu`), remoção (`-Rns`), troca de kernel e `-U`/downgrades: **pedir confirmação**.
- Revise os PKGBUILDs do AUR antes de instalar (não use `--noconfirm` em PKGBUILD não revisado).
- Não use `--overwrite` sem autorização explícita.

## Rollback

- Remover a regra: `sudo rm /etc/sudoers.d/opencode-pacman` (exige a senha do usuário).
- Desinstalar um pacote: `sudo -n pacman -Rns <pkg>` (pedir confirmação).
