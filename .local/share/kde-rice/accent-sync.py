#!/usr/bin/env python3
"""accent-sync — propaga a cor de destaque do Plasma para o terminal e o fastfetch.

Fonte da verdade: ~/.config/kdeglobals -> [General] AccentColor (formato "r,g,b"),
que o Plasma recalcula ao trocar o wallpaper (wallpaper-switcher) ou quando você
muda a cor de destaque em Configurações do Sistema > Cores.

O que este script faz:
  1. gera ~/.config/ghostty/themes/kde-accent (tema derivado do destaque)
  2. aponta ~/.config/ghostty/config para esse tema (theme = kde-accent)
  3. pinta os realces do fastfetch (~/.config/fastfetch/config.jsonc) com tons do destaque
  4. recarrega a config do Ghostty que já está rodando (SIGUSR2 via systemd)

A borda da barra superior não passa por aqui: ela usa a fonte "System" do Panel
Colorizer (linkColor = cor de destaque do Plasma), então acompanha sozinha.

Uso:
    accent-sync.py            # aplica
    accent-sync.py --dry-run  # mostra o que mudaria
"""
import colorsys
import os
import re
import shutil
import subprocess
import sys

KDE_GLOBALS = os.path.expanduser("~/.config/kdeglobals")
GHOSTTY_DIR = os.path.expanduser("~/.config/ghostty")
GHOSTTY_CONFIG = os.path.join(GHOSTTY_DIR, "config")
GHOSTTY_THEME = os.path.join(GHOSTTY_DIR, "themes", "kde-accent")
FASTFETCH_CONFIG = os.path.expanduser("~/.config/fastfetch/config.jsonc")
GHOSTTY_UNIT = "app-com.mitchellh.ghostty.service"

FALLBACK = "#C97EBC"     # usado se o Plasma não tiver destaque definido
THEME_NAME = "kde-accent"


# ---------------------------------------------------------------- utilidades
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(clamp(c, 0, 255))) for c in rgb)


def hls_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, clamp(l, 0, 1), clamp(s, 0, 1))
    return rgb_to_hex((r * 255, g * 255, b * 255))


