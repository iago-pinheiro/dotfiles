#!/usr/bin/env python3
"""Aplica no KDE Plasma 6.8 os atalhos de tiling + o que já existia no Krohnkite.

Mistura: posições de tecla no estilo tiling (SUPER = Meta) para janelas/tiling/workspaces,
mantendo a essência do KDE (Overview, Grid View, Alt+Tab, Meta+L bloqueia a sessão,
Meta+Backspace restaura, Meta+D minimiza tudo, etc).

Aplica via D-Bus no kglobalaccel (que no Plasma 6.8 roda dentro do kwin_wayland).
Detalhe importante: o actionId precisa ter os 4 campos
(componente, ação, nome amigável do componente, nome amigável da ação) —
com só 2 campos a chamada retorna sucesso mas é ignorada em silêncio.

As mudanças valem na hora e o próprio kglobalaccel grava em ~/.config/kglobalshortcutsrc.

Uso:
    python3 kde-keybinds.py            # aplica
    python3 kde-keybinds.py --dry-run  # só mostra o que faria
"""
import subprocess
import sys

MODS = {"shift": 0x02000000, "ctrl": 0x04000000, "alt": 0x08000000, "meta": 0x10000000}
KEYS = {
    "left": 0x01000012, "right": 0x01000014, "up": 0x01000013, "down": 0x01000015,
    "return": 0x01000004, "enter": 0x01000005, "tab": 0x01000001, "space": 0x20,
    "escape": 0x01000000, "backspace": 0x01000003, "print": 0x01000009,
    "pgup": 0x01000016, "pgdown": 0x01000017, "home": 0x01000010, "end": 0x01000011,
    "volume up": 0x01000072, "volume down": 0x01000070, "volume mute": 0x01000071,
    ",": 0x2C, ".": 0x2E, "[": 0x5B, "]": 0x5D, "\\": 0x5C, "`": 0x60,
}
for _i in range(1, 25):
    KEYS[f"f{_i}"] = 0x01000030 + _i - 1


def encode(combo):
    """'Meta+Shift+Left' -> inteiro no formato do KGlobalAccel (modificadores | tecla Qt)."""
    value = 0
    for part in combo.split("+"):
        part = part.strip()
        low = part.lower()
        if low in MODS:
            value |= MODS[low]
        elif low in KEYS:
            value |= KEYS[low]
        elif len(part) == 1:
            value |= ord(part.upper())
        else:
            raise SystemExit(f"tecla desconhecida: {part!r} (em {combo!r})")
    return value


