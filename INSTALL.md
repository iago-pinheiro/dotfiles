# Instalação — passo a passo

Este é o tutorial completo. O caminho curto é `./install.sh`; abaixo está o que
ele faz, o que **não** faz (e precisa ser manual) e como conferir cada parte.

Testado em **CachyOS / Arch + KDE Plasma 6.8 (Wayland), KWin 6.8, Frameworks 6.31,
Qt 6.12, Ghostty 1.3.1**. Em versões próximas deve funcionar; em versões muito
antigas de Plasma 5, não.

---

## 0. Requisitos

- Arch Linux ou derivado (CachyOS, EndeavourOS...) com `pacman`.
- KDE Plasma 6 instalado e sessão **Wayland** (`echo $XDG_SESSION_TYPE` = `wayland`).
- `git` e um helper de AUR — o script usa `paru` (se não tiver: `sudo pacman -S --needed base-devel git && paru` ou o binário `paru-bin` do AUR).
- ~2 GB livres em disco (pacotes + temas).

```fish
sudo pacman -S --needed git base-devel
command -v paru; or echo "instale o paru antes de continuar"
```

---

## 1. Clonar

```fish
git clone https://github.com/SEU-USUARIO/dotfiles.git ~/dotfiles
cd ~/dotfiles
```

> Se você já tem um `~/dotfiles` (por exemplo, um clone antigo usado com `stow`),
> mova/renomeie antes. O instalador faz backup dos arquivos de configuração, mas
> não de um repositório inteiro.

---

## 2. Instalar

```fish
./install.sh
```

O script executa 6 etapas:

1. **Checagens** — confirma `pacman` e avisa se a sessão não for Plasma.
2. **Pacotes oficiais** — `sudo pacman -S --needed $(cat packages/pacman.txt)`
   (224 pacotes: Plasma, KWin, Ghostty, fastfetch, fontes, imagemagick...).
3. **AUR** — `paru -S --needed - < packages/aur.txt`
   (klassy, krema, kwin-scripts-krohnkite-git, plasma6-applets-panel-colorizer, ulauncher, artcraft).
   *Opcional:* `--flatpak` instala também `packages/flatpak.txt`.
4. **Dotfiles** — copia cada caminho de `manifest.txt` para o `$HOME`.
   O que já existia vai para `~/.dotfiles-backup-<data>/`.
   Caminhos que já são symlink para dentro do repo (stow antigo) são deixados como estão.
5. **Pós-instalação** — `kbuildsycoca6`, `systemctl --user daemon-reload`,
   reaplica atalhos, aplica a barra (Panel Colorizer), regenera o tema do Ghostty
   e o fastfetch, aplica o wallpaper e manda o KWin reler a config.
6. **Resumo** — o que ainda depende de você.

Variações:

```fish
./install.sh --no-packages   # só os dotfiles (útil em máquina já pronta)
./install.sh --dry-run       # mostra tudo sem alterar nada
./install.sh --flatpak       # inclui os flatpaks
```

> **Atenção à lista de pacotes:** `packages/pacman.txt` é um retrato desta
> máquina e inclui coisas específicas de CachyOS (kernel `linux-cachyos`,
> `limine`, `plymouth`, `chwd`...). Numa máquina diferente, prefira
> `./install.sh --no-packages` e instale à mão o que faltar — ou edite a lista
> antes. Em CachyOS já instalado, `--needed` só instala o que está faltando.

---

## 3. O que o script **não** faz (manual, uma vez)

### 3.1 Temas de ícones e cursores

Ficam fora do git por tamanho.

**Ícones — Tela-circle-dark**

```fish
paru -S --needed tela-circle-icon-theme-git
# confere se apareceu a variante escura:
ls ~/.local/share/icons | grep -i tela
```

Se o pacote não gerar a variante `dark`, instale pelo repositório oficial:

```fish
git clone https://github.com/vinceliuice/Tela-circle-icon-theme.git /tmp/tela
cd /tmp/tela && ./install.sh -d ~/.local/share/icons
```

**Cursores — WinSur-dark-cursors**

Não existe no AUR. Baixe o tema (por exemplo do GNOME-Look/Pling, procurando por
"WinSur cursors") e deixe a pasta como `~/.icons/WinSur-dark-cursors/` com
`index.theme` dentro. Depois:

```fish
kwriteconfig6 --file kdeglobals --group Icons --key Theme Tela-circle-dark
kwriteconfig6 --file kcminputrc --group Mouse --key cursorTheme WinSur-dark-cursors
kbuildsycoca6 --noincremental
```

(ou escolha em **Configurações do Sistema → Aparência**).

### 3.2 Acentos e teclas mortas no Ghostty

O `install.sh` já deixa o drop-in do systemd no lugar
(`~/.config/systemd/user/app-com.mitchellh.ghostty.service.d/im.conf` com
`GTK_IM_MODULE=simple`), mas o GTK só lê essa variável **ao iniciar** o processo:

```fish
systemctl --user restart app-com.mitchellh.ghostty.service
```

Isso fecha as janelas do Ghostty (e a TUI do OpenCode, se estiver aberta ali) —
faça quando puder. Alternativa: sair e entrar na sessão. Teste digitando
`ção`, `ação`, `ãõ` no terminal.