def kread(group, key, default=""):
    try:
        out = subprocess.run(["kreadconfig6", "--file", "kdeglobals",
                              "--group", group, "--key", key],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or default
    except Exception:
        return default


def read_accent():
    """Retorna (h, l, s) da cor de destaque viva do Plasma."""
    raw = ""
    for group, key in (("Colors:View", "DecorationFocus"),
                       ("General", "AccentColor")):
        raw = kread(group, key)
        if re.fullmatch(r"\d+,\d+,\d+", raw) or re.fullmatch(r"#[0-9A-Fa-f]{6}", raw):
            break
    rgb = None
    if re.fullmatch(r"\d+,\d+,\d+", raw):
        rgb = tuple(int(x) for x in raw.split(","))
    elif re.fullmatch(r"#[0-9A-Fa-f]{6}", raw):
        rgb = hex_to_rgb(raw)
    if rgb is None:
        rgb = hex_to_rgb(FALLBACK)
    r, g, b = (c / 255 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # garante destaque vivo o bastante para virar tema de terminal
    return h, clamp(l, 0.45, 0.62), max(s, 0.42)


# ---------------------------------------------------------------- paleta
def palette(acc_h, acc_l, acc_s):
    """Tema completo do Ghostty ancorado no destaque do wallpaper."""

    def tint(hue, blend):
        """Puxa a hue semântica na direção da hue do destaque (caminho curto)."""
        delta = ((acc_h - hue + 0.5) % 1.0) - 0.5
        return hue + blend * delta

    accent = hls_to_hex(acc_h, acc_l, acc_s)
    bg = hls_to_hex(acc_h, 0.075, min(acc_s * 0.30, 0.18))
    fg = hls_to_hex(acc_h, 0.88, min(acc_s * 0.14, 0.11))

    p = {
        "background": bg,
        "foreground": fg,
        "cursor-color": accent,
        "cursor-text": bg,
        "selection-background": hls_to_hex(acc_h, 0.26, min(acc_s, 0.5) * 0.55),
        "selection-foreground": hls_to_hex(acc_h, 0.95, 0.08),
    }

    # ANSI 0-15: hues clássicas puxadas para o destaque (legibilidade preservada),
    # com o próprio destaque ocupando o slot "blue" (o mais usado: dirs, prompts).
    ansi = [
        hls_to_hex(acc_h, 0.16, 0.20),                          # 0 preto
        hls_to_hex(tint(0.00, 0.35), 0.58, 0.55),               # 1 vermelho
        hls_to_hex(tint(0.34, 0.35), 0.58, 0.48),               # 2 verde
        hls_to_hex(tint(0.12, 0.15), 0.62, 0.55),               # 3 amarelo
        accent,                                                 # 4 azul = destaque
        hls_to_hex(tint(0.83, 0.35), 0.62, 0.50),               # 5 magenta
        hls_to_hex(tint(0.52, 0.35), 0.58, 0.45),               # 6 ciano
        hls_to_hex(acc_h, 0.82, 0.10),                          # 7 branco
        hls_to_hex(acc_h, 0.34, 0.18),                          # 8 preto claro
        hls_to_hex(tint(0.00, 0.35), 0.70, 0.60),               # 9 vermelho claro
        hls_to_hex(tint(0.34, 0.35), 0.70, 0.52),               # 10 verde claro
        hls_to_hex(tint(0.12, 0.15), 0.74, 0.60),               # 11 amarelo claro
        hls_to_hex(acc_h, min(acc_l + 0.14, 0.78), acc_s),      # 12 azul claro
        hls_to_hex(tint(0.83, 0.35), 0.74, 0.55),               # 13 magenta claro
        hls_to_hex(tint(0.52, 0.35), 0.70, 0.50),               # 14 ciano claro
        hls_to_hex(acc_h, 0.96, 0.05),                          # 15 branco claro
    ]
    p["palette"] = ansi
    return p, accent, hls_to_hex(acc_h, min(acc_l + 0.14, 0.78), acc_s), \
        hls_to_hex(acc_h, max(acc_l - 0.12, 0.35), acc_s)


def theme_text(p, src):
    lines = [
        "# Gerado por accent-sync.py — não edite à mão.",
        f"# Tema do Ghostty derivado da cor de destaque do Plasma ({src}).",
        "# Regerar: ~/.local/share/kde-rice/accent-sync.py",
        "",
        f"background = {p['background']}",
        f"foreground = {p['foreground']}",
        f"cursor-color = {p['cursor-color']}",
        f"cursor-text = {p['cursor-text']}",
        f"selection-background = {p['selection-background']}",
        f"selection-foreground = {p['selection-foreground']}",
        "",
    ]
    lines += [f"palette = {i}={c}" for i, c in enumerate(p["palette"])]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- aplicação
def apply_ghostty_theme(p, src, dry):
    cur = open(GHOSTTY_THEME, encoding="utf-8").read() if os.path.exists(GHOSTTY_THEME) else ""
    new = theme_text(p, src)
    if cur == new:
        print(f"  ghostty: tema já atualizado ({src})")
    else:
        print(f"  ghostty: gravando temas/{THEME_NAME} ({src})")
        if not dry:
            os.makedirs(os.path.dirname(GHOSTTY_THEME), exist_ok=True)
            with open(GHOSTTY_THEME, "w", encoding="utf-8") as fh:
                fh.write(new)

    cfg = open(GHOSTTY_CONFIG, encoding="utf-8").read() if os.path.exists(GHOSTTY_CONFIG) else ""
    want = f"theme = {THEME_NAME}"
    if re.search(rf"^{re.escape(want)}$", cfg, re.M):
        return False
    if re.search(r"^theme\s*=.*$", cfg, re.M):
        cfg = re.sub(r"^theme\s*=.*$", want, cfg, count=1, flags=re.M)
    else:
        cfg = want + "\n" + cfg
    print(f"  ghostty: config -> {want}")
    if not dry:
        shutil.copy2(GHOSTTY_CONFIG, GHOSTTY_CONFIG + ".bak-accent-sync")
        with open(GHOSTTY_CONFIG, "w", encoding="utf-8") as fh:
            fh.write(cfg)
    return True


def apply_fastfetch(accent, light, dark, dry):
    """Repinta os realces do fastfetch com tons do destaque.

    Os módulos usam três cores de grupo (hoje "green"/"blue"/"magenta"); cada
    cor distinta encontrada em keyColor/color vira um tom do destaque, na ordem
    em que aparece no arquivo.
    """
    if not os.path.exists(FASTFETCH_CONFIG):
        print("  fastfetch: config não encontrada, pulando")
        return
    tones = [accent, light, dark]
    txt = open(FASTFETCH_CONFIG, encoding="utf-8").read()
    mapping = {}
    changed = 0

    def repl(m):
        nonlocal changed
        key, value = m.group(1), m.group(2)
        if value not in mapping:
            mapping[value] = tones[min(len(mapping), len(tones) - 1)]
        if mapping[value] != value:
            changed += 1
        return f'{key}"{mapping[value]}"'

    new = re.sub(r'("(?:keyColor|color)"\s*:\s*)"([^"]+)"', repl, txt)
    if not changed:
        print("  fastfetch: já sincronizado")
        return
    print(f"  fastfetch: realces -> {accent} / {light} / {dark} ({changed} campos)")
    if not dry:
        shutil.copy2(FASTFETCH_CONFIG, FASTFETCH_CONFIG + ".bak-accent-sync")
        with open(FASTFETCH_CONFIG, "w", encoding="utf-8") as fh:
            fh.write(new)


def reload_ghostty(dry):
    if dry:
        print("  ghostty: (dry-run) recarregaria a config")
        return
    ok = subprocess.run(["systemctl", "--user", "reload", GHOSTTY_UNIT],
                        capture_output=True, text=True)
    if ok.returncode == 0:
        print("  ghostty: config recarregada (SIGUSR2)")
        return
    pid = subprocess.run(["pgrep", "-x", "ghostty"], capture_output=True,
                         text=True).stdout.split()
    if pid:
        subprocess.run(["kill", "-USR2", *pid])
        print("  ghostty: config recarregada (SIGUSR2 no processo)")
    else:
        print("  ghostty: não está rodando (a config será lida no próximo start)")


def main():
    dry = "--dry-run" in sys.argv
    acc_h, acc_l, acc_s = read_accent()
    p, accent, light, dark = palette(acc_h, acc_l, acc_s)
    src = "#%02X%02X%02X" % tuple(
        int(round(c * 255)) for c in colorsys.hls_to_rgb(acc_h, acc_l, acc_s))
    print(f"accent-sync: destaque do Plasma = {src}")
    changed = apply_ghostty_theme(p, src, dry)
    apply_fastfetch(accent, light, dark, dry)
    if changed:
        reload_ghostty(dry)
    if dry:
        print("(dry-run: nada foi escrito)")


if __name__ == "__main__":
    main()