# (componente, ação, teclas)  -- ["none"] desvincula
TABLE = [
    # ---------- janelas: fechar, maximizar, minimizar ----------
    ("kwin", "Window Close", ["Meta+Q", "Alt+F4"]),
    ("kwin", "Window Fullscreen", ["Meta+F"]),
    ("kwin", "Window Maximize", ["Meta+Alt+F", "Meta+PgUp"]),
    ("kwin", "Window Minimize", ["Meta+M", "Meta+PgDown"]),
    # libera Meta+setas (tiling rápido nativo) para o foco do Krohnkite
    ("kwin", "Window Quick Tile Left", ["none"]),
    ("kwin", "Window Quick Tile Right", ["none"]),
    ("kwin", "Window Quick Tile Top", ["none"]),
    ("kwin", "Window Quick Tile Bottom", ["none"]),
    ("kwin", "Window to Previous Screen", ["Meta+Alt+Shift+Left"]),
    ("kwin", "Window to Next Screen", ["Meta+Alt+Shift+Right"]),
    # libera Meta+Tab (era o outro alternador de janelas) para trocar de área de trabalho
    ("kwin", "Walk Through Windows", ["Alt+Tab"]),
    ("kwin", "Walk Through Windows (Reverse)", ["Alt+Shift+Tab"]),
    ("kwin", "Switch to Next Desktop", ["Meta+Tab"]),
    ("kwin", "Switch to Previous Desktop", ["Meta+Shift+Tab"]),
    # libera Meta+T (o editor de blocos nativo brigava com o Krohnkite)
    ("kwin", "Edit Tiles", ["none"]),

    # ---------- Krohnkite: foco/swap com setas + HJKL como alternativa ----------
    ("kwin", "KrohnkiteFocusLeft", ["Meta+Left", "Meta+H"]),
    ("kwin", "KrohnkiteFocusRight", ["Meta+Right"]),  # Meta+L fica com o bloqueio de sessão
    ("kwin", "KrohnkiteFocusUp", ["Meta+Up", "Meta+K"]),
    ("kwin", "KrohnkiteFocusDown", ["Meta+Down", "Meta+J"]),
    ("kwin", "KrohnkiteShiftLeft", ["Meta+Shift+Left", "Meta+Shift+H"]),
    ("kwin", "KrohnkiteShiftRight", ["Meta+Shift+Right", "Meta+Shift+L"]),
    ("kwin", "KrohnkiteShiftUp", ["Meta+Shift+Up", "Meta+Shift+K"]),
    ("kwin", "KrohnkiteShiftDown", ["Meta+Shift+Down", "Meta+Shift+J"]),
    ("kwin", "KrohnkiteToggleFloat", ["Meta+T"]),  # tiling: SUPER+T alterna flutuante
    ("kwin", "KrohnkiteFloatAll", ["Meta+Ctrl+Shift+F"]),
    ("kwin", "KrohnkiteBTreeLayout", ["Meta+Ctrl+1"]),
    ("kwin", "KrohnkiteTileLayout", ["Meta+Ctrl+2"]),
    ("kwin", "KrohnkiteFloatingLayout", ["Meta+Ctrl+3"]),
    ("kwin", "KrohnkiteMonocleLayout", ["Meta+Ctrl+4"]),
    ("kwin", "KrohnkiteSetMaster", ["Meta+Alt+Return"]),
    ("kwin", "KrohnkiteIncrease", ["Meta+]"]),
    ("kwin", "KrohnkiteDecrease", ["Meta+["]),

    # ---------- áreas de trabalho numeradas ----------
    *[("kwin", f"Switch to Desktop {n}", [f"Meta+{n}"]) for n in range(1, 10)],
    # Shift+1..5 chega ao KDE já como o símbolo da tecla e SEM o modificador Shift
    # (o keymap "consome" o Shift; bug KDE 434988). Por isso o atalho é
    # registrado como Meta+símbolo: Meta+! = Super+Shift+1, Meta+@ = Super+Shift+2, ...
    *[("kwin", f"Window to Desktop {n}", [f"Meta+{c}"]) for n, c in
      enumerate("!@#$%", start=1)],
    # Krema registra Meta+1..9 para abrir apps; cede as teclas para as áreas de trabalho
    *[("krema", f"activate-entry-{n}", ["none"]) for n in range(1, 10)],
    *[("krema", f"new-instance-entry-{n}", ["none"]) for n in range(1, 10)],

    # ---------- essência do KDE no que sobra ----------
    ("plasmashell", "manage activities", ["none"]),  # cedeu Meta+Q para "fechar janela"
    ("plasmashell", "toggle do not disturb", ["Meta+Ctrl+,"]),  # combinação equivalente: SUPER+CTRL+,
    ("kmix", "increase_volume_small", ["Alt+Volume Up", "Shift+Volume Up"]),
    ("kmix", "decrease_volume_small", ["Alt+Volume Down", "Shift+Volume Down"]),

    # ---------- lançadores de aplicativos ----------
    ("com.mitchellh.ghostty.desktop", "_launch", ["Meta+Return"]),
    ("org.kde.krunner.desktop", "_launch", ["Meta+Space"]),
    ("org.kde.dolphin.desktop", "_launch", ["Meta+Shift+F"]),
    ("org.kde.kcalc.desktop", "_launch", ["Meta+Ctrl+Q"]),
    ("org.kde.plasma.emojier.desktop", "_launch", ["Meta+Ctrl+E"]),
    ("braveweb.desktop", "_launch", ["Meta+Shift+Return"]),
    ("org.kde.kate.desktop", "_launch", ["Meta+Shift+N"]),

    # Print fica com o Flameshot (dotfiles) e Meta+R/Meta+Shift+R com o Krohnkite
    ("org.kde.spectacle.desktop", "_launch", ["none"]),
    ("org.kde.spectacle.desktop", "RecordRegion", ["none"]),
]


def call(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def apply(component, action, combos, dry):
    keys = [] if combos == ["none"] else [encode(c) for c in combos]
    shown = "none" if not keys else ", ".join(combos)
    print(f"  {component:34s} {action:28s} -> {shown}")
    if dry:
        return
    call([
        "gdbus", "call", "--session", "--dest", "org.kde.kglobalaccel",
        "--object-path", "/kglobalaccel",
        "--method", "org.kde.KGlobalAccel.setForeignShortcut",
        f"['{component}', '{action}', '{component}', '{action}']",
        "[" + ", ".join(str(k) for k in keys) + "]",
    ])


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    print("Aplicando atalhos (janelas + Krohnkite + essência do KDE):\n")
    for component, action, combos in TABLE:
        apply(component, action, combos, dry)
    print("\n(dry-run: nada foi alterado)" if dry else "\nPronto (vale na hora).")
