#!/usr/bin/env bash
# install.sh — instala os pacotes e aplica estes dotfiles na máquina.
#
#   ./install.sh                 # pacotes + dotfiles + pós-instalação
#   ./install.sh --no-packages   # só os dotfiles (já tem os pacotes)
#   ./install.sh --flatpak       # inclui também packages/flatpak.txt
#   ./install.sh --dry-run       # mostra tudo o que faria, sem tocar em nada
#
# O repositório espelha o $HOME: .config/ghostty/config -> ~/.config/ghostty/config
# Tudo que já existe em ~ é salvo antes em ~/.dotfiles-backup-<data>/
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$REPO/manifest.txt"
BACKUP="$HOME/.dotfiles-backup-$(date +%Y%m%d-%H%M%S)"

COM_PACOTES=1
COM_FLATPAK=0
DRY=0

uso() { sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
    case "$1" in
        --no-packages) COM_PACOTES=0 ;;
        --flatpak) COM_FLATPAK=1 ;;
        --dry-run) DRY=1 ;;
        -h|--help) uso; exit 0 ;;
        *) echo "opção desconhecida: $1" >&2; uso; exit 1 ;;
    esac
    shift
done

roda() {
    if [ "$DRY" = 1 ]; then printf '  (dry-run) %s\n' "$*"; else printf '  $ %s\n' "$*"; "$@"; fi
}
lista() { grep -vE '^[[:space:]]*(#|$)' "$1" || true; }

echo "== 1/6 — checagens"
command -v pacman >/dev/null || { echo "este repositório assume Arch/CachyOS (pacman)." >&2; exit 1; }
case "${XDG_CURRENT_DESKTOP:-}" in
    *KDE*) echo "  sessão Plasma detectada: ${XDG_CURRENT_DESKTOP}" ;;
    *) echo "  aviso: a sessão atual não é Plasma (${XDG_CURRENT_DESKTOP:-?}); passos de KDE serão pulados." ;;
esac
[ "$DRY" = 1 ] && echo "  modo dry-run: nada será alterado"

if [ "$COM_PACOTES" = 1 ]; then
    echo
    echo "== 2/6 — pacotes oficiais (packages/pacman.txt)"
    mapfile -t NATIVOS < <(lista "$REPO/packages/pacman.txt")
    echo "  ${#NATIVOS[@]} pacotes na lista (sudo/paru vai pedir senha)"
    if [ "$DRY" = 1 ]; then
        roda sudo pacman -S --needed --noconfirm "${NATIVOS[@]}"
    else
        sudo pacman -S --needed --noconfirm "${NATIVOS[@]}" || {
            echo "  aviso: falhou algum pacote (lista veio de outra máquina?)." >&2
            echo "  edite packages/pacman.txt e rode de novo se precisar." >&2
        }
    fi

    echo
    echo "== 3/6 — pacotes do AUR (packages/aur.txt)"
    if command -v paru >/dev/null; then
        if [ "$DRY" = 1 ]; then
            echo "  (dry-run) paru -S --needed - < packages/aur.txt"
        else
            paru -S --needed --noconfirm - < <(lista "$REPO/packages/aur.txt") || \
                echo "  aviso: falha em algum pacote do AUR (veja packages/aur.txt)" >&2
        fi
    else
        echo "  paru não encontrado. Instale (ex.: paru-bin do AUR) e rode:"
        echo "    paru -S --needed - < $REPO/packages/aur.txt"
    fi

    if [ "$COM_FLATPAK" = 1 ] && command -v flatpak >/dev/null; then
        while read -r app; do
            [ -n "$app" ] && roda flatpak install -y flathub "$app"
        done < <(lista "$REPO/packages/flatpak.txt")
    fi
else
    echo
    echo "== 2/6 e 3/6 — pacotes: pulados (--no-packages)"
fi

