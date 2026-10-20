# Atalhos — tiling no KDE Plasma (Meta = SUPER)

Aplicado por `kde-keybinds.py` (neste mesmo diretório). Rode de novo depois de
qualquer reset para reaplicar. `--dry-run` mostra sem alterar.

## Janelas

| Atalho | Ação |
|---|---|
| `SUPER+Q` / `Alt+F4` | Fechar janela |
| `SUPER+F` | Tela cheia |
| `SUPER+Alt+F` / `SUPER+PgUp` | Maximizar |
| `SUPER+M` / `SUPER+PgDown` | Minimizar |
| `SUPER+Backspace` | Restaurar janela (KDE) |
| `SUPER+D` | Minimizar tudo (KDE) |
| `SUPER+W` | Overview (KDE) |
| `SUPER+G` | Grid View (KDE) |
| `SUPER+L` | Bloquear sessão (KDE) |

## Tiling (Krohnkite)

| Atalho | Ação |
|---|---|
| `SUPER+←/→/↑/↓` | Focar janela (setas) |
| `SUPER+H/J/K` | Focar esquerda/baixo/cima (alternativo) |
| `SUPER+Shift+setas` (+`H/J/K/L`) | Mover/trocar janela |
| `SUPER+T` | Alternar flutuante |
| `SUPER+Ctrl+Shift+F` | Flutuar todas |
| `SUPER+Ctrl+1/2/3/4` | Layout BTree / Tile / Floating / Monocle |
| `SUPER+\` e `SUPER+\|` | Próximo / layout anterior |
| `SUPER+Alt+Enter` | Definir janela mestre |
| `SUPER+]` / `SUPER+[` | Aumentar / diminuir área mestre |
| `SUPER+Ctrl+H/J/K/L` | Ajustar largura/altura |
| `SUPER+R` / `SUPER+Shift+R` | Rotacionar layout / parte |
| `SUPER+.` / `SUPER+,` | Focar próxima / anterior |
| `SUPER+Ctrl+Esc` | Matar janela (KDE) |

## Áreas de trabalho

| Atalho | Ação |
|---|---|
| `SUPER+1..5` | Ir para a área de trabalho N (5 áreas) |
| `SUPER+Shift+1..5` | Mandar a janela ativa para a área de trabalho N |
| `SUPER+Tab` / `SUPER+Shift+Tab` | Próxima / anterior área de trabalho |
| `SUPER+Ctrl+setas` | Navegar entre áreas (KDE) |
| `Alt+Tab` / `Alt+Shift+Tab` | Alternar janelas (KDE) |

> **Por que `SUPER+Shift+2` é registrado como `Meta+@`:** no KDE/Wayland o Shift
> é consumido quando a combinação gera símbolo (`Shift+2` = `@` no ABNT2). O
> `kglobalshortcutsrc` mostra `Meta+!`, `Meta+@`, `Meta+#`, `Meta+$`, `Meta+%` —
> no teclado o resultado é o mesmo `SUPER+Shift+1..5`. As teclas numéricas do
> Krema foram desativadas para não roubar `SUPER+1..9`.

## Aplicativos

| Atalho | Ação |
|---|---|
| `SUPER+Enter` | Ghostty |
| `SUPER+Shift+Enter` | Brave |
| `SUPER+Shift+F` | Dolphin |
| `SUPER+Shift+N` | Kate |
| `SUPER+Space` | KRunner |
| `SUPER+Ctrl+Q` | Calculadora (KCalc) |
| `SUPER+Ctrl+E` | Emoji picker |
| `Print` | Flameshot (captura) |
| `SUPER+V` | Histórico da área de transferência (Klipper) |

## Sistema

| Atalho | Ação |
|---|---|
| `SUPER+Ctrl+,` | Alternar "Não perturbe" |
| `Alt+Volume↑/↓` | Volume em passos de 1% |
| `Shift+Volume↑/↓` | Volume em passos de 1% |
| `XF86Audio*` | Volume / mídia |
| `XF86MonBrightness*` | Brilho |

## Foco de janela

Foco segue o mouse (hover), sem atraso — em `~/.config/kwinrc`:

```ini
[Windows]
FocusPolicy=FocusFollowsMouse
DelayFocusInterval=0
```

- `DelayFocusInterval` em ms: `0` = troca na hora; `150`–`300` evita troca acidental ao passar por cima.
- `AutoRaise=false`: não levanta a janela ao passar o mouse (irrelevante no tiling, que não sobrepõe).
- O destaque visual vem do Klassy: borda accent com contraste na janela ativa, cor de sombra na inativa.

## Decisões (o que cedeu)

- `SUPER+L` continua **bloqueando a sessão** (KDE) em vez de ciclar layout — o ciclo
  ficou em `SUPER+\` / `SUPER+|`.
- `SUPER+1..0` agora **troca de área de trabalho** (antes ativava a entrada N da
  dock); o Krema ficou sem atalhos numéricos.
- `SUPER+W` continua sendo **Overview** (KDE); fechar janela é `SUPER+Q`.
- `SUPER+F` virou **tela cheia**; flutuar é `SUPER+T`.
- O editor de blocos nativo do KWin (`SUPER+T`) foi desvinculado — quem manda é o Krohnkite.

## Como reverter

```fish
# mostra o que seria mudado, sem aplicar
python3 ~/.local/share/kde-rice/kde-keybinds.py --dry-run

# restaura o estado versionado dos atalhos e do KWin e recarrega
cd ~/dotfiles && git checkout -- .config/kglobalshortcutsrc .config/kwinrc
qdbus6 org.kde.KWin /KWin reconfigure
```
