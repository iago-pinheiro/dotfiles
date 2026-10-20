# Cor de destaque, terminal e fastfetch — 20/10/2026

Tudo aqui é derivado da **cor de destaque do Plasma**, que o `wallpaper-switcher`
recalcula a cada troca de wallpaper (`General/AccentColor` +
`Colors:*/DecorationFocus` no `~/.config/kdeglobals`).

## 1. Borda da barra superior (segue o destaque, ao vivo)

A borda de 1 px da barra usa a fonte **System** do Panel Colorizer com o papel
`focusColor` (com `systemColorSet=View`). No Plasma esse papel é exatamente o
`Colors:View DecorationFocus`, ou seja, a cor de destaque.

| | valor |
|---|---|
| fonte | System (`focusColor` / `View`) |
| alpha | 0.28 (mantido, é o que dá o efeito sutil) |

Trocar wallpaper (ou a cor de destaque em Configurações do Sistema) **repinta a
borda sem reiniciar nada** — verificado trocando o destaque para verde e lendo o
pixel da borda (`#22CC88` na hora).

`~/.local/share/kde-rice/panel-colorizer.py` aplica essa config
(`python3 panel-colorizer.py` + `systemctl --user restart plasma-plasmashell.service`;
só esse restart é necessário, uma vez).

Papéis testados e descartados: `linkColor` devolve o azul padrão do Kirigami e
`activeTextColor` devolve o destaque escurecido (50% preto) — `focusColor` é o
único que entrega a cor exata.

## 2. Terminal (Ghostty) + fastfetch

```bash
python3 ~/.local/share/kde-rice/accent-sync.py            # aplica
python3 ~/.local/share/kde-rice/accent-sync.py --dry-run  # só mostra
```

O `wallpaper-switcher` chama isso sozinho no fim (passo 6).

O que o script faz:

1. gera `~/.config/ghostty/themes/kde-accent` — tema do Ghostty derivado do
   destaque: fundo/foreground levemente tingidos, cursor e seleção no destaque,
   paleta ANSI com as hues clássicas puxadas 35% na direção do destaque e o
   próprio destaque no slot `blue` (dirs/prompt);
2. aponta `~/.config/ghostty/config` para esse tema (`theme = kde-accent`);
3. repinta os realces do `~/.config/fastfetch/config.jsonc` com três tons do
   destaque (grupos Hardware / Software / System Info, na ordem em que aparecem);
4. recarrega a config do Ghostty em execução (SIGUSR2 via `systemctl --user
   reload app-com.mitchellh.ghostty.service`) — janelas abertas pegam o tema novo.

Backups: `config.bak-accent-sync` (ghostty) e `config.jsonc.bak-accent-sync`
(fastfetch). Reverter = restaurar os backups e apagar
`~/.config/ghostty/themes/kde-accent`.

## 3. Acentos (teclas mortas) no Ghostty

Sintoma: `´ + a` não virava `á`. Causa: o GTK 4.20+ parou de compor teclas mortas
por conta própria e passou a depender do IME do compositor; sem ibus/fcitx
rodando, a composição simplesmente não acontece (upstream:
`ghostty-org/ghostty` discussion #8899 e #9112).

Correção: forçar o contexto simples do GTK só no Ghostty, via drop-in do serviço:

```
~/.config/systemd/user/app-com.mitchellh.ghostty.service.d/im.conf
[Service]
Environment=GTK_IM_MODULE=simple
```

```bash
systemctl --user daemon-reload
systemctl --user restart app-com.mitchellh.ghostty.service   # fecha as janelas do Ghostty
```

Ponto importante: `GTK_IM_MODULE` é lido **na inicialização** do processo, então o
efeito só aparece depois desse restart (ou de um novo login). Alternativa global
(afeta todos os apps GTK): `~/.config/environment.d/10-im.conf` com
`GTK_IM_MODULE=simple` — só vale após relogar.
