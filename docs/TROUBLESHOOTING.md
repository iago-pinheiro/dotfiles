# Problemas conhecidos e como resolver

Tudo aqui foi encontrado na prática montando este setup (CachyOS, Plasma 6.8,
Wayland, i915). Se algo quebrar depois de uma atualização, comece por aqui.

---

## 1. Blur do KWin quebrado (janelas pretas/artefatos)

**Sintoma:** com `blurEnabled=true`, janelas translúcidas ficam pretas, com
faixas ou listras; o `journalctl` do KWin mostra:

```
GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT
```

**Causa:** combinação de GPU Intel (i915) com Mesa recente. Não é configuração
errada — é bug de driver/efeito.

**Solução usada aqui:** desligar o blur e usar vidro com alpha mais alto
(o painel fica translúcido sem depender do blur):

```fish
kwriteconfig6 --file kwinrc --group Plugins --key blurEnabled false
qdbus6 org.KWin /KWin reconfigure
```

O `panel-colorizer.py` já aplica alpha ~0.28 na borda e fundo com alpha alto no
painel, então o visual continua "vidro" sem o efeito.

Se quiser testar de novo após atualizar o Mesa:

```fish
kwriteconfig6 --file kwinrc --group Plugins --key blurEnabled true
qdbus6 org.KWin /KWin reconfigure
journalctl --user -b -u plasma-kwin_wayland | grep -i framebuffer | tail
```

---

## 2. Acentos e teclas mortas no Ghostty (GTK 4.20+)

**Sintoma:** digitar `ção`, `ã`, `õ` no Ghostty não produz nada (ou produz a
letra sem acento), enquanto em outros apps funciona.

**Causa:** o GTK 4.20 mudou o comportamento do método de entrada; o Ghostty
(que é GTK 4) precisa do módulo `simple` para teclas mortas do X11/ABNT2.

**Solução usada aqui (só no Ghostty):**

```ini
# ~/.config/systemd/user/app-com.mitchellh.ghostty.service.d/im.conf
[Service]
Environment=GTK_IM_MODULE=simple
```

```fish
systemctl --user daemon-reload
systemctl --user restart app-com.mitchellh.ghostty.service   # fecha as janelas do Ghostty
```

> A variável é lida **na inicialização do processo**. Editar o drop-in sem
> reiniciar o serviço não muda nada no processo em execução.
> Se você abre o Ghostty fora do systemd (ex.: `ghostty --gtk-single-instance=false`),
> reinicie essa instância também.

**Se quiser para todos os apps GTK** (e não só o Ghostty), use o mecanismo da
sessão — exige logout/login:

```fish
mkdir -p ~/.config/environment.d
echo 'GTK_IM_MODULE=simple' > ~/.config/environment.d/90-im.conf
```

**Teste rápido:** abrir um Ghostty novo com a variável na mão:

```fish
env GTK_IM_MODULE=simple ghostty --gtk-single-instance=false
```

---

## 3. `SUPER+Shift+1..5` não funciona no Wayland

**Sintoma:** registrar `Meta+Shift+2` "dá certo", mas o atalho nunca dispara.

