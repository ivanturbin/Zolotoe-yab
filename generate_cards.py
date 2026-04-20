"""
generate_cards.py — Генерация карточек товаров в стилистике goldapple.ru
с ПОЛНОЦЕННЫМИ векторными иллюстрациями товаров (вместо плейсхолдера)
и премиум-эффектами по рарностям.

По рарностям:
  Common    — чистый кремовый фон, минимум декора
  Rare      — мягкая голубая подложка, тонкая сетка точек
  Epic      — лавандовый градиент + редкие блёстки
  Legendary — золотой градиент + золотая foil-рамка + частички золота

Запуск:  python generate_cards.py
"""

from __future__ import annotations

import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.config import CARDS_JSON, ASSETS_DIR
from product_illustrations import draw_product, hex_to_rgb

FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

CARD_W, CARD_H = 600, 840

RARITY_ACCENT = {
    "Common":    "#8A8680",
    "Rare":      "#4A6FA5",
    "Epic":      "#7C4A8C",
    "Legendary": "#D4AF37",
}
RARITY_BG_A = {
    "Common":    "#F4F1EB",
    "Rare":      "#EBF0F7",
    "Epic":      "#F0E8F3",
    "Legendary": "#FBF3DC",
}
RARITY_BG_B = {
    "Common":    "#EEE9DF",
    "Rare":      "#DEE7F2",
    "Epic":      "#E4D6EC",
    "Legendary": "#F3E3AD",
}

COLOR_TEXT = "#0F0F0F"
COLOR_MUTED = "#8A8680"
COLOR_BORDER = "#E8E4DC"
GOLD = "#D4AF37"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONTS_DIR, name)
    if os.path.isfile(path):
        return ImageFont.truetype(path, size)
    for fb in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.isfile(fb):
            return ImageFont.truetype(fb, size)
    return ImageFont.load_default()