Detalhes e o porquê: [TROUBLESHOOTING](TROUBLESHOOTING.md#2-acentos-e-teclas-mortas-no-ghostty-gtk-420).

### 3.3 Wallpaper e cor de destaque

Os wallpapers **não** ficam no repositório (são ~160 MB de imagens). Coloque os
seus em `~/Imagens/Wallpapers` e escolha pelo app **"Trocar wallpaper"**
(KRunner/menu) ou pelo terminal:

```fish
wallpaper-switcher                               # seletor nativo do KDE (kdialog)
# ou
plasma-apply-wallpaperimage ~/Imagens/Wallpapers/sua-imagem.jpg
python3 ~/.local/share/kde-rice/accent-sync.py   # terminal + fastfetch no novo accent
```

O painel (borda + vidro) acompanha a cor de destaque **ao vivo** (o Panel Colorizer
usa a fonte "System"), então não precisa de script. O `wallpaper-switcher` cuida
do `accent-sync.py` (tema do Ghostty + fastfetch). Se você trocar o wallpaper
**pelo menu do Plasma**, rode o acabamento na mão:

```fish
python3 ~/.local/share/kde-rice/accent-sync.py
python3 ~/.local/share/kde-rice/panel-colorizer.py   # só se a barra não acompanhar
```

### 3.4 Conferir o Krohnkite (tiling)

O pacote AUR instala o script e o `kwinrc` versionado já vem com
`[Plugins] krohnkiteEnabled=true`. Se as janelas não estiverem em tiling:

```fish
kwriteconfig6 --file kwinrc --group Plugins --key krohnkiteEnabled true
qdbus6 org.kde.KWin /KWin reconfigure
```

Configuração do Krohnkite (layouts, gaps, atalhos) fica em
`~/.config/kwinrc`, grupo `[Script-krohnkite]`.

### 3.5 Krema (dock)

Vem do AUR (`krema`) com autostart do próprio pacote
(`/etc/xdg/autostart/com.bhyoo.krema.autostart.desktop`). A configuração
(`~/.config/kremarc`) é restaurada pelo script — **o Krema só lê esse arquivo ao
iniciar**, então depois de instalá-lo:

```fish
systemctl --user restart com.bhyoo.krema     # ou saia e entre na sessão
```

Se o serviço não existir, feche/abra o Krema pelo menu ou reinicie a sessão.

### 3.6 Fontes

Já vêm na lista de pacotes: `ttf-jetbrains-mono-nerd` (terminal/código),
`inter-font` (interface), `noto-fonts-emoji` (emoji). O `kdeglobals` já aponta
para elas; se trocar de máquina com outra escala de DPI, ajuste em
**Configurações → Fontes**.

---

## 4. Checklist pós-instalação

Saia e entre na sessão (ou reinicie). Depois confira:

| Item | Como conferir |
|---|---|
| Barra superior | fundo translúcido + borda na cor do wallpaper |
| Dock | passa o mouse na borda inferior → Krema aparece |
| Tiling | abrir duas janelas: elas se dividem (Krohnkite) |
| Áreas de trabalho | `SUPER+2` muda de área; `SUPER+Shift+2` manda a janela |
| Terminal | `SUPER+Enter` → Ghostty com fundo escuro quente e cursor accent |
| Acentos | digitar `ção` no Ghostty |
| fastfetch | `fastfetch` no terminal → realces em tons do accent |
| Wallpaper | "Trocar wallpaper" no KRunner/menu, ou `wallpaper-switcher` no terminal → seletor nativo do KDE |
| KRunner | `SUPER+Espaço` |

Comandos úteis de diagnóstico:

```fish
# cor de destaque atual (RGB) e o que a decoração usa
kreadconfig6 --file kdeglobals --group General --key AccentColor
kreadconfig6 --file kdeglobals --group "Colors:View" --key DecorationFocus

# o que o painel está usando
kreadconfig6 --file plasma-org.kde.plasma.desktop-appletsrc \
             --group Containments --group 32 --group Applets --group 34 --group Configuration --group General --key focusColor

# tema gerado do Ghostty
head -20 ~/.config/ghostty/themes/kde-accent
```

---

## 5. Reverter

- **Arquivos**: tudo que foi sobrescrito está em `~/.dotfiles-backup-<data>/`
  (mesma estrutura do `$HOME`).
- **Uma config específica**: `cd ~/dotfiles && git checkout -- .config/kwinrc`
  restaura a versão versionada; depois recarregue o componente (KWin:
  `qdbus6 org.kde.KWin /KWin reconfigure`; painel:
  `systemctl --user restart plasma-plasmashell.service`).
- **Atalhos**: `python3 ~/.local/share/kde-rice/kde-keybinds.py --dry-run`
  mostra o que seria aplicado, sem aplicar.

---

## 6. Notas de versão

| Componente | Versão usada |
|---|---|
| Plasma / KWin | 6.8.0 |
| KDE Frameworks | 6.31.0 |
| Qt | 6.12.0 |
| Ghostty | 1.3.1 |
| GTK | 4.24.1 |
| Krohnkite | `kwin-scripts-krohnkite-git` |
| Klassy | 6.7.3 (AUR) |
| Krema | 0.12.0 (AUR) |
| Panel Colorizer | AUR |

Em Plasma 6.9+ alguns nomes de atalho (`kglobalshortcutsrc`) podem mudar; nesse
caso rode `python3 ~/.local/share/kde-rice/kde-keybinds.py` para
reaplicar os atalhos com os nomes atuais.