**Causa:** no KDE/Wayland o `Shift` é consumido quando a combinação gera um
símbolo. No ABNT2, `Shift+2` = `@`, então o KWin recebe `Meta+@`, não
`Meta+Shift+2` (bug conhecido do keymap, KDE #434988).

**Solução usada aqui:** registrar as combinações já resolvidas —
`Meta+!`, `Meta+@`, `Meta+#`, `Meta+$`, `Meta+%` — que no teclado são exatamente
`SUPER+Shift+1..5`. Está em `kglobalshortcutsrc` e é o que o
`kde-keybinds.py` aplica.

**Detalhes que mordem:**

- `setForeignShortcut` no kglobalaccel exige o **actionId com 4 campos**
  (`componente,ação,nome do componente,nome da ação`). Com 2 campos retorna
  sucesso e é ignorado em silêncio.
- Quando duas ações disputam a mesma tecla, vale o **menor serial** — daí a
  necessidade de desativar os atalhos numéricos do Krema (`kremarc`) para
  `SUPER+1..9` pertencer às áreas de trabalho.
- Para inspecionar o que está registrado:
  `qdbus6 org.kde.kglobalaccel /kglobalaccel org.kde.KGlobalAccel.getGlobalShortcutsByKey` (ou `kreadconfig6 --file kglobalshortcutsrc`).

---

## 4. Barra superior: borda não muda / config não aplica

**Sintoma:** editar o painel não reflete; ou a borda fica em outra cor.

**Causas e soluções:**

1. **O Panel Colorizer só relê a configuração quando o plasmashell reinicia**
   (ou quando o script `panel-colorizer.py` escreve com o shell parado). Se você
   editar `plasma-org.kde.plasma.desktop-appletsrc` com o Plasma rodando, o
   valor é sobrescrito. O fluxo correto:

   ```fish
   systemctl --user stop plasma-plasmashell.service
   # editar o appletsrc aqui
   systemctl --user start plasma-plasmashell.service
   ```

   O script já faz isso:

   ```fish
   python3 ~/.local/share/kde-rice/panel-colorizer.py
   ```

2. **Cor da borda:** vem de `focusColor` com `systemColorSet=View`
   (= `Colors:View/DecorationFocus`, a cor de destaque exata), alpha 0.28.
   **Não** use `linkColor` (devolve o azul padrão do Kirigami) nem
   `activeTextColor` (destaque escurecido 50%).

3. Para ver o que ficou gravado:

   ```fish
   kreadconfig6 --file plasma-org.kde.plasma.desktop-appletsrc \
     --group Containments --group 32 --group Applets --group 34 \
     --group Configuration --group General --key focusColor
   ```

4. Se o painel mostrar um applet com erro, o plasmoid não está instalado:
   `paru -S plasma6-applets-panel-colorizer` e reinicie o plasmashell.

---

## 5. Accent: `plasma-apply-colorscheme` não muda a cor de destaque global

`plasma-apply-colorscheme OpalFruitsDark -a '#d38539'` atualiza os grupos
`Colors:*` (inclusive `DecorationFocus`), mas **não** grava
`General/AccentColor`. Se algum app lê o accent global, ajuste na mão:

```fish
kwriteconfig6 --file kdeglobals --group General --key AccentColor 211,133,57
```

Depois regenere tema do terminal e fastfetch:

```fish
python3 ~/.local/share/kde-rice/accent-sync.py
```

---

## 6. Krema (dock): config não muda / atalhos numéricos roubando `SUPER+1..9`

- O Krema lê `~/.config/kremarc` **só ao iniciar**:

  ```fish
  systemctl --user restart com.bhyoo.krema
  ```

  (se o serviço não existir, saia e entre na sessão).

- O Krema registra atalhos numéricos por padrão; eles ganham de `SUPER+1..9`
  (menor serial). Deixe-os desativados no `kremarc` (é o que este repo faz).

---

## 7. Arquivo do applet aponta para um wallpaper que não existe

O `plasma-org.kde.plasma.desktop-appletsrc` guarda o **caminho absoluto** da
imagem (`Image=/home/<usuário>/Imagens/Wallpapers/...`). Se o usuário da máquina
nova for outro, o instalador reescreve `/home/<antigo>` → `$HOME` nos arquivos
versionados (usa o `.dotfiles-origem` gravado pelo `save.sh`).

Se ainda assim o wallpaper não aparecer:

```fish
plasma-apply-wallpaperimage ~/Imagens/Wallpapers/wallhaven-yqk2q7.jpg
```

O mesmo vale para `kscreenlockerrc` (imagem da tela de bloqueio).

---

## 8. Temas de ícones/cursores "desapareceram"

Eles não estão no repositório (tamanho). Se o KDE cair para o Breeze:

```fish
ls ~/.local/share/icons | grep -i tela         # Tela-circle-dark existe?
ls ~/.icons | grep -i winsur                   # WinSur-dark-cursors existe?

kwriteconfig6 --file kdeglobals --group Icons --key Theme Tela-circle-dark
kwriteconfig6 --file kcminputrc --group Mouse --key cursorTheme WinSur-dark-cursors
kbuildsycoca6 --noincremental
```

Instalação dos temas: veja [INSTALL.md §3.1](../INSTALL.md#31-temas-de-ícones-e-cursores).

---

## 9. Painel/tema com aparência estranha depois de mexer

Caches do Plasma guardam artefatos de applets e temas removidos:

```fish
rm -rf ~/.cache/*plasma* ~/.cache/*svg*
systemctl --user restart plasma-plasmashell.service
```

Se o problema for em uma janela específica (decoração), mude e volte o tema:

```fish
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme Klassy
qdbus6 org.kde.KWin /KWin reconfigure
```

---

## 10. Ghostty: o tema gerado não pode ser editado à mão

`~/.config/ghostty/themes/kde-accent` é **gerado** pelo `accent-sync.py` a
cada troca de wallpaper. Edite o script (ou o `accent-sync.py` chamado pelo
`wallpaper-switcher`) e rode:

```fish
python3 ~/.local/share/kde-rice/accent-sync.py
systemctl --user reload app-com.mitchellh.ghostty.service   # recarrega sem fechar
```

`restart` fecha as janelas; `reload` relê o config e aplica o tema.

---

## 11. Nada aplica de verdade? Reinicie a sessão

Muita coisa (painel, KWin, atalhos, temas de janela, `GTK_IM_MODULE`) só entra
em vigor num login novo:

```fish
# sair da sessão
qdbus6 org.kde.Shutdown /Shutdown org.kde.Shutdown.logout
```

Antes de reiniciar, confira que os arquivos estão no lugar:

```fish
cd ~/dotfiles && ./save.sh --dry-run   # nada deve estar "ausente"
```
