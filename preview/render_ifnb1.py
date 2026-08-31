#!/usr/bin/env python3
"""One-off preview renderer for mock/ifnb1.json. Not the product app."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "mock/ifnb1.json").read_text())
OUT = Path(__file__).with_name("ifnb1-map.png")

W, H = 2400, 1350
BG = (246, 243, 236)
INK = (27, 36, 51)
MUTED = (107, 114, 128)
LINE = (214, 207, 194)
TEAL = (14, 107, 104)
TEAL_SOFT = (196, 222, 219)
SAND = (232, 223, 208)
CORAL = (217, 106, 79)
CORAL_SOFT = (247, 226, 218)
AMBER = (184, 122, 42)
AMBER_SOFT = (241, 226, 196)
GRAY = (154, 160, 166)
WHITE = (255, 255, 255)
ROW_ALT = (241, 237, 229)

FONT_UI = "/System/Library/Fonts/SFNS.ttf"
FONT_UI_IT = "/System/Library/Fonts/SFNSItalic.ttf"
FONT_SERIF = "/System/Library/Fonts/NewYork.ttf"
FONT_MONO = "/System/Library/Fonts/SFNSMono.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def pass_status(s: dict, design: dict) -> str:
    rules = s["rules"]
    full = all(rules.values())
    gc_ok = design["gcMin"] <= s["gc"] <= design["gcMax"]
    tm_ok = s["seedTm"] <= design["seedTmMax"]
    if full and gc_ok and tm_ok:
        return "pass"
    if not full and (not gc_ok or not tm_ok):
        return "fail"
    return "warn"


def bar_color(status: str, selected: bool) -> tuple[int, int, int]:
    if selected:
        return CORAL
    return {"pass": TEAL, "warn": AMBER, "fail": GRAY}[status]


def rounded(draw: ImageDraw.ImageDraw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def text_w(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont) -> float:
    return draw.textlength(text, font=f)


def main() -> None:
    tx = DATA["transcript"]
    cds = DATA["cds"]
    design = DATA["design"]
    sirnas = DATA["sirnas"]
    length = tx["length"]
    selected_id = max(sirnas, key=lambda s: s["score"])["id"]

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_mark = font(FONT_SERIF, 36)
    f_title = font(FONT_MONO, 22)
    f_chip = font(FONT_UI, 18)
    f_small = font(FONT_UI, 16)
    f_tiny = font(FONT_UI, 14)
    f_label = font(FONT_UI, 15)
    f_mono = font(FONT_MONO, 15)
    f_mono_sm = font(FONT_MONO, 14)
    f_head = font(FONT_UI, 20)
    f_tip = font(FONT_MONO, 16)

    # --- top bar ---
    d.rectangle((0, 0, W, 78), fill=(238, 234, 225))
    d.line((0, 78, W, 78), fill=LINE, width=1)
    d.text((48, 22), "siMap", font=f_mark, fill=INK)

    chip = f"{tx['id']}  ·  {tx['symbol']}  ·  {length} nt"
    cw = text_w(d, chip, f_title)
    rounded(d, (W / 2 - cw / 2 - 22, 20, W / 2 + cw / 2 + 22, 58), 8, WHITE, LINE)
    d.text((W / 2 - cw / 2, 28), chip, font=f_title, fill=INK)

    right = "ifnb1.json"
    rw = text_w(d, right, f_chip)
    rounded(d, (W - 48 - rw - 28, 22, W - 48, 56), 8, WHITE, LINE)
    d.text((W - 48 - rw - 14, 30), right, font=f_chip, fill=MUTED)

    cand = f"{len(sirnas)} candidates"
    caw = text_w(d, cand, f_chip)
    rounded(d, (W - 48 - rw - 28 - 24 - caw - 28, 22, W - 48 - rw - 28 - 16, 56), 8, TEAL_SOFT)
    d.text((W - 48 - rw - 28 - 16 - caw - 14, 30), cand, font=f_chip, fill=TEAL)

    # --- map geometry ---
    mx0, mx1 = 80, W - 80
    mw = mx1 - mx0

    def x_of(pos: float) -> float:
        return mx0 + (pos - 1) / (length - 1) * mw

    # ruler
    ruler_y = 118
    d.line((mx0, ruler_y, mx1, ruler_y), fill=INK, width=1)
    ticks = [1, 100, 200, 300, 400, 500, 600, 700, 840]
    for t in ticks:
        x = x_of(t)
        d.line((x, ruler_y - 8, x, ruler_y + 8), fill=INK, width=1)
        label = str(t)
        d.text((x - text_w(d, label, f_tiny) / 2, ruler_y + 12), label, font=f_tiny, fill=MUTED)

    # transcript track
    track_y = 188
    track_h = 36
    d.line((mx0, track_y + track_h / 2, mx1, track_y + track_h / 2), fill=(168, 162, 150), width=2)

    utr5 = (x_of(1), track_y + 8, x_of(cds["start"] - 1), track_y + track_h - 8)
    cds_box = (x_of(cds["start"]), track_y, x_of(cds["end"]), track_y + track_h)
    utr3 = (x_of(cds["end"] + 1), track_y + 8, x_of(length), track_y + track_h - 8)
    rounded(d, utr5, 4, SAND, (176, 164, 142))
    rounded(d, cds_box, 6, TEAL)
    rounded(d, utr3, 4, SAND, (176, 164, 142))

    d.text((utr5[0] + 10, track_y + 12), "5' UTR", font=f_label, fill=INK)
    cds_label = f"CDS  {cds['start']} – {cds['end']}"
    d.text(
        ((cds_box[0] + cds_box[2]) / 2 - text_w(d, cds_label, f_head) / 2, track_y + 6),
        cds_label,
        font=f_head,
        fill=WHITE,
    )
    d.text((utr3[0] + 10, track_y + 12), "3' UTR", font=f_label, fill=INK)
    d.text((mx0, track_y - 22), "5'", font=f_tiny, fill=MUTED)
    d.text((mx1 - 12, track_y - 22), "3'", font=f_tiny, fill=MUTED)

    # siRNA track
    sirna_y = 268
    bar_h = 16
    selected = next(s for s in sirnas if s["id"] == selected_id)
    sx0, sx1 = x_of(selected["start"]), x_of(selected["end"])
    d.rectangle((sx0 - 4, 96, sx1 + 4, 980), fill=CORAL_SOFT)

    for s in sirnas:
        status = pass_status(s, design)
        color = bar_color(status, s["id"] == selected_id)
        x0, x1 = x_of(s["start"]), x_of(s["end"])
        h = bar_h + 4 if s["id"] == selected_id else bar_h
        y0 = sirna_y + (bar_h - h) / 2
        rounded(d, (x0, y0, max(x1, x0 + 8), y0 + h), 4, color)
        lid = s["id"]
        d.text((x0, sirna_y - 22), lid, font=f_tiny, fill=CORAL if s["id"] == selected_id else MUTED)

    d.text((mx0, sirna_y + 28), "siRNA", font=f_tiny, fill=MUTED)

    # tooltip
    tip = (
        f"{selected['id']}    {selected['start']}–{selected['end']}    "
        f"{design['length']}+{design['overhang']} nt    "
        f"GC {selected['gc']}%    seed Tm {selected['seedTm']}°C    "
        f"score {selected['score']:.2f}"
    )
    tw = text_w(d, tip, f_tip)
    tip_x = min(max(sx0 - 20, mx0), mx1 - tw - 36)
    tip_y = sirna_y + 52
    rounded(d, (tip_x, tip_y, tip_x + tw + 28, tip_y + 40), 8, INK)
    d.text((tip_x + 14, tip_y + 11), tip, font=f_tip, fill=WHITE)

    # rule chips
    chips = [
        design["combine"],
        f"seed Tm ≤ {design['seedTmMax']}°C",
        f"GC {design['gcMin']}–{design['gcMax']}%",
        f"no G≥{design['avoidContiguousGC']} / A≥{design['avoidContiguousAT']}",
        f"target {design['targetRange']['from']}–{design['targetRange']['to']}",
    ]
    cx, cy = mx0, 380
    for ch in chips:
        ww = text_w(d, ch, f_chip)
        rounded(d, (cx, cy, cx + ww + 28, cy + 36), 18, WHITE, LINE)
        d.text((cx + 14, cy + 8), ch, font=f_chip, fill=INK)
        cx += ww + 40

    # legend
    legend = [("pass", TEAL, "pass"), ("warn", AMBER, "partial"), ("fail", GRAY, "fail"), ("sel", CORAL, "selected")]
    lx = mx0
    for _, col, name in legend:
        d.rounded_rectangle((lx, 432, lx + 18, 446), radius=3, fill=col)
        d.text((lx + 24, 428), name, font=f_small, fill=MUTED)
        lx += 100

    # table
    cols = [
        ("id", 90, "left"),
        ("start", 80, "right"),
        ("end", 80, "right"),
        ("sense", 320, "left"),
        ("antisense", 320, "left"),
        ("GC", 80, "right"),
        ("seed Tm", 110, "right"),
        ("U", 36, "center"),
        ("R", 36, "center"),
        ("A", 36, "center"),
        ("score", 80, "right"),
        ("status", 90, "left"),
    ]
    table_x = 80
    table_w = sum(c[1] for c in cols) + 48
    row_h = 40
    header_y = 470
    rounded(d, (table_x, header_y, table_x + table_w, header_y + 44 + row_h * len(sirnas)), 10, WHITE, LINE)

    d.rectangle((table_x + 1, header_y + 1, table_x + table_w - 1, header_y + 43), fill=(238, 234, 225))
    d.text((table_x + 20, header_y - 28), "candidates", font=f_small, fill=MUTED)

    def col_xs():
        x = table_x + 24
        xs = []
        for _, w, align in cols:
            xs.append((x, x + w, align))
            x += w
        return xs

    xs = col_xs()
    headers = [c[0] for c in cols]
    for (x0, x1, align), hname in zip(xs, headers):
        ww = text_w(d, hname, f_tiny)
        if align == "right":
            txpos = x1 - ww
        elif align == "center":
            txpos = (x0 + x1) / 2 - ww / 2
        else:
            txpos = x0
        d.text((txpos, header_y + 14), hname, font=f_tiny, fill=MUTED)

    for i, s in enumerate(sirnas):
        y = header_y + 44 + i * row_h
        status = pass_status(s, design)
        sel = s["id"] == selected_id
        if sel:
            d.rectangle((table_x + 1, y, table_x + table_w - 1, y + row_h), fill=CORAL_SOFT)
        elif i % 2 == 1:
            d.rectangle((table_x + 1, y, table_x + table_w - 1, y + row_h), fill=ROW_ALT)

        mark = {"pass": "pass", "warn": "warn", "fail": "fail"}[status]
        values = [
            s["id"],
            str(s["start"]),
            str(s["end"]),
            s["sense"],
            s["antisense"],
            f"{s['gc']:.1f}",
            f"{s['seedTm']:.1f}",
            "●" if s["rules"]["Ui-Tei"] else "○",
            "●" if s["rules"]["Reynolds"] else "○",
            "●" if s["rules"]["Amarzguioui"] else "○",
            f"{s['score']:.2f}",
            mark,
        ]
        fill = CORAL if sel else INK
        for (x0, x1, align), val, (name, _, _) in zip(xs, values, cols):
            fnt = f_mono_sm if name in {"sense", "antisense", "id"} else f_small
            if name == "status":
                fill_c = {"pass": TEAL, "warn": AMBER, "fail": GRAY}[status]
            else:
                fill_c = fill
            ww = text_w(d, val, fnt)
            if align == "right":
                txpos = x1 - ww
            elif align == "center":
                txpos = (x0 + x1) / 2 - ww / 2
            else:
                txpos = x0
            d.text((txpos, y + 11), val, font=fnt, fill=fill_c)

    img.save(OUT, "PNG")
    print(OUT)


if __name__ == "__main__":
    main()
