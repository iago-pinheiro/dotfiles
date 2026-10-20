# Painéis (barra superior + dock) — 20/10/2026

A barra de cima continua sendo um painel do Plasma estilizado pelo **Panel
Colorizer**; a dock de baixo agora é o **Krema** (app separado). O painel do
Plasma que fazia a dock foi removido.

## Barra superior (painel 32 + applet 34 do colorizer)

| | valor |
|---|---|
| posição | topo, flutuante, `fill` |
| fundo | `#12141A` a 85% + blur |
| cantos | 10 px |
| borda | 1 px na cor de destaque do sistema (fonte System/`focusColor`) a 28% |
| padding lateral | 10 px |
| sombra | 6 px, deslocada 1 px |

Fundo nativo do painel transparente (`nativePanel.background.opacity=0`) e
`hideWidget=true` no colorizer: só o vidro aparece, sem bloco quadrado.

```bash
python3 ~/.local/share/kde-rice/panel-colorizer.py            # aplica
python3 ~/.local/share/kde-rice/panel-colorizer.py --dry-run  # só mostra
systemctl --user restart plasma-plasmashell.service              # recarrega
```

Valores em `TARGETS` (raio, alpha, borda, padding, sombra); cor do vidro em `BG`.
A borda não tem cor fixa: vem do destaque do Plasma e acompanha o wallpaper ao
vivo (detalhes em `TEMA.md`).
Backup: `~/.config/plasma-org.kde.plasma.desktop-appletsrc.bak-panel-colorizer`.

## Dock inferior (Krema)

- Pacote: `krema` (AUR, v0.12.0, compilado do release oficial).
- Config: `~/.config/kremarc` (todas as chaves em `src/config/krema.kcfg` do repo).
- Ajustes na mão: editar o `kremarc` e reiniciar (`pkill -x krema; krema &`).
- Ajustes pela interface: botão direito na dock → configurações.
- Autostart: `/etc/xdg/autostart/com.bhyoo.krema.autostart.desktop`.
- Atalhos: `Meta+\`` mostra/esconde; `Meta+1..9` abre/ativa o n-ésimo app.

| chave | valor | efeito |
|---|---|---|
| `IconSize` | 56 | tamanho do ícone |
| `IconSpacing` | 8 | espaço entre ícones |
| `MaxZoomFactor` | 1.7 | zoom parabólico no hover |
| `ZoomAnimationPreset` | 0 | "Natural" (estilo macOS) |
| `CornerRadius` | 24 | pílula |
| `Floating` / `FloatingMargin` | true / 10 | flutua 10 px da borda |
| `BackgroundStyle` | 3 | Acrylic (vidro + ruído) |
| `BackgroundOpacity` | 0.78 | transparência do vidro |
| `ShadowEnabled` / `ShadowIntensity` | true / 0.45 | sombra |
| `VisibilityMode` | 0 | 0=sempre visível, 1=auto-hide, 2=esconde com janela |
| `ReserveScreenSpace` | true | janelas maximizadas não cobrem a dock |
| `PinnedLaunchers` | Brave, Dolphin, Ghostty | apps fixos |

Os pontinhos embaixo dos ícones são o indicador de app aberto (nativo do Krema).
Pré-visualização de janelas no hover vem do PipeWire.

### Alternativas avaliadas

- **Latte Dock**: morto, não roda no Plasma 6.
- **Plank**: só X11.
- **Crystal Dock** (`crystal-dock-bin` quebrado no Arch; `crystal-dock-git`
  compila mas foi reprovado no visual). Continua instalado, sem autostart.
- **Dock do Plasma** (painel + Icons-only Task Manager): o frame do tema
  preenche o item inteiro, então o "app aberto" sempre vira uma placa grande;
  não dá para fazer bolinha/pílula sem hack no SVG do tema.

## Histórico / reversão

- O painel da dock (id 2) foi apagado. Backup do appletsrc:
  `~/.config/plasma-org.kde.plasma.desktop-appletsrc.bak-antes-krema`.
- O override de `widgets/tasks.svg` em
  `~/.local/share/plasma/desktoptheme/klassy-dark/` foi removido (não há mais
  gerenciador de tarefas no Plasma) — o tema voltou a ser o do sistema.

## Observações

- O blur do KWin registra `GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT` nesta máquina
  (i915/Mesa 26). O vidro usa alpha alto para continuar legível mesmo assim.
- Se abrir as configurações do Panel Colorizer e clicar em *Aplicar*, o widget
  sobrescreve o JSON — rode o script de novo depois.