echo
echo "== 4/6 — aplicando dotfiles (backup em $BACKUP)"
while IFS= read -r caminho; do
    case "$caminho" in ''|\#*) continue ;; esac
    src="$REPO/$caminho"
    dst="$HOME/$caminho"
    [ -e "$src" ] || { printf '  ! %s (ausente no repositório)\n' "$caminho" >&2; continue; }

    # destino já aponta para o repo (stow): não mexe
    real="$(readlink -f -- "$dst" 2>/dev/null || true)"
    case "$real" in
        "$REPO"/*) printf '  = %s (já é symlink do repo)\n' "$caminho"; continue ;;
    esac

    if [ -e "$dst" ]; then
        if [ "$DRY" = 1 ]; then
            printf '  (dry-run) backup: %s\n' "$caminho"
        else
            mkdir -p "$BACKUP/$(dirname "$caminho")"
            cp -a "$dst" "$BACKUP/$caminho"
        fi
    fi

    mkdir -p "$(dirname "$dst")"
    if [ "$DRY" = 1 ]; then
        printf '  (dry-run) instalar: %s\n' "$caminho"
    else
        rm -rf "$dst"
        cp -aL "$src" "$dst"
        printf '  + %s\n' "$caminho"
    fi
done < "$MANIFEST"

# ---- ajuste de caminhos absolutos (ex.: /home/iago -> $HOME da máquina nova) ----
ORIG="$(cat "$REPO/.dotfiles-origem" 2>/dev/null || true)"
if [ -n "$ORIG" ] && [ "$ORIG" != "$HOME" ]; then
    echo
    echo "  ajustando caminhos $ORIG -> $HOME"
    ajusta_arquivo() {
        [ -f "$1" ] || return 0
        grep -Iq . "$1" 2>/dev/null || return 0          # ignora binários
        grep -qF -- "$ORIG" "$1" 2>/dev/null || return 0
        if [ "$DRY" = 1 ]; then
            printf '  (dry-run) caminho em %s\n' "${1#"$HOME"/}"
        else
            sed -i "s|$ORIG|$HOME|g" "$1"
            printf '  ~ %s\n' "${1#"$HOME"/}"
        fi
    }
    while IFS= read -r caminho; do
        case "$caminho" in ''|\#*) continue ;; esac
        alvo="$HOME/$caminho"
        if [ -d "$alvo" ]; then
            while IFS= read -r f; do ajusta_arquivo "$f"; done \
                < <(grep -rlIF -- "$ORIG" "$alvo" 2>/dev/null || true)
        else
            ajusta_arquivo "$alvo"
        fi
    done < "$MANIFEST"
fi

echo
echo "== 5/6 — pós-instalação (KDE)"
if [ "$DRY" = 1 ]; then
    echo "  (dry-run) kbuildsycoca6 / daemon-reload / atalhos / barra / tema do terminal / wallpaper / kwin reconfigure"
else
    command -v kbuildsycoca6 >/dev/null && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
    systemctl --user daemon-reload 2>/dev/null || true
    command -v xdg-user-dirs-update >/dev/null && xdg-user-dirs-update 2>/dev/null || true

    if pgrep -x plasmashell >/dev/null; then
        [ -f "$HOME/.local/share/kde-rice/kde-keybinds.py" ] && \
            python3 "$HOME/.local/share/kde-rice/kde-keybinds.py" || true
        if [ -f "$HOME/.local/share/kde-rice/panel-colorizer.py" ]; then
            python3 "$HOME/.local/share/kde-rice/panel-colorizer.py" || true
            systemctl --user restart plasma-plasmashell.service || true
            sleep 4
        fi
    fi

    [ -f "$HOME/.local/share/kde-rice/accent-sync.py" ] && \
        python3 "$HOME/.local/share/kde-rice/accent-sync.py" || true

    # wallpaper: não é versionado (são suas imagens). Se a pasta existir e já
    # houver um wallpaper aplicado, nada a fazer; use "Trocar wallpaper" depois.

    command -v qdbus6 >/dev/null && qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
fi

echo
echo "== 6/6 — pronto!"
cat <<FIM

O que ainda depende de você (uma vez):

  1. Temas que ficam fora do git por tamanho:
       Tela-circle-dark     -> ~/.local/share/icons/   (paru -S tela-circle-icon-theme-git)
       WinSur-dark-cursors  -> ~/.icons/               (veja docs/TROUBLESHOOTING.md)
     Depois escolha em Configurações do Sistema > Aparência.

  2. Acentos no Ghostty: o GTK só lê GTK_IM_MODULE ao iniciar, então:
       systemctl --user restart app-com.mitchellh.ghostty.service

  3. Wallpaper: coloque suas imagens em ~/Imagens/Wallpapers e use o app
     "Trocar wallpaper" (KRunner/menu). Ele sincroniza o accent sozinho.

  4. Saia e entre de novo na sessão Plasma para painel/KWin/atalhos/temas entrarem em vigor.

Verificação rápida:
       Meta+1..5        troca de área de trabalho
       Meta+Shift+2     manda a janela ativa para a área 2
       Meta+Retorno     ghostty      Meta+Shift+Retorno  Brave      Meta+Espaço  KRunner

Backup do que existia antes: $BACKUP
FIM
