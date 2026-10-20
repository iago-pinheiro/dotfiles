#!/usr/bin/env python3
"""Estiliza a instância do Panel Colorizer da barra superior (vidro escuro,
cantos 10, borda 1px na cor de destaque do sistema — macOS-like).

A cor da borda vem da fonte "System" do colorizer (linkColor), que é a própria
cor de destaque do Plasma: acompanha a troca de wallpaper sem reaplicar nada.

A dock inferior agora é o Krema (~/.config/kremarc), então não há mais painel
do Plasma embaixo; este script cuida só da barra de cima.

Detalhes que evitam artefatos:
- hideWidget=true  -> o widget do colorizer não desenha nem ocupa espaço
- fundo nativo do painel transparente (opacity 0), então só o vidro aparece
- sombra vem do colorizer (Kirigami.ShadowedRectangle), que respeita o raio

Depois de rodar:
    systemctl --user restart plasma-plasmashell.service

Uso:
    python3 panel-colorizer.py            # aplica
    python3 panel-colorizer.py --dry-run  # mostra o que mudaria
"""
import json
import os
import shutil
import sys

CONFIG = os.path.expanduser("~/.config/plasma-org.kde.plasma.desktop-appletsrc")

BG = "#12141A"          # vidro escuro (combina com OpalFruitsDark)


def accent_hex():
    """Cor de destaque viva do Plasma (Colors:View DecorationFocus)."""
    import subprocess
    for group, key in (("Colors:View", "DecorationFocus"),
                       ("General", "AccentColor")):
        try:
            v = subprocess.run(["kreadconfig6", "--file", "kdeglobals",
                                "--group", group, "--key", key],
                               capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            v = ""
        if v.count(",") == 2 and all(p.strip().isdigit() for p in v.split(",")):
            r, g, b = (int(p) for p in v.split(","))
            return "#%02X%02X%02X" % (r, g, b)
    return "#C97EBC"


def style(cfg, radius, alpha, border_alpha, pad, shadow_size=0, shadow_y=0, pad_v=0):
    np_ = cfg["nativePanel"]["background"]
    np_.update(enabled=True, opacity=0, shadow=True)

    p = cfg["panel"]["normal"]
    p["enabled"] = True
    p["blurBehind"] = True
    p["backgroundClipping"] = True

    bg = p["backgroundColor"]
    bg.update(enabled=True, sourceType=0, custom=BG, alpha=alpha)

    p["radius"]["enabled"] = True
    p["radius"]["corner"] = {k: radius for k in
                             ("topLeft", "topRight", "bottomLeft", "bottomRight")}

    b = p["border"]
    b["enabled"] = True
    b["width"] = 1
    b["customSides"] = False
    # cor = fonte "System" do colorizer com o papel focusColor, que no Plasma é
    # exatamente a cor de destaque (Colors:View DecorationFocus). Assim a borda
    # acompanha a cor do wallpaper ao vivo, sem reaplicar nada.
    b["color"].update(enabled=True, sourceType=1, systemColorSet="View",
                      systemColor="focusColor", custom=accent_hex(),
                      alpha=border_alpha)

    p["padding"]["enabled"] = True
    p["padding"]["side"] = {"left": pad, "right": pad, "top": pad_v, "bottom": pad_v}
    p["margin"]["enabled"] = True
    p["margin"]["side"] = {"left": 0, "right": 0, "top": 0, "bottom": 0}

    sh = p["shadow"]["background"]
    sh["enabled"] = shadow_size > 0
    sh["size"] = shadow_size
    sh["xOffset"] = 0
    sh["yOffset"] = shadow_y
    sh["color"].update(enabled=True, sourceType=0, custom="#000000", alpha=0.35)
    p["shadow"]["foreground"]["enabled"] = False

    # widgets sem fundo próprio (ícones/texto direto no vidro)
    for key in ("widgets", "trayWidgets"):
        cfg[key]["normal"]["enabled"] = False


TARGETS = {
    # (containment, applet): (radius, alpha, border_alpha, padding, sombra, yoff, pad_v)
    ("32", "34"): (10, 0.85, 0.28, 10, 6, 1, 0),   # barra superior
}


def main():
    dry = "--dry-run" in sys.argv
    path = CONFIG
    if not dry:
        shutil.copy2(path, path + ".bak-panel-colorizer")
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8")]

    targets = {f"Containments][{c}][Applets][{a}][Configuration][General": (c, a)
               for c, a in TARGETS}
    section = None
    changed = 0
    hide_done = set()

    for i, line in enumerate(lines):
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section not in targets:
            continue
        if line.startswith("hideWidget="):
            lines[i] = "hideWidget=true"
            hide_done.add(section)
        elif line.startswith("globalSettings="):
            panel, applet = section.split("][")[1], section.split("][")[3]
            params = TARGETS[(panel, applet)]
            cfg = json.loads(line.split("=", 1)[1])
            style(cfg, *params)
            new = json.dumps(cfg, separators=(",", ":"))
            json.loads(new)  # valida
            print(f"  painel {panel} / colorizer {applet}: radius={params[0]} "
                  f"alpha={params[1]} borda={params[2]}")
            lines[i] = "globalSettings=" + new
            changed += 1

    for sec in targets:
        if sec in hide_done:
            continue
        print(f"  [{sec}] hideWidget=true (adicionado)")
        idx = lines.index("[" + sec + "]")
        lines.insert(idx + 1, "hideWidget=true")

    if changed < 1:
        raise SystemExit("nenhum applet do colorizer encontrado (os painéis mudaram de id?)")
    if dry:
        print("(dry-run: nada foi escrito)")
        return
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("gravado. reinicie o plasmashell para aplicar.")


if __name__ == "__main__":
    main()