def wrap_text(draw, text, font_obj, max_w):
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = f"{current} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_obj)
        if bbox[2] - bbox[0] > max_w:
            if current:
                lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def _vertical_gradient(size, top_hex, bottom_hex):
    w, h = size
    top = hex_to_rgb(top_hex)
    bot = hex_to_rgb(bottom_hex)
    img = Image.new("RGB", size, top)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def _radial_highlight(size, center_color=(255, 255, 255, 110)):
    w, h = size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r = int(min(w, h) * 0.6)
    d.ellipse([-r // 3, -r // 3, r, r], fill=center_color)
    overlay = overlay.filter(ImageFilter.GaussianBlur(30))
    return overlay


def _draw_sparkle(d, cx, cy, size, color):
    d.polygon([
        (cx, cy - size), (cx + 1, cy - 1),
        (cx + size, cy), (cx + 1, cy + 1),
        (cx, cy + size), (cx - 1, cy + 1),
        (cx - size, cy), (cx - 1, cy - 1),
    ], fill=color)


def _pattern_dots(img, rarity):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    if rarity == "Rare":
        dot_color = (74, 111, 165, 38)
        spacing = 28
        for y in range(8, h, spacing):
            for x in range(8, w, spacing):
                d.ellipse([x, y, x + 2, y + 2], fill=dot_color)

    elif rarity == "Epic":
        random.seed(7)
        for _ in range(60):
            x = random.randint(6, w - 6)
            y = random.randint(6, h - 6)
            s = random.choice([1, 1, 1, 2])
            alpha = random.randint(40, 110)
            d.ellipse([x, y, x + s, y + s], fill=(124, 74, 140, alpha))
        for _ in range(5):
            x = random.randint(20, w - 20)
            y = random.randint(20, h - 20)
            _draw_sparkle(d, x, y, 5, (255, 215, 235, 160))

    elif rarity == "Legendary":
        random.seed(11)
        gold = hex_to_rgb(GOLD)
        for _ in range(80):
            x = random.randint(6, w - 6)
            y = random.randint(6, h - 6)
            s = random.choice([1, 1, 2, 2, 3])
            alpha = random.randint(50, 180)
            d.ellipse([x, y, x + s, y + s], fill=(*gold, alpha))
        for _ in range(8):
            x = random.randint(25, w - 25)
            y = random.randint(25, h - 25)
            size = random.randint(4, 8)
            _draw_sparkle(d, x, y, size, (255, 235, 170, 210))


def _draw_foil_border(img, rarity):
    if rarity != "Legendary":
        return
    d = ImageDraw.Draw(img, "RGBA")
    gold = hex_to_rgb(GOLD)
    d.rectangle([0, 0, CARD_W - 1, CARD_H - 1],
                outline=(*gold, 220), width=2)
    pad = 14
    d.rectangle([pad, pad, CARD_W - pad - 1, CARD_H - pad - 1],
                outline=(*gold, 110), width=1)


def generate_card(entry):
    rarity = entry["rarity"]
    name = entry["product_name"]
    category = entry.get("category", "")
    discount = entry.get("discount_value", 0)
    image_path = entry.get("image", "")
    product_id = entry["product_id"]

    accent_hex = RARITY_ACCENT[rarity]
    accent = hex_to_rgb(accent_hex)

    img = Image.new("RGB", (CARD_W, CARD_H), "white")
    img_rgba = img.convert("RGBA")

    d = ImageDraw.Draw(img_rgba, "RGBA")
    d.rectangle([48, 0, CARD_W - 48, 8], fill=accent)

    brand_font = font("Unbounded-Black.ttf", 14)
    d.text((48, 32), "ЗОЛОТОЕ ЯБЛОКО",
           fill=hex_to_rgb(COLOR_TEXT), font=brand_font, anchor="lm")
    d.ellipse([32, 30, 42, 40], fill=hex_to_rgb(GOLD))

    id_font = font("Inter-Medium.ttf", 13)
    d.text((CARD_W - 48, 36), product_id,
           fill=hex_to_rgb(COLOR_MUTED), font=id_font, anchor="rm")

    rarity_font = font("Unbounded-Bold.ttf", 15)
    d.text((CARD_W // 2, 82), rarity.upper(),
           fill=accent, font=rarity_font, anchor="mm")

    IMG_X0, IMG_Y0 = 40, 100
    IMG_X1, IMG_Y1 = CARD_W - 40, 490
    IMG_W, IMG_H = IMG_X1 - IMG_X0, IMG_Y1 - IMG_Y0

    bg = _vertical_gradient((IMG_W, IMG_H),
                            RARITY_BG_A[rarity], RARITY_BG_B[rarity])
    bg = bg.convert("RGBA")
    bg.alpha_composite(_radial_highlight((IMG_W, IMG_H)))
    _pattern_dots(bg, rarity)

    mask = Image.new("L", (IMG_W, IMG_H), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, IMG_W, IMG_H], radius=14, fill=255)
    bg.putalpha(mask)
    img_rgba.alpha_composite(bg, (IMG_X0, IMG_Y0))

    d.rounded_rectangle([IMG_X0, IMG_Y0, IMG_X1, IMG_Y1],
                        radius=14, outline=hex_to_rgb(COLOR_BORDER), width=1)

    illu_cx = (IMG_X0 + IMG_X1) // 2
    illu_cy = (IMG_Y0 + IMG_Y1) // 2 + 6
    illu_size = int(IMG_H * 0.48)
    draw_product(img_rgba, product_id, illu_cx, illu_cy, size=illu_size)

    name_font = font("Unbounded-Bold.ttf", 28)
    d2 = ImageDraw.Draw(img_rgba, "RGBA")
    name_y = 535
    lines = wrap_text(d2, name, name_font, CARD_W - 120)
    for i, line in enumerate(lines[:3]):
        d2.text((CARD_W // 2, name_y + i * 38), line,
                fill=hex_to_rgb(COLOR_TEXT), font=name_font, anchor="mm")

    cat_font = font("Inter-Regular.ttf", 14)
    cat_y = name_y + len(lines) * 38 + 14
    d2.text((CARD_W // 2, cat_y), category.lower(),
            fill=hex_to_rgb(COLOR_MUTED), font=cat_font, anchor="mm")

    line_y = CARD_H - 110
    d2.line([60, line_y, CARD_W - 60, line_y],
            fill=hex_to_rgb(COLOR_BORDER), width=1)

    if discount > 0:
        disc_font_big = font("Unbounded-Black.ttf", 44)
        disc_label_font = font("Inter-Medium.ttf", 11)
        d2.text((60, CARD_H - 66), f"−{discount}%",
                fill=accent, font=disc_font_big, anchor="lm")
        d2.text((60, CARD_H - 34), "скидка на категорию",
                fill=hex_to_rgb(COLOR_MUTED),
                font=disc_label_font, anchor="lm")

    tier_count = {"Common": 1, "Rare": 2, "Epic": 3, "Legendary": 4}[rarity]
    dot_r = 5
    dot_spacing = 18
    total_w = 3 * dot_spacing + dot_r * 2
    start_x = CARD_W - 60 - total_w + dot_r
    dot_y = CARD_H - 55
    for i in range(4):
        x = start_x + i * dot_spacing
        if i < tier_count:
            d2.ellipse([x - dot_r, dot_y - dot_r,
                        x + dot_r, dot_y + dot_r], fill=accent)
        else:
            d2.ellipse([x - dot_r, dot_y - dot_r,
                        x + dot_r, dot_y + dot_r],
                       outline=hex_to_rgb(COLOR_BORDER), width=1)

    tier_label = {"Common": "tier 1", "Rare": "tier 2",
                  "Epic": "tier 3", "Legendary": "tier 4"}[rarity]
    tier_lbl_font = font("Inter-Regular.ttf", 10)
    d2.text((CARD_W - 60, dot_y + 16), tier_label,
            fill=hex_to_rgb(COLOR_MUTED),
            font=tier_lbl_font, anchor="rm")

    d2.rectangle([0, 0, CARD_W - 1, CARD_H - 1],
                 outline=hex_to_rgb(COLOR_BORDER), width=1)
    _draw_foil_border(img_rgba, rarity)

    out_path = os.path.join(ASSETS_DIR, image_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img_rgba.convert("RGB").save(out_path, "PNG")
    print(f"  ✓ {rarity:10s} {product_id}  {name}")


def _pack_stack_mini_cards(img, cx, cy, accent_hex, count=3):
    accent = hex_to_rgb(accent_hex)
    card_w = 70
    card_h = 100
    spreads = [(-0.22, -14), (-0.04, 0), (0.2, -6)]
    for i, (angle_f, dy) in enumerate(spreads[:count]):
        single = Image.new("RGBA", (card_w + 20, card_h + 20), (0, 0, 0, 0))
        sd = ImageDraw.Draw(single)
        sd.rounded_rectangle([8, 10, card_w + 8, card_h + 10],
                             radius=8, fill=(0, 0, 0, 40))
        sd.rounded_rectangle([7, 7, card_w + 7, card_h + 7],
                             radius=8, fill=(255, 255, 255),
                             outline=(230, 226, 215), width=1)
        sd.rectangle([13, 7, card_w + 1, 10], fill=accent)
        sd.ellipse([7 + card_w // 2 - 11, 38, 7 + card_w // 2 + 11, 60],
                   outline=accent, width=2)
        sd.rectangle([20, 74, card_w - 6, 76], fill=(180, 175, 165))
        sd.rectangle([24, 82, card_w - 10, 84], fill=(200, 195, 185))
        angle = angle_f * 40
        rotated = single.rotate(angle, resample=Image.BICUBIC, expand=True)
        rw, rh = rotated.size
        img.alpha_composite(rotated, (cx - rw // 2 + i * 6 - 6,
                                      cy - rh // 2 + dy))


def generate_pack(fname, label, accent_hex,
                  bg_a_hex, bg_b_hex, tier_count,
                  legendary_decor=False):
    W, H = 420, 600
    accent = hex_to_rgb(accent_hex)

    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([40, 0, W - 40, 8], fill=accent)

    brand_font = font("Unbounded-Black.ttf", 12)
    d.text((40, 30), "ЗОЛОТОЕ ЯБЛОКО",
           fill=hex_to_rgb(COLOR_TEXT), font=brand_font, anchor="lm")
    d.ellipse([26, 28, 34, 36], fill=hex_to_rgb(GOLD))

    PAD = 40
    Y0 = 80
    Y1 = H - 170
    pack_w = W - 2 * PAD
    pack_h = Y1 - Y0
    bg = _vertical_gradient((pack_w, pack_h), bg_a_hex, bg_b_hex)
    bg = bg.convert("RGBA")
    bg.alpha_composite(_radial_highlight((pack_w, pack_h)))

    rarity_for_pattern = "Rare"
    if label.lower().startswith("epic"):
        rarity_for_pattern = "Epic"
    if legendary_decor:
        rarity_for_pattern = "Legendary"
    _pattern_dots(bg, rarity_for_pattern)

    mask = Image.new("L", (pack_w, pack_h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, pack_w, pack_h], radius=18, fill=255)
    bg.putalpha(mask)
    img.alpha_composite(bg, (PAD, Y0))

    d.rounded_rectangle([PAD, Y0, W - PAD, Y1],
                        radius=18, outline=hex_to_rgb(COLOR_BORDER), width=1)

    _pack_stack_mini_cards(img, W // 2, Y0 + pack_h // 2 - 10,
                           accent_hex, count=3)

    title_font = font("Unbounded-Black.ttf", 30)
    d2 = ImageDraw.Draw(img, "RGBA")
    d2.text((W // 2, H - 130), label.upper(),
            fill=hex_to_rgb(COLOR_TEXT), font=title_font, anchor="mm")

    sub_font = font("Inter-Medium.ttf", 12)
    sub_count = {1: "3 карты", 3: "4 карты", 4: "5 карт"}.get(tier_count, "")
    d2.text((W // 2, H - 96), f"набор · {sub_count}",
            fill=hex_to_rgb(COLOR_MUTED), font=sub_font, anchor="mm")

    dot_r = 4
    spacing = 14
    total = 3 * spacing
    sx = W // 2 - total // 2
    dot_y = H - 60
    for i in range(4):
        x = sx + i * spacing
        if i < tier_count:
            d2.ellipse([x - dot_r, dot_y - dot_r, x + dot_r, dot_y + dot_r],
                       fill=accent)
        else:
            d2.ellipse([x - dot_r, dot_y - dot_r, x + dot_r, dot_y + dot_r],
                       outline=hex_to_rgb(COLOR_BORDER), width=1)

    tier_lbl_font = font("Inter-Regular.ttf", 10)
    tlabel = {1: "tier 1 · базовый",
              3: "tier 3 · расширенный",
              4: "tier 4 · флагман"}.get(tier_count, "")
    d2.text((W // 2, H - 38), tlabel,
            fill=hex_to_rgb(COLOR_MUTED),
            font=tier_lbl_font, anchor="mm")

    d2.rectangle([0, 0, W - 1, H - 1],
                 outline=hex_to_rgb(COLOR_BORDER), width=1)

    if legendary_decor:
        gold = hex_to_rgb(GOLD)
        d2.rectangle([0, 0, W - 1, H - 1], outline=(*gold, 220), width=2)
        d2.rectangle([10, 10, W - 11, H - 11], outline=(*gold, 110), width=1)

    out_path = os.path.join(ASSETS_DIR, "packs", fname)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.convert("RGB").save(out_path, "PNG")
    print(f"  ✓ pack  {fname}")


def main():
    with open(CARDS_JSON, "r", encoding="utf-8") as fh:
        cards = json.load(fh)

    print(f"Генерация {len(cards)} карточек …\n")
    for entry in cards:
        generate_card(entry)

    print("\nГенерация обложек паков …")
    generate_pack("common_pack.png",    "Common Pack",
                  "#8A8680", "#F4F1EB", "#EEE9DF", tier_count=1)
    generate_pack("epic_pack.png",      "Epic Pack",
                  "#7C4A8C", "#F0E8F3", "#E4D6EC", tier_count=3)
    generate_pack("legendary_pack.png", "Legendary Pack",
                  "#D4AF37", "#FBF3DC", "#F3E3AD",
                  tier_count=4, legendary_decor=True)

    print("\nГотово!")


if __name__ == "__main__":
    main()
