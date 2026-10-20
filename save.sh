#!/usr/bin/env bash
# save.sh — sincroniza o estado ATUAL do sistema para dentro do repositório.
#
# Use depois de mexer em qualquer configuração, para o repositório voltar a
# refletir o sistema (e então commitar).
#
#   ./save.sh             # copia tudo que está em manifest.txt
#   ./save.sh --dry-run   # só lista o que seria copiado
#
# Observações:
#  - o repositório espelha o $HOME (ex.: .config/ghostty/config -> .config/ghostty/config)
#  - caminhos que já são symlink para dentro do repo (stow) são deixados como estão
#  - symlinks são dereferenciados (o repo guarda arquivos de verdade)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$REPO/manifest.txt"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

[ -f "$MANIFEST" ] || { echo "manifest.txt não encontrado" >&2; exit 1; }

copiados=0
ligados=0
ausentes=0

while IFS= read -r path; do
    case "$path" in ''|\#*) continue ;; esac
    src="$HOME/$path"
    dst="$REPO/$path"

    if [ ! -e "$src" ]; then
        printf '  ! %-52s (não existe no sistema)\n' "$path" >&2
        ausentes=$((ausentes + 1))
        continue
    fi

    real="$(readlink -f -- "$src" 2>/dev/null || true)"
    case "$real" in
        "$REPO"/*)
            printf '  = %-52s (já é symlink do repo)\n' "$path"
            ligados=$((ligados + 1))
            continue
            ;;
    esac

    copiados=$((copiados + 1))
    if [ "$DRY" = 1 ]; then
        printf '  ~ %s\n' "$path"
        continue
    fi

    # copia primeiro para um temporário e só depois troca: assim symlinks
    # internos que apontam para dentro do repo continuam válidos durante a cópia
    tmp="$(mktemp -d)"
    cp -aL "$src" "$tmp/novo"
    rm -rf "$dst"
    mkdir -p "$(dirname "$dst")"
    mv "$tmp/novo" "$dst"
    rmdir "$tmp"
    printf '  + %s\n' "$path"
done < "$MANIFEST"

if [ "$DRY" = 1 ]; then
    echo "(dry-run: nada foi escrito — $copiados a copiar, $ligados já ligados, $ausentes ausentes)"
else
    printf '%s\n' "$HOME" > "$REPO/.dotfiles-origem"
    echo
    echo "$copiados copiados, $ligados já ligados por symlink, $ausentes ausentes."
    echo "Revise com: git -C \"$REPO\" status --short"
fi
