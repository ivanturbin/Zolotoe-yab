"""
product_illustrations.py — Векторные иллюстрации товаров в PIL.

Рисуем аккуратные, минималистичные иллюстрации типов косметики
(бутылочки, тюбики, палетки, парфюмы и т.д.) в эстетике goldapple.ru.

Каждая функция принимает:
  img   — PIL.Image (RGB/RGBA), на котором рисуется
  cx,cy — центр области рисования
  size  — «крупность» иллюстрации (примерно ширина в пикселях)
  color — основной цвет товара (hex), необязательный

И рисует товар с тонкой обводкой и приглушённой тенью.
"""

from __future__ import annotations

from typing import Tuple
from PIL import Image, ImageDraw, ImageFilter


# ─── Вспомогательные ─────────────────────────────────────────────────────────

def hex_to_rgb(hx: str) -> Tuple[int, int, int]:
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def lighten(color: Tuple[int, int, int], amt: float = 0.15) -> Tuple[int, int, int]:
    return tuple(min(255, int(c + (255 - c) * amt)) for c in color)


def darken(color: Tuple[int, int, int], amt: float = 0.15) -> Tuple[int, int, int]:
    return tuple(max(0, int(c * (1 - amt))) for c in color)


STROKE = (32, 32, 32)
STROKE_LIGHT = (80, 80, 80)
CAP_DARK = (38, 38, 38)
GOLD = hex_to_rgb("#D4AF37")
GOLD_LIGHT = hex_to_rgb("#E8C547")
GOLD_DARK = hex_to_rgb("#A8871C")
CREAM = hex_to_rgb("#F5EEDC")
SILVER = hex_to_rgb("#C8C8CE")


def _soft_shadow(img: Image.Image, bbox, color=(0, 0, 0, 55), blur: int = 8) -> None:
    """Накладывает мягкую тень под товар (эллипс внизу)."""
    x0, y0, x1, y1 = bbox
    w = x1 - x0
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sy = y1 + int(w * 0.05)
    sd.ellipse(
        [x0 + int(w * 0.1), sy - int(w * 0.06),
         x1 - int(w * 0.1), sy + int(w * 0.08)],
        fill=color,
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(shadow)


def _rounded(draw: ImageDraw.Draw, box, radius: int, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


# ─── Базовые товары ──────────────────────────────────────────────────────────

def draw_bottle_tall(img, cx, cy, size, color_hex="#B8D8E8", cap_hex=None):
    """Высокая узкая бутылочка (тоник, мицелярка)."""
    color = hex_to_rgb(color_hex)
    cap = hex_to_rgb(cap_hex) if cap_hex else CAP_DARK
    w = int(size * 0.55)
    h = int(size * 1.5)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка
    cap_h = int(h * 0.14)
    cap_w = int(w * 0.5)
    _rounded(d, [cx - cap_w // 2, y0, cx + cap_w // 2, y0 + cap_h],
             radius=4, fill=cap, outline=STROKE, width=2)
    # горлышко
    neck_h = int(h * 0.05)
    d.rectangle([cx - cap_w // 2 + 2, y0 + cap_h - 1,
                 cx + cap_w // 2 - 2, y0 + cap_h + neck_h],
                fill=cap)
    # тело бутылки
    body_top = y0 + cap_h + neck_h
    _rounded(d, [x0, body_top, x1, y1],
             radius=10, fill=color, outline=STROKE, width=2)
    # блик
    _rounded(d, [x0 + int(w * 0.12), body_top + int(h * 0.08),
                 x0 + int(w * 0.26), y1 - int(h * 0.15)],
             radius=6, fill=lighten(color, 0.55))
    # этикетка
    lbl_y0 = body_top + int(h * 0.45)
    lbl_y1 = body_top + int(h * 0.72)
    _rounded(d, [x0 + 4, lbl_y0, x1 - 4, lbl_y1],
             radius=4, fill=(255, 255, 255), outline=STROKE_LIGHT, width=1)
    d.rectangle([x0 + 10, lbl_y0 + 7,
                 x1 - 10, lbl_y0 + 10], fill=STROKE)
    d.rectangle([x0 + 10, lbl_y0 + 15,
                 x0 + int(w * 0.55), lbl_y0 + 17], fill=STROKE_LIGHT)


def draw_bottle_big(img, cx, cy, size, color_hex="#F5EEDC", cap_hex="#E8C547"):
    """Большая бутылка шампуня/кондиционера с помпой-крышкой."""
    color = hex_to_rgb(color_hex)
    cap = hex_to_rgb(cap_hex)
    w = int(size * 0.7)
    h = int(size * 1.45)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка-flip-top
    cap_h = int(h * 0.12)
    _rounded(d, [x0 + int(w * 0.2), y0, x1 - int(w * 0.2), y0 + cap_h],
             radius=6, fill=cap, outline=STROKE, width=2)
    # плечи (сужение сверху)
    sh_h = int(h * 0.12)
    d.polygon([
        (x0, y0 + cap_h + sh_h),
        (x0 + int(w * 0.2), y0 + cap_h),
        (x1 - int(w * 0.2), y0 + cap_h),
        (x1, y0 + cap_h + sh_h),
    ], fill=color, outline=STROKE)
    # тело
    body_top = y0 + cap_h + sh_h - 1
    _rounded(d, [x0, body_top, x1, y1],
             radius=14, fill=color, outline=STROKE, width=2)
    # замаскируем верх скругления (оно перекрывает плечи)
    d.rectangle([x0 + 1, body_top, x1 - 1, body_top + 3], fill=color)
    # блик
    _rounded(d, [x0 + int(w * 0.12), body_top + int(h * 0.06),
                 x0 + int(w * 0.24), y1 - int(h * 0.25)],
             radius=8, fill=lighten(color, 0.45))
    # этикетка
    lbl_y0 = body_top + int(h * 0.35)
    lbl_y1 = body_top + int(h * 0.68)
    _rounded(d, [x0 + 6, lbl_y0, x1 - 6, lbl_y1],
             radius=6, fill=(255, 255, 255), outline=STROKE_LIGHT, width=1)
    d.rectangle([x0 + 16, lbl_y0 + 9, x1 - 16, lbl_y0 + 13], fill=STROKE)
    d.rectangle([x0 + 16, lbl_y0 + 19, x1 - 32, lbl_y0 + 22],
                fill=STROKE_LIGHT)
    d.rectangle([x0 + 16, lbl_y0 + 27, x1 - 40, lbl_y0 + 29],
                fill=STROKE_LIGHT)


def draw_tube(img, cx, cy, size, color_hex="#F5EEDC", cap_hex=None,
              accent_hex=None):
    """Горизонтально-лежащий тюбик (крем, пилинг, пена)."""
    color = hex_to_rgb(color_hex)
    cap = hex_to_rgb(cap_hex) if cap_hex else CAP_DARK
    accent = hex_to_rgb(accent_hex) if accent_hex else None
    w = int(size * 1.55)
    h = int(size * 0.55)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка (слева, круглая)
    cap_w = int(w * 0.14)
    _rounded(d, [x0, y0, x0 + cap_w, y1],
             radius=6, fill=cap, outline=STROKE, width=2)
    # тело
    body_x0 = x0 + cap_w - 2
    _rounded(d, [body_x0, y0, x1, y1],
             radius=8, fill=color, outline=STROKE, width=2)
    # «запаянный» конец справа — ступенькой вниз
    d.polygon([
        (x1 - 6, y0 + 4),
        (x1, y0 + 8),
        (x1, y1 - 8),
        (x1 - 6, y1 - 4),
    ], fill=darken(color, 0.08), outline=STROKE)
    # шов на конце
    d.line([x1, y0 + 8, x1, y1 - 8], fill=STROKE, width=1)
    # блик
    _rounded(d, [body_x0 + int(w * 0.1), y0 + 6,
                 body_x0 + int(w * 0.18), y1 - 6],
             radius=4, fill=lighten(color, 0.5))
    # этикетка/название
    if accent:
        d.rectangle([body_x0 + int(w * 0.22), y0 + 10,
                     body_x0 + int(w * 0.34), y0 + 14], fill=accent)
    d.rectangle([body_x0 + int(w * 0.22), cy - 2,
                 x1 - 12, cy + 1], fill=STROKE)
    d.rectangle([body_x0 + int(w * 0.22), cy + 6,
                 x1 - 24, cy + 8], fill=STROKE_LIGHT)


def draw_tube_vertical(img, cx, cy, size, color_hex="#F5EEDC",
                       cap_hex=None, accent_hex=None):
    """Вертикальный тюбик (BB-крем, праймер и т.д.)."""
    color = hex_to_rgb(color_hex)
    cap = hex_to_rgb(cap_hex) if cap_hex else CAP_DARK
    accent = hex_to_rgb(accent_hex) if accent_hex else GOLD
    w = int(size * 0.5)
    h = int(size * 1.5)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка
    cap_h = int(h * 0.12)
    _rounded(d, [x0, y0, x1, y0 + cap_h],
             radius=4, fill=cap, outline=STROKE, width=2)
    # шов на крышке
    d.line([x0 + 3, y0 + cap_h // 2, x1 - 3, y0 + cap_h // 2],
           fill=STROKE_LIGHT, width=1)
    # тело
    body_top = y0 + cap_h - 2
    _rounded(d, [x0, body_top, x1, y1],
             radius=6, fill=color, outline=STROKE, width=2)
    # нижняя кромка «запаяно» (узкая линия)
    d.line([x0 + 3, y1, x1 - 3, y1], fill=STROKE, width=1)
    # блик
    _rounded(d, [x0 + 4, body_top + 8, x0 + int(w * 0.26), y1 - 16],
             radius=3, fill=lighten(color, 0.5))
    # этикетка
    lbl_y = body_top + int(h * 0.4)
    d.rectangle([x0 + 6, lbl_y, x1 - 6, lbl_y + 2], fill=accent)
    d.rectangle([x0 + 6, lbl_y + 10, x1 - 6, lbl_y + 13], fill=STROKE)
    d.rectangle([x0 + 6, lbl_y + 19, x1 - 14, lbl_y + 21], fill=STROKE_LIGHT)


def draw_jar(img, cx, cy, size, color_hex="#F5EEDC", lid_hex=None):
    """Круглая баночка (скраб, маска, крем)."""
    color = hex_to_rgb(color_hex)
    lid = hex_to_rgb(lid_hex) if lid_hex else CAP_DARK
    w = int(size * 1.0)
    h = int(size * 0.85)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка сверху (эллипс сплющенный)
    lid_h = int(h * 0.35)
    d.rectangle([x0, y0 + lid_h // 2, x1, y0 + lid_h - 2],
                fill=lid)
    d.ellipse([x0, y0, x1, y0 + lid_h],
              fill=lid, outline=STROKE, width=2)
    d.ellipse([x0, y0 + lid_h - 8, x1, y0 + lid_h],
              fill=lighten(lid, 0.2), outline=STROKE, width=1)
    # тело
    body_top = y0 + lid_h - 4
    _rounded(d, [x0, body_top, x1, y1],
             radius=10, fill=color, outline=STROKE, width=2)
    # маскируем верх скругления под крышку
    d.rectangle([x0 + 2, body_top, x1 - 2, body_top + 3], fill=color)
    # блик
    _rounded(d, [x0 + int(w * 0.15), body_top + 8,
                 x0 + int(w * 0.28), y1 - 16],
             radius=6, fill=lighten(color, 0.5))
    # название
    d.rectangle([x0 + int(w * 0.25), cy + 4,
                 x1 - int(w * 0.25), cy + 7], fill=STROKE)
    d.rectangle([x0 + int(w * 0.3), cy + 13,
                 x1 - int(w * 0.3), cy + 15], fill=STROKE_LIGHT)


def draw_compact(img, cx, cy, size, color_hex="#E0B896",
                 case_hex="#2E2E2E"):
    """Круглая компактная упаковка (пудра, румяна, хайлайтер)."""
    case = hex_to_rgb(case_hex)
    color = hex_to_rgb(color_hex)
    r = int(size * 0.6)

    _soft_shadow(img, (cx - r, cy - r, cx + r, cy + r))
    d = ImageDraw.Draw(img)
    # корпус
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=case, outline=STROKE, width=2)
    # внутреннее зеркало/пудра (смещаем вверх, будто приоткрыта)
    inner = r - 8
    d.ellipse([cx - inner, cy - inner + 2, cx + inner, cy + inner + 2],
              fill=color, outline=darken(color, 0.2), width=1)
    # блик
    d.ellipse([cx - inner + 8, cy - inner + 8,
               cx - inner + 30, cy - inner + 22],
              fill=lighten(color, 0.35))
    # логотип — маленькая точка в центре верха
    d.ellipse([cx - 3, cy - r + 8, cx + 3, cy - r + 14], fill=GOLD)


def draw_palette(img, cx, cy, size, tones=None, case_hex="#2E2E2E"):
    """Прямоугольная палетка теней (4 цвета по умолчанию)."""
    case = hex_to_rgb(case_hex)
    if tones is None:
        tones = ["#E8D3B8", "#C9A37B", "#9C6E48", "#4F2E1D"]
    w = int(size * 1.4)
    h = int(size * 0.85)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # корпус
    _rounded(d, [x0, y0, x1, y1],
             radius=8, fill=case, outline=STROKE, width=2)
    # зеркало (верхняя половина, приглушённый оттенок)
    mirror_h = int(h * 0.38)
    _rounded(d, [x0 + 8, y0 + 8, x1 - 8, y0 + mirror_h],
             radius=4, fill=(238, 238, 240), outline=STROKE_LIGHT, width=1)
    # рефлекс
    d.polygon([(x0 + 14, y0 + 14),
               (x0 + 40, y0 + 14),
               (x0 + 30, y0 + mirror_h - 6)],
              fill=(255, 255, 255))
    # ряд теней (тонов = 4)
    pan_y0 = y0 + mirror_h + 8
    pan_y1 = y1 - 8
    pan_w = (x1 - x0 - 16 - 3 * (len(tones) - 1)) // len(tones)
    for i, tone in enumerate(tones):
        px0 = x0 + 8 + i * (pan_w + 3)
        _rounded(d, [px0, pan_y0, px0 + pan_w, pan_y1],
                 radius=4, fill=hex_to_rgb(tone),
                 outline=darken(hex_to_rgb(tone), 0.2), width=1)
        # блик
        d.rectangle([px0 + 3, pan_y0 + 3,
                     px0 + 9, pan_y0 + 8],
                    fill=lighten(hex_to_rgb(tone), 0.4))


def draw_lipstick(img, cx, cy, size, color_hex="#B83246", case_hex="#1A1A1A"):
    """Открытая помада (губная)."""
    color = hex_to_rgb(color_hex)
    case = hex_to_rgb(case_hex)
    w = int(size * 0.45)
    h = int(size * 1.5)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # футляр нижний
    case_top = y0 + int(h * 0.55)
    _rounded(d, [x0, case_top, x1, y1],
             radius=3, fill=case, outline=STROKE, width=2)
    # декоративная полоска
    d.rectangle([x0 + 2, case_top + int(h * 0.14),
                 x1 - 2, case_top + int(h * 0.17)], fill=GOLD)
    # внутренний держатель (чуть светлее корпуса)
    hold_h = int(h * 0.1)
    d.rectangle([x0 + 2, case_top - hold_h, x1 - 2, case_top + 1],
                fill=lighten(case, 0.25), outline=STROKE, width=1)
    # сам стержень помады (скошенный срез)
    st_top = y0
    st_bot = case_top - hold_h
    d.polygon([
        (x0 + 2, st_bot),
        (x1 - 2, st_bot),
        (x1 - 2, st_top + int(h * 0.1)),
        (cx, st_top),
        (x0 + 2, st_top + int(h * 0.2)),
    ], fill=color, outline=STROKE)
    # блик на стержне
    d.polygon([
        (x0 + 6, st_top + int(h * 0.3)),
        (x0 + 10, st_bot - 3),
        (x0 + 7, st_bot - 3),
    ], fill=lighten(color, 0.35))


def draw_lipstick_set(img, cx, cy, size, colors=None):
    """Набор помад в ряд (для epic)."""
    if colors is None:
        colors = ["#C43E57", "#A02B44", "#E89B81", "#7E3F5C"]
    gap = int(size * 0.08)
    w_each = int(size * 0.36)
    total_w = len(colors) * w_each + (len(colors) - 1) * gap
    start_x = cx - total_w // 2
    for i, c in enumerate(colors):
        ex = start_x + i * (w_each + gap) + w_each // 2
        draw_lipstick(img, ex, cy, int(size * 0.8), color_hex=c)


def draw_mascara(img, cx, cy, size, color_hex="#111111"):
    """Тушь для ресниц: стоит вертикально, конус + щёточка вверху."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.45)
    h = int(size * 1.5)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # колпачок с щёточкой торчащей наружу не рисуем — тушь закрыта
    cap_h = int(h * 0.32)
    _rounded(d, [x0, y0, x1, y0 + cap_h],
             radius=4, fill=color, outline=STROKE, width=2)
    # тонкая декоративная полоска
    d.rectangle([x0 + 1, y0 + cap_h - 8, x1 - 1, y0 + cap_h - 5], fill=GOLD)
    # тело-флакон (цилиндр, расширяющийся книзу)
    body_top = y0 + cap_h - 1
    w_bot = int(w * 1.2)
    d.polygon([
        (x0, body_top),
        (x1, body_top),
        (cx + w_bot // 2, y1),
        (cx - w_bot // 2, y1),
    ], fill=color, outline=STROKE)
    # этикетка-название
    lbl_y = body_top + int(h * 0.2)
    d.rectangle([cx - int(w * 0.35), lbl_y,
                 cx + int(w * 0.35), lbl_y + 3],
                fill=GOLD)
    d.rectangle([cx - int(w * 0.4), lbl_y + 10,
                 cx + int(w * 0.4), lbl_y + 12],
                fill=lighten(color, 0.4))


def draw_eyeliner(img, cx, cy, size, color_hex="#111111"):
    """Подводка: тонкий длинный фломастер, лежит горизонтально."""
    color = hex_to_rgb(color_hex)
    w = int(size * 1.7)
    h = int(size * 0.22)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1), color=(0, 0, 0, 40), blur=5)
    d = ImageDraw.Draw(img)
    # корпус
    _rounded(d, [x0, y0, x1 - int(w * 0.15), y1],
             radius=h // 2, fill=color, outline=STROKE, width=2)
    # конус к кончику
    tip_x0 = x1 - int(w * 0.18)
    d.polygon([
        (tip_x0, y0),
        (x1 - 4, cy - 1),
        (x1, cy),
        (x1 - 4, cy + 1),
        (tip_x0, y1),
    ], fill=color, outline=STROKE)
    # золотая полоска
    d.rectangle([x0 + int(w * 0.35), y0 + 2,
                 x0 + int(w * 0.38), y1 - 2], fill=GOLD)
    # блик
    _rounded(d, [x0 + 6, y0 + 3,
                 x0 + int(w * 0.3), y0 + 6],
             radius=2, fill=lighten(color, 0.35))


def draw_pencil(img, cx, cy, size, color_hex="#8B5A3C", wood_hex="#E8C89F"):
    """Карандаш (брови, глаза) — с деревянным заточенным кончиком."""
    color = hex_to_rgb(color_hex)
    wood = hex_to_rgb(wood_hex)
    w = int(size * 1.6)
    h = int(size * 0.24)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1), color=(0, 0, 0, 40), blur=5)
    d = ImageDraw.Draw(img)
    # корпус (левый — основной)
    body_x1 = x0 + int(w * 0.7)
    _rounded(d, [x0, y0, body_x1, y1],
             radius=4, fill=color, outline=STROKE, width=2)
    # ободок
    d.rectangle([body_x1 - 6, y0, body_x1 - 2, y1],
                fill=GOLD)
    # заточенный деревянный участок
    tip_x1 = x1 - int(w * 0.08)
    d.polygon([
        (body_x1, y0),
        (tip_x1, cy - 2),
        (tip_x1, cy + 2),
        (body_x1, y1),
    ], fill=wood, outline=STROKE)
    # графит (кончик)
    d.polygon([
        (tip_x1, cy - 2),
        (x1, cy),
        (tip_x1, cy + 2),
    ], fill=darken(color, 0.3), outline=STROKE)


def draw_nail_polish(img, cx, cy, size, color_hex="#C83A5A"):
    """Бутылочка лака для ногтей."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.68)
    h = int(size * 1.3)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка чёрная высокая
    cap_h = int(h * 0.42)
    cap_w = int(w * 0.6)
    _rounded(d, [cx - cap_w // 2, y0,
                 cx + cap_w // 2, y0 + cap_h],
             radius=3, fill=(22, 22, 22), outline=STROKE, width=2)
    # декоративная золотая полоска на крышке
    d.rectangle([cx - cap_w // 2 + 2, y0 + cap_h - 6,
                 cx + cap_w // 2 - 2, y0 + cap_h - 3], fill=GOLD)
    # горлышко (узкое)
    nk_w = int(w * 0.35)
    d.rectangle([cx - nk_w // 2, y0 + cap_h - 1,
                 cx + nk_w // 2, y0 + cap_h + 5],
                fill=(180, 180, 185), outline=STROKE)
    # флакон (стекло с лаком)
    body_top = y0 + cap_h + 4
    _rounded(d, [x0, body_top, x1, y1],
             radius=6, fill=color, outline=STROKE, width=2)
    # «жидкость» — тонкая линия заполнения
    d.line([x0 + 3, body_top + 8, x1 - 3, body_top + 8],
           fill=darken(color, 0.3), width=1)
    # блик на флаконе
    _rounded(d, [x0 + 5, body_top + 12, x0 + 10, y1 - 10],
             radius=2, fill=lighten(color, 0.5))


def draw_nail_polish_set(img, cx, cy, size, colors=None):
    """Набор гель-лаков."""
    if colors is None:
        colors = ["#C83A5A", "#E8A0B5", "#6B3E7E", "#D4AF37"]
    gap = int(size * 0.06)
    each = int(size * 0.48)
    total = len(colors) * each + (len(colors) - 1) * gap
    start = cx - total // 2
    for i, c in enumerate(colors):
        ex = start + i * (each + gap) + each // 2
        draw_nail_polish(img, ex, cy, int(size * 0.75), color_hex=c)


def draw_lip_balm_stick(img, cx, cy, size, color_hex="#E8A7B8"):
    """Гигиеническая помада — маленький стик."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.38)
    h = int(size * 1.15)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # колпачок
    cap_h = int(h * 0.45)
    _rounded(d, [x0, y0, x1, y0 + cap_h],
             radius=3, fill=darken(color, 0.15), outline=STROKE, width=2)
    # кольцо
    d.rectangle([x0, y0 + cap_h - 4, x1, y0 + cap_h - 2], fill=GOLD)
    # корпус
    body_top = y0 + cap_h - 1
    _rounded(d, [x0, body_top, x1, y1],
             radius=3, fill=color, outline=STROKE, width=2)
    # наклейка-кольцо название
    d.rectangle([x0, body_top + int(h * 0.2),
                 x1, body_top + int(h * 0.23)], fill=(255, 255, 255))


def draw_lip_balm_jar(img, cx, cy, size, color_hex="#E8A7B8"):
    """Бальзам для губ в плоской круглой баночке."""
    color = hex_to_rgb(color_hex)
    w = int(size * 1.0)
    h = int(size * 0.45)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # нижняя часть (банка)
    _rounded(d, [x0, cy - 2, x1, y1],
             radius=8, fill=lighten(color, 0.35),
             outline=STROKE, width=2)
    # крышка
    _rounded(d, [x0, y0, x1, cy + 4],
             radius=8, fill=color, outline=STROKE, width=2)
    # надпись
    d.rectangle([cx - int(w * 0.25), cy - 12,
                 cx + int(w * 0.25), cy - 10], fill=(255, 255, 255))
    d.rectangle([cx - int(w * 0.18), cy - 6,
                 cx + int(w * 0.18), cy - 4], fill=(255, 255, 255))


def draw_cotton_pads(img, cx, cy, size, color_hex="#FFFFFF"):
    """Стопка ватных дисков."""
    color = hex_to_rgb(color_hex)
    r = int(size * 0.55)
    h_each = 4
    layers = 8
    y0 = cy - (layers * h_each) // 2 - r // 3
    y1 = cy + (layers * h_each) // 2 + r // 3

    _soft_shadow(img, (cx - r, y0, cx + r, y1))
    d = ImageDraw.Draw(img)
    # нижний эллипс — тень стопки
    d.ellipse([cx - r, y1 - r // 3, cx + r, y1 + r // 3],
              fill=darken(color, 0.08))
    # слои
    for i in range(layers):
        yy = y1 - i * h_each
        d.ellipse([cx - r, yy - r // 3, cx + r, yy + r // 3],
                  fill=color, outline=(190, 190, 190), width=1)
    # верхний диск — чуть ярче
    top_y = y1 - (layers - 1) * h_each
    d.ellipse([cx - r, top_y - r // 3, cx + r, top_y + r // 3],
              fill=(252, 252, 252),
              outline=(200, 200, 200), width=1)
    # текстура верхнего (круг внутри)
    d.ellipse([cx - r + 6, top_y - r // 3 + 4,
               cx + r - 6, top_y + r // 3 - 4],
              outline=(220, 220, 220), width=1)


def draw_sponge(img, cx, cy, size, color_hex="#F0A4B8"):
    """Спонж-капелька для макияжа."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.85)
    h = int(size * 1.15)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # форма-капля
    d.polygon([
        (cx, y0),
        (x1, cy + int(h * 0.08)),
        (cx + int(w * 0.35), y1),
        (cx - int(w * 0.35), y1),
        (x0, cy + int(h * 0.08)),
    ], fill=color, outline=STROKE)
    # закругления низа
    d.ellipse([x0, cy - int(h * 0.15),
               x1, y1 + 8],
              fill=color, outline=STROKE, width=2)
    # «срез» сверху
    d.ellipse([cx - int(w * 0.08), y0,
               cx + int(w * 0.08), y0 + int(h * 0.12)],
              fill=darken(color, 0.15))
    # блик
    d.ellipse([cx - int(w * 0.25), cy - int(h * 0.08),
               cx - int(w * 0.08), cy + int(h * 0.05)],
              fill=lighten(color, 0.35))


def draw_sheet_mask(img, cx, cy, size, color_hex="#7FBFB0"):
    """Тканевая маска — саше (пакетик)."""
    color = hex_to_rgb(color_hex)
    w = int(size * 1.2)
    h = int(size * 1.4)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # сам пакетик
    _rounded(d, [x0, y0, x1, y1],
             radius=6, fill=color, outline=STROKE, width=2)
    # зубчатый верх (запаян)
    seg = (x1 - x0) // 10
    for i in range(10):
        xx = x0 + i * seg
        d.polygon([(xx, y0),
                   (xx + seg // 2, y0 + 6),
                   (xx + seg, y0)],
                  fill=darken(color, 0.1))
    # декоративный силуэт лица
    face_cx = cx
    face_cy = cy + 8
    face_r = int(w * 0.3)
    d.ellipse([face_cx - face_r, face_cy - face_r,
               face_cx + face_r, face_cy + face_r],
              outline=(255, 255, 255), width=2)
    # прорези
    d.ellipse([face_cx - 14, face_cy - 8,
               face_cx - 6, face_cy - 2], fill=color,
              outline=(255, 255, 255), width=1)
    d.ellipse([face_cx + 6, face_cy - 8,
               face_cx + 14, face_cy - 2], fill=color,
              outline=(255, 255, 255), width=1)
    d.polygon([(face_cx - 5, face_cy + 6),
               (face_cx + 5, face_cy + 6),
               (face_cx, face_cy + 10)], fill=color,
              outline=(255, 255, 255))
    # название сверху-слева
    d.rectangle([x0 + 10, y0 + 16, x0 + int(w * 0.4), y0 + 19],
                fill=(255, 255, 255))
    d.rectangle([x0 + 10, y0 + 24, x0 + int(w * 0.3), y0 + 26],
                fill=lighten(color, 0.4))


def draw_deodorant(img, cx, cy, size, color_hex="#E8E8EE"):
    """Дезодорант-стик — овальное основание + поворотный корпус."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.78)
    h = int(size * 1.35)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # колпачок (овальный)
    cap_h = int(h * 0.45)
    d.ellipse([x0, y0, x1, y0 + 20], fill=color, outline=STROKE, width=2)
    _rounded(d, [x0, y0 + 8, x1, y0 + cap_h],
             radius=4, fill=color, outline=STROKE, width=2)
    # маскируем лишнее в переходе
    d.rectangle([x0 + 2, y0 + 10, x1 - 2, y0 + 20], fill=color)
    # кольцо-шов
    d.rectangle([x0, y0 + cap_h - 3, x1, y0 + cap_h - 1],
                fill=darken(color, 0.1))
    # корпус
    body_top = y0 + cap_h
    _rounded(d, [x0, body_top, x1, y1],
             radius=6, fill=darken(color, 0.08), outline=STROKE, width=2)
    # этикетка по центру
    d.rectangle([x0 + 6, body_top + int(h * 0.15),
                 x1 - 6, body_top + int(h * 0.4)],
                fill=(255, 255, 255), outline=STROKE_LIGHT, width=1)
    d.rectangle([x0 + 12, body_top + int(h * 0.2),
                 x1 - 12, body_top + int(h * 0.23)],
                fill=STROKE)
    d.rectangle([x0 + 12, body_top + int(h * 0.28),
                 x0 + int(w * 0.7), body_top + int(h * 0.3)],
                fill=STROKE_LIGHT)


def draw_spray_bottle(img, cx, cy, size, color_hex="#D6E4F0"):
    """Спрей-термозащита — с распылителем-триггером."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.7)
    h = int(size * 1.4)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # распылитель-триггер (сверху-слева)
    trig_h = int(h * 0.15)
    _rounded(d, [x0 - int(w * 0.2), y0 + int(trig_h * 0.2),
                 cx + int(w * 0.1), y0 + trig_h],
             radius=3, fill=(44, 44, 44), outline=STROKE, width=2)
    # носик спрея
    d.polygon([
        (x0 - int(w * 0.2), y0 + trig_h // 2),
        (x0 - int(w * 0.3), y0 + trig_h // 2 - 3),
        (x0 - int(w * 0.3), y0 + trig_h // 2 + 3),
    ], fill=(44, 44, 44))
    # шейка
    d.rectangle([cx - int(w * 0.2), y0 + trig_h - 1,
                 cx + int(w * 0.2), y0 + trig_h + 8],
                fill=(44, 44, 44))
    # тело
    body_top = y0 + trig_h + 5
    _rounded(d, [x0, body_top, x1, y1],
             radius=8, fill=color, outline=STROKE, width=2)
    # блик
    _rounded(d, [x0 + 5, body_top + 6, x0 + 11, y1 - 18],
             radius=3, fill=lighten(color, 0.5))
    # этикетка
    lbl_y = body_top + int(h * 0.25)
    _rounded(d, [x0 + 6, lbl_y, x1 - 6, lbl_y + int(h * 0.3)],
             radius=3, fill=(255, 255, 255), outline=STROKE_LIGHT, width=1)
    d.rectangle([x0 + 12, lbl_y + 8, x1 - 12, lbl_y + 11], fill=STROKE)
    d.rectangle([x0 + 12, lbl_y + 17, x1 - 20, lbl_y + 19],
                fill=STROKE_LIGHT)


def draw_dropper_bottle(img, cx, cy, size, color_hex="#E6C47F", dark=False):
    """Флакон-капельница (сыворотка, масло для кутикулы)."""
    color = hex_to_rgb(color_hex)
    glass_tint = darken(color, 0.2) if dark else color
    w = int(size * 0.6)
    h = int(size * 1.35)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # резиновый колпачок пипетки (сверху)
    bulb_h = int(h * 0.12)
    bulb_w = int(w * 0.4)
    _rounded(d, [cx - bulb_w // 2, y0,
                 cx + bulb_w // 2, y0 + bulb_h],
             radius=5, fill=CAP_DARK, outline=STROKE, width=2)
    # крышка флакона
    cap_h = int(h * 0.14)
    _rounded(d, [x0 + 3, y0 + bulb_h, x1 - 3, y0 + bulb_h + cap_h],
             radius=3, fill=(52, 52, 52), outline=STROKE, width=2)
    # флакон
    body_top = y0 + bulb_h + cap_h - 2
    _rounded(d, [x0, body_top, x1, y1],
             radius=6, fill=glass_tint, outline=STROKE, width=2)
    # блик
    _rounded(d, [x0 + 5, body_top + 6, x0 + 10, y1 - 14],
             radius=2, fill=lighten(glass_tint, 0.5))
    # капля-пипетка внутри (намёк)
    d.line([cx, body_top, cx, y1 - int(h * 0.15)],
           fill=darken(glass_tint, 0.35), width=2)
    # этикетка
    lbl_y = body_top + int(h * 0.35)
    d.rectangle([x0 + 4, lbl_y, x1 - 4, lbl_y + 2], fill=GOLD)
    d.rectangle([x0 + 4, lbl_y + 8, x1 - 8, lbl_y + 10], fill=STROKE)


def draw_eye_patches(img, cx, cy, size, color_hex="#F8C8D8"):
    """Баночка патчей для глаз (прозрачная + патчи)."""
    color = hex_to_rgb(color_hex)
    w = int(size * 1.1)
    h = int(size * 0.95)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка
    cap_h = int(h * 0.2)
    _rounded(d, [x0, y0, x1, y0 + cap_h],
             radius=8, fill=GOLD, outline=STROKE, width=2)
    # стенки банки (полупрозрачные)
    _rounded(d, [x0, y0 + cap_h - 2, x1, y1],
             radius=10, fill=lighten(color, 0.45),
             outline=STROKE, width=2)
    # маскируем верх скругления
    d.rectangle([x0 + 2, y0 + cap_h - 2, x1 - 2, y0 + cap_h + 2],
                fill=lighten(color, 0.45))
    # сами патчи — видны сквозь стенку
    patch_y = cy + 2
    for i, dx in enumerate([-int(w * 0.22), int(w * 0.02), int(w * 0.22)]):
        d.ellipse([cx + dx - 16, patch_y - 7,
                   cx + dx + 16, patch_y + 7],
                  fill=color, outline=darken(color, 0.2), width=1)
    # блик на банке
    _rounded(d, [x0 + 8, y0 + cap_h + 4, x0 + 12, y1 - 18],
             radius=2, fill=(255, 255, 255, 160) if False else lighten(color, 0.3))


def draw_lip_gloss(img, cx, cy, size, color_hex="#E86B9E"):
    """Блеск для губ с палочкой-аппликатором."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.48)
    h = int(size * 1.5)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # крышка-колпачок (с тонким горлышком)
    cap_h = int(h * 0.55)
    _rounded(d, [x0, y0, x1, y0 + cap_h],
             radius=3, fill=darken(color, 0.25),
             outline=STROKE, width=2)
    # декоративное кольцо
    d.rectangle([x0, y0 + cap_h - 5, x1, y0 + cap_h - 3], fill=GOLD)
    # флакон с блеском
    body_top = y0 + cap_h - 1
    _rounded(d, [x0 + 2, body_top, x1 - 2, y1],
             radius=5, fill=color, outline=STROKE, width=2)
    # блик
    d.rectangle([x0 + 5, body_top + 6, x0 + 8, y1 - 10],
                fill=lighten(color, 0.5))


def draw_perfume(img, cx, cy, size, color_hex="#E8B87A", cap_gold=True):
    """Классический флакон парфюма (прямоугольный + золотая пробка)."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.9)
    h = int(size * 1.35)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # пробка (золотая, крупная)
    cap_h = int(h * 0.22)
    cap_w = int(w * 0.45)
    cap_color = GOLD if cap_gold else CAP_DARK
    _rounded(d, [cx - cap_w // 2, y0,
                 cx + cap_w // 2, y0 + cap_h],
             radius=4, fill=cap_color, outline=STROKE, width=2)
    # блик на пробке
    d.rectangle([cx - cap_w // 2 + 3, y0 + 2,
                 cx - cap_w // 2 + 6, y0 + cap_h - 2],
                fill=lighten(cap_color, 0.4))
    # горлышко
    d.rectangle([cx - int(cap_w * 0.35), y0 + cap_h - 1,
                 cx + int(cap_w * 0.35), y0 + cap_h + 6],
                fill=(210, 210, 214), outline=STROKE)
    # тело (прямоугольный флакон с закруглением)
    body_top = y0 + cap_h + 5
    _rounded(d, [x0, body_top, x1, y1],
             radius=10, fill=color, outline=STROKE, width=2)
    # верхняя тень на флаконе
    d.line([x0 + 2, body_top + 3, x1 - 2, body_top + 3],
           fill=darken(color, 0.15), width=1)
    # шильдик-табличка
    lbl_y0 = body_top + int(h * 0.25)
    lbl_y1 = body_top + int(h * 0.6)
    _rounded(d, [x0 + int(w * 0.2), lbl_y0,
                 x1 - int(w * 0.2), lbl_y1],
             radius=4, fill=(255, 255, 255), outline=STROKE_LIGHT, width=1)
    d.rectangle([x0 + int(w * 0.28), lbl_y0 + 8,
                 x1 - int(w * 0.28), lbl_y0 + 11], fill=STROKE)
    d.rectangle([x0 + int(w * 0.33), lbl_y0 + 19,
                 x1 - int(w * 0.33), lbl_y0 + 21], fill=GOLD)
    # блик на флаконе
    _rounded(d, [x0 + 8, body_top + 8, x0 + 14, y1 - 18],
             radius=3, fill=lighten(color, 0.35))


def draw_perfume_luxe(img, cx, cy, size, color_hex="#F5D68E"):
    """Люкс-парфюм: высокий гранёный флакон с большой золотой пробкой."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.95)
    h = int(size * 1.5)
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # пробка крупная, многоугольная
    cap_h = int(h * 0.3)
    cap_w = int(w * 0.55)
    # основание пробки
    _rounded(d, [cx - cap_w // 2, y0 + int(cap_h * 0.15),
                 cx + cap_w // 2, y0 + cap_h],
             radius=4, fill=GOLD, outline=STROKE, width=2)
    # верхушка пробки (ромб-«драгоценность»)
    top_w = int(cap_w * 0.7)
    d.polygon([
        (cx - top_w // 2, y0 + int(cap_h * 0.2)),
        (cx, y0),
        (cx + top_w // 2, y0 + int(cap_h * 0.2)),
        (cx, y0 + int(cap_h * 0.4)),
    ], fill=GOLD_LIGHT, outline=STROKE)
    # блик на пробке
    d.polygon([(cx - 4, y0 + 4), (cx + 4, y0 + 4), (cx, y0 + int(cap_h * 0.3))],
              fill=(255, 246, 200))
    # горлышко
    neck_w = int(cap_w * 0.4)
    d.rectangle([cx - neck_w // 2, y0 + cap_h - 1,
                 cx + neck_w // 2, y0 + cap_h + 6],
                fill=GOLD_DARK, outline=STROKE)
    # гранёный флакон: трапеция
    body_top = y0 + cap_h + 5
    d.polygon([
        (x0 + int(w * 0.07), body_top),
        (x1 - int(w * 0.07), body_top),
        (x1, y1 - int(h * 0.1)),
        (x1 - int(w * 0.1), y1),
        (x0 + int(w * 0.1), y1),
        (x0, y1 - int(h * 0.1)),
    ], fill=color, outline=STROKE)
    # вертикальная грань-блик
    d.line([x0 + int(w * 0.35), body_top + 4,
            x0 + int(w * 0.35), y1 - 6],
           fill=lighten(color, 0.35), width=2)
    # центральная эмблема
    emb_r = int(w * 0.14)
    d.ellipse([cx - emb_r, cy + int(h * 0.08),
               cx + emb_r, cy + int(h * 0.08) + emb_r * 2],
              fill=GOLD, outline=STROKE, width=2)
    d.ellipse([cx - 3, cy + int(h * 0.08) + emb_r - 3,
               cx + 3, cy + int(h * 0.08) + emb_r + 3],
              fill=GOLD_DARK)


def draw_hair_dryer(img, cx, cy, size, color_hex="#2A2A2E"):
    """Фен-стайлер — вид сбоку. Компактная композиция со шнуром, который
    аккуратно сворачивается внутри области и не вылезает снизу."""
    color = hex_to_rgb(color_hex)
    w = int(size * 1.4)
    # уменьшенная общая высота — фен поместится в зоне карточки
    h = int(size * 1.05)

    d = ImageDraw.Draw(img)
    # корпус-двигатель — чуть выше центра, чтобы осталось место ручке + шнуру
    body_cy = cy - int(h * 0.12)
    bx0 = cx - int(w * 0.4)
    bx1 = cx + int(w * 0.25)
    by0 = body_cy - int(h * 0.22)
    by1 = body_cy + int(h * 0.22)
    _soft_shadow(img, (bx0, by0, cx + int(w * 0.4), by1 + 30))
    _rounded(d, [bx0, by0, bx1, by1],
             radius=16, fill=color, outline=STROKE, width=2)
    # сопло (сужающееся)
    noz_x0 = bx1 - 4
    noz_x1 = cx + int(w * 0.4)
    noz_y0 = body_cy - int(h * 0.15)
    noz_y1 = body_cy + int(h * 0.15)
    d.polygon([
        (noz_x0, by0 + 4), (noz_x1, noz_y0),
        (noz_x1, noz_y1), (noz_x0, by1 - 4),
    ], fill=color, outline=STROKE)
    # внутреннее кольцо сопла
    d.ellipse([noz_x1 - 10, noz_y0, noz_x1, noz_y1],
              fill=GOLD, outline=STROKE)
    d.ellipse([noz_x1 - 7, noz_y0 + 3, noz_x1 - 2, noz_y1 - 3],
              fill=(20, 20, 20))
    # решётка сзади
    d.ellipse([bx0 - 2, by0 + 4, bx0 + 14, by1 - 4],
              fill=darken(color, 0.3), outline=STROKE, width=2)
    d.ellipse([bx0 + 4, by0 + 10, bx0 + 10, by1 - 10],
              outline=GOLD_LIGHT, width=1)
    # ручка (вниз) — короче, чтобы шнур уместился
    hy0 = by1 - 4
    hy1 = hy0 + int(h * 0.34)
    hx0 = cx - int(w * 0.16)
    hx1 = cx + int(w * 0.02)
    _rounded(d, [hx0, hy0, hx1, hy1],
             radius=7, fill=color, outline=STROKE, width=2)
    # кнопка на ручке
    _rounded(d, [hx0 + 3, hy0 + 9, hx1 - 3, hy0 + 15],
             radius=2, fill=GOLD)
    # шнур — аккуратная дуга вниз-влево, полностью внутри зоны
    cord_sx = (hx0 + hx1) // 2
    cord_sy = hy1
    # 10 сегментов по дуге
    import math as _m
    steps = 10
    for i in range(steps):
        t = (i + 1) / steps
        # дуга по квадратичной Безье: от (cord_sx, cord_sy) влево-вниз
        dx = -int(w * 0.22 * t)
        dy = int(h * 0.14 * _m.sin(t * _m.pi * 0.75))
        px = cord_sx + dx
        py = cord_sy + dy + int(h * 0.02 * t)
        d.ellipse([px - 3, py - 3, px + 3, py + 3],
                  outline=color, width=1)


def draw_straightener(img, cx, cy, size, color_hex="#D4AF37"):
    """Выпрямитель-титан (две пластины)."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.5)
    h = int(size * 1.5)
    x0 = cx - w // 2
    x1 = cx + w // 2
    y0 = cy - h // 2
    y1 = cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # основная форма (две половины с зазором)
    gap_y = cy + int(h * 0.05)
    # верхняя половина
    _rounded(d, [x0, y0, x1, gap_y - 3],
             radius=12, fill=color, outline=STROKE, width=2)
    # нижняя половина
    _rounded(d, [x0, gap_y + 3, x1, y1],
             radius=12, fill=color, outline=STROKE, width=2)
    # пластина сверху (внутренняя, видно между половинами)
    plate_y0 = gap_y - 3
    plate_y1 = gap_y + 3
    d.rectangle([x0 + 6, plate_y0, x1 - 6, plate_y1],
                fill=(240, 240, 245), outline=STROKE, width=1)
    # экран (на верхней ручке)
    _rounded(d, [x0 + 6, y0 + int(h * 0.1), x1 - 6, y0 + int(h * 0.22)],
             radius=3, fill=(20, 20, 20), outline=STROKE, width=1)
    d.rectangle([x0 + 10, y0 + int(h * 0.14),
                 x0 + int(w * 0.6), y0 + int(h * 0.17)],
                fill=GOLD_LIGHT)
    # кнопки
    d.ellipse([cx - 3, y0 + int(h * 0.28), cx + 3, y0 + int(h * 0.33)],
              fill=darken(color, 0.2), outline=STROKE)
    d.ellipse([cx - 3, y0 + int(h * 0.36), cx + 3, y0 + int(h * 0.41)],
              fill=darken(color, 0.2), outline=STROKE)
    # шнур внизу
    for i in range(8):
        xi = cx + (5 if i % 2 else -5)
        d.ellipse([xi - 3, y1 + i * 5, xi + 3, y1 + i * 5 + 6],
                  outline=STROKE, width=1)


def draw_brush_set(img, cx, cy, size):
    """Набор кистей для макияжа."""
    d = ImageDraw.Draw(img)
    brushes = [
        ("#E8D5A8", "#8A7040", 1.15, 0.18),   # большая пушистая
        ("#F5E5BA", "#9E8050", 1.0, 0.14),    # средняя
        ("#F5D5B0", "#8A5A40", 0.9, 0.08),    # плоская узкая
        ("#FFFFFF", "#999999", 1.05, 0.12),   # белая плоская
    ]
    total_w = int(size * 1.3)
    gap = total_w // (len(brushes) + 1)
    start = cx - total_w // 2
    for i, (bristle_hex, handle_hex, hlen, bw) in enumerate(brushes):
        x = start + (i + 1) * gap
        _draw_brush(d, img, x, cy, size * hlen, size * bw,
                    bristle_hex, handle_hex)


def _draw_brush(d, img, cx, cy, h, bw, bristle_hex, handle_hex):
    """Одна кисть."""
    bristle = hex_to_rgb(bristle_hex)
    handle = hex_to_rgb(handle_hex)
    h = int(h)
    bw = max(10, int(bw))
    x0 = cx - bw // 2
    x1 = cx + bw // 2
    y0 = cy - h // 2
    y1 = cy + h // 2
    # тень
    _soft_shadow(img, (x0, y0, x1, y1), color=(0, 0, 0, 30), blur=4)
    # кисть-волос (верх)
    bristle_h = int(h * 0.28)
    d.polygon([
        (x0 - 2, y0 + bristle_h),
        (cx - bw // 3, y0 + 2),
        (cx + bw // 3, y0 + 2),
        (x1 + 2, y0 + bristle_h),
    ], fill=bristle, outline=darken(bristle, 0.2))
    # обойма
    fer_y0 = y0 + bristle_h - 1
    fer_y1 = fer_y0 + int(h * 0.08)
    _rounded(d, [x0, fer_y0, x1, fer_y1],
             radius=2, fill=GOLD, outline=STROKE, width=1)
    d.rectangle([x0, fer_y0 + 2, x1, fer_y0 + 4], fill=GOLD_DARK)
    # ручка
    _rounded(d, [x0, fer_y1, x1, y1],
             radius=bw // 3, fill=handle, outline=STROKE, width=1)
    # блик на ручке
    d.rectangle([x0 + 2, fer_y1 + 3, x0 + 3, y1 - 6],
                fill=lighten(handle, 0.3))


def draw_beauty_box(img, cx, cy, size):
    """VIP-бьюти-бокс: открытая коробка с содержимым."""
    d = ImageDraw.Draw(img)
    w = int(size * 1.4)
    h = int(size * 1.05)
    x0 = cx - w // 2
    x1 = cx + w // 2
    y0 = cy - int(h * 0.3)
    y1 = cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    # задняя «стенка» коробки (выше)
    back_y0 = y0 - int(h * 0.25)
    d.polygon([
        (x0 + 15, back_y0),
        (x1 - 15, back_y0),
        (x1, y0 + 10),
        (x0, y0 + 10),
    ], fill=darken(GOLD, 0.25), outline=STROKE)
    # ленточка (атласный бант сверху)
    d.rectangle([cx - 4, back_y0 - 8, cx + 4, back_y0 + 4],
                fill=GOLD_LIGHT, outline=STROKE, width=1)
    d.polygon([
        (cx - 14, back_y0 - 4),
        (cx, back_y0 + 2),
        (cx - 14, back_y0 + 8),
    ], fill=GOLD, outline=STROKE)
    d.polygon([
        (cx + 14, back_y0 - 4),
        (cx, back_y0 + 2),
        (cx + 14, back_y0 + 8),
    ], fill=GOLD, outline=STROKE)
    # коробка-основание
    _rounded(d, [x0, y0 + 8, x1, y1],
             radius=6, fill=GOLD, outline=STROKE, width=2)
    # внутренняя полка (чуть темнее)
    _rounded(d, [x0 + 10, y0 + 18, x1 - 10, y0 + 50],
             radius=4, fill=darken(GOLD, 0.18),
             outline=STROKE, width=1)
    # содержимое — маленькие флакончики внутри
    # парфюм
    d.rectangle([x0 + 20, y0 + 22, x0 + 34, y0 + 48],
                fill="#F5E0A8", outline=STROKE)
    d.rectangle([x0 + 24, y0 + 18, x0 + 30, y0 + 24], fill=GOLD_DARK)
    # помада
    d.rectangle([x0 + 44, y0 + 26, x0 + 54, y0 + 48],
                fill="#C83A5A", outline=STROKE)
    d.rectangle([x0 + 44, y0 + 24, x0 + 54, y0 + 28],
                fill=(22, 22, 22))
    # тюбик
    _rounded(d, [x0 + 64, y0 + 30, x0 + 90, y0 + 48],
             radius=3, fill=(255, 255, 255), outline=STROKE, width=1)
    d.rectangle([x0 + 88, y0 + 32, x0 + 92, y0 + 46],
                fill=GOLD)
    # маленький кружок-пудра
    d.ellipse([x1 - 45, y0 + 30, x1 - 25, y0 + 50],
              fill="#F5D5B0", outline=STROKE)
    # надпись на коробке
    lbl_y = y0 + 60
    d.rectangle([cx - int(w * 0.25), lbl_y,
                 cx + int(w * 0.25), lbl_y + 3], fill=(22, 22, 22))
    d.rectangle([cx - int(w * 0.15), lbl_y + 10,
                 cx + int(w * 0.15), lbl_y + 12],
                fill=darken(GOLD, 0.4))


def draw_haute_couture_set(img, cx, cy, size):
    """Коллекция Haute Couture — композиция из премиум-предметов."""
    d = ImageDraw.Draw(img)
    # общая «подставка»
    plate_w = int(size * 1.4)
    plate_h = int(size * 0.12)
    _rounded(d, [cx - plate_w // 2, cy + int(size * 0.55),
                 cx + plate_w // 2, cy + int(size * 0.55) + plate_h],
             radius=4, fill=darken(GOLD, 0.35), outline=STROKE, width=2)
    # центр: парфюм-люкс
    draw_perfume_luxe(img, cx, cy + int(size * 0.1),
                      int(size * 0.7), color_hex="#F5D68E")
    # слева: помада
    draw_lipstick(img, cx - int(size * 0.5), cy + int(size * 0.25),
                  int(size * 0.55), color_hex="#A02B44", case_hex="#1A1A1A")
    # справа: компактная пудра
    draw_compact(img, cx + int(size * 0.5), cy + int(size * 0.3),
                 int(size * 0.5), color_hex="#F0D5B8", case_hex="#1A1A1A")


def draw_gold_mask_jar(img, cx, cy, size):
    """Золотая маска 24K — банка с золотым покрытием."""
    d = ImageDraw.Draw(img)
    w = int(size * 1.0)
    h = int(size * 0.92)
    x0 = cx - w // 2
    x1 = cx + w // 2
    y0 = cy - h // 2
    y1 = cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    # крышка (золото-тиснёная)
    lid_h = int(h * 0.3)
    _rounded(d, [x0, y0, x1, y0 + lid_h],
             radius=10, fill=GOLD, outline=STROKE, width=2)
    # эмблема на крышке
    d.ellipse([cx - 12, y0 + 6, cx + 12, y0 + 22],
              fill=darken(GOLD, 0.25), outline=STROKE, width=1)
    d.text((cx, y0 + 14), "24K", anchor="mm",
           fill=(240, 220, 140))
    # тело банки (полупрозрачное + золотое напыление)
    body_top = y0 + lid_h - 3
    _rounded(d, [x0, body_top, x1, y1],
             radius=12, fill=lighten(GOLD, 0.4),
             outline=STROKE, width=2)
    # маскируем стык
    d.rectangle([x0 + 2, body_top, x1 - 2, body_top + 3],
                fill=lighten(GOLD, 0.4))
    # «24K GOLD» надпись
    lbl_y0 = body_top + int(h * 0.2)
    _rounded(d, [x0 + 10, lbl_y0,
                 x1 - 10, lbl_y0 + int(h * 0.35)],
             radius=4, fill=(255, 255, 255, 240),
             outline=GOLD_DARK, width=2)
    d.rectangle([x0 + 18, lbl_y0 + 6, x1 - 18, lbl_y0 + 9], fill=GOLD_DARK)
    d.rectangle([x0 + 22, lbl_y0 + 15, x1 - 22, lbl_y0 + 18], fill=STROKE)
    # частички золота вокруг
    import random as _r
    _r.seed(42)
    for _ in range(18):
        px = x0 + _r.randint(-20, w + 20)
        py = y0 + _r.randint(-10, h + 20)
        s = _r.randint(1, 3)
        d.ellipse([px, py, px + s, py + s], fill=GOLD_LIGHT)


def draw_pump_bottle(img, cx, cy, size, color_hex="#F0E3C8"):
    """Флакон с дозатором-помпой (тональный крем, сыворотка)."""
    color = hex_to_rgb(color_hex)
    w = int(size * 0.6)
    h = int(size * 1.5)
    x0 = cx - w // 2
    x1 = cx + w // 2
    y0 = cy - h // 2
    y1 = cy + h // 2

    _soft_shadow(img, (x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    # помпа (носик сбоку)
    pump_x0 = cx - int(w * 0.05)
    pump_x1 = cx + int(w * 0.3)
    pump_y0 = y0
    pump_y1 = y0 + int(h * 0.07)
    _rounded(d, [pump_x0, pump_y0, pump_x1, pump_y1],
             radius=2, fill=CAP_DARK)
    # стойка помпы
    d.rectangle([cx - int(w * 0.08), pump_y1,
                 cx + int(w * 0.08), y0 + int(h * 0.14)],
                fill=CAP_DARK)
    # колпачок-основание дозатора
    cap_h = int(h * 0.12)
    _rounded(d, [x0 + 2, y0 + int(h * 0.1), x1 - 2, y0 + int(h * 0.1) + cap_h],
             radius=3, fill=CAP_DARK, outline=STROKE, width=2)
    # тело флакона
    body_top = y0 + int(h * 0.1) + cap_h - 2
    _rounded(d, [x0, body_top, x1, y1],
             radius=8, fill=color, outline=STROKE, width=2)
    # этикетка
    lbl_y0 = body_top + int(h * 0.2)
    d.rectangle([x0 + 4, lbl_y0, x1 - 4, lbl_y0 + 3], fill=GOLD)
    d.rectangle([x0 + 4, lbl_y0 + 10, x1 - 4, lbl_y0 + 13], fill=STROKE)
    d.rectangle([x0 + 8, lbl_y0 + 21, x1 - 12, lbl_y0 + 23],
                fill=STROKE_LIGHT)
    # блик
    _rounded(d, [x0 + 5, body_top + 8, x0 + 9, y1 - 16],
             radius=2, fill=lighten(color, 0.5))


# ─── Мастер-диспетчер ────────────────────────────────────────────────────────

# Палитры цветов, подобранные под каждый товар
PRODUCT_MAP = {
    # ─── Common ─────────────────────────────────────────────────────
    "C001": ("bottle_tall",        {"color_hex": "#B8D8E8"}),     # Мицеллярная вода
    "C002": ("lip_balm_stick",     {"color_hex": "#E8A7B8"}),     # Гиг. помада
    "C003": ("cotton_pads",        {"color_hex": "#FAFAFA"}),     # Ватные диски
    "C004": ("tube",               {"color_hex": "#F5EEDC", "cap_hex": "#D4AF37", "accent_hex": "#D4AF37"}),  # Крем для рук
    "C005": ("bottle_tall",        {"color_hex": "#CFE4D0"}),     # Тоник для лица
    "C006": ("tube",               {"color_hex": "#E8D5E3", "cap_hex": "#7C4A8C"}),  # Пилинг
    "C007": ("sheet_mask",         {"color_hex": "#7FBFB0"}),     # Тканевая маска
    "C008": ("sponge",             {"color_hex": "#F0A4B8"}),     # Спонж
    "C009": ("nail_polish",        {"color_hex": "#C83A5A"}),     # Лак для ногтей
    "C010": ("lip_balm_jar",       {"color_hex": "#F0AAB8"}),     # Бальзам для губ
    "C011": ("bottle_big",         {"color_hex": "#F5EEDC", "cap_hex": "#E8C547"}),  # Шампунь
    "C012": ("bottle_big",         {"color_hex": "#E0D8F0", "cap_hex": "#7C4A8C"}),  # Кондиционер
    "C013": ("bottle_big",         {"color_hex": "#F5F2EA", "cap_hex": "#9FE85A"}),  # Гель для душа
    "C014": ("deodorant",          {"color_hex": "#E8E8EE"}),     # Дезодорант
    "C015": ("tube",               {"color_hex": "#FFFFFF", "cap_hex": "#4A6FA5", "accent_hex": "#4A6FA5"}),  # Пена для умывания
    "C016": ("eye_patches",        {"color_hex": "#F8C8D8"}),     # Патчи для глаз
    "C017": ("jar",                {"color_hex": "#E5CEB5", "lid_hex": "#8B5A3C"}),  # Скраб для тела
    "C018": ("dropper_bottle",     {"color_hex": "#F0E4C8"}),     # Масло для кутикулы
    "C019": ("spray_bottle",       {"color_hex": "#DCEAF5"}),     # Термозащита
    "C020": ("tube_vertical",      {"color_hex": "#FFE19A", "cap_hex": "#E8A24A", "accent_hex": "#E8A24A"}),  # Солнцезащитный крем

    # ─── Rare ───────────────────────────────────────────────────────
    "R001": ("mascara",            {"color_hex": "#111111"}),     # Тушь
    "R002": ("lipstick",           {"color_hex": "#B83246", "case_hex": "#1A1A1A"}),  # Помада Velvet
    "R003": ("palette",            {"tones": ["#EAD6B8", "#C9A37B", "#9C6E48", "#5F3E24"],
                                    "case_hex": "#2E2E2E"}),       # Палетка Nude
    "R004": ("tube_vertical",      {"color_hex": "#F5DCC4", "cap_hex": "#8B6A48", "accent_hex": "#D4AF37"}),  # BB-крем
    "R005": ("compact",            {"color_hex": "#E8B5A0", "case_hex": "#C78A6A"}),  # Хайлайтер Rose Gold
    "R006": ("tube_vertical",      {"color_hex": "#F5E0C8", "cap_hex": "#2E2E2E", "accent_hex": "#D4AF37"}),  # Консилер Pro
    "R007": ("compact",            {"color_hex": "#F0A995", "case_hex": "#2E2E2E"}),  # Румяна Peachy
    "R008": ("pencil",             {"color_hex": "#5C3A26"}),     # Карандаш для бровей
    "R009": ("eyeliner",           {"color_hex": "#1A1A1A"}),     # Подводка
    "R010": ("dropper_bottle",     {"color_hex": "#F0B060", "dark": True}),  # Сыворотка витамин C
    "R011": ("jar",                {"color_hex": "#F5EEDC", "lid_hex": "#D4AF37"}),  # Маска кератин
    "R012": ("compact",            {"color_hex": "#F0DCC0", "case_hex": "#2E2E2E"}),  # Пудра матирующая
    "R013": ("tube_vertical",      {"color_hex": "#F5E8D0", "cap_hex": "#D4AF37", "accent_hex": "#D4AF37"}),  # Праймер Glow
    "R014": ("lip_gloss",          {"color_hex": "#E86B9E"}),     # Блеск для губ
    "R015": ("bottle_tall",        {"color_hex": "#E8B87A", "cap_hex": "#D4AF37"}),  # Масло для тела

    # ─── Epic ───────────────────────────────────────────────────────
    "E001": ("perfume",            {"color_hex": "#F5D68E", "cap_gold": True}),  # Парфюм Golden Aura
    "E002": ("palette",            {"tones": ["#3A2A5A", "#6A3E7E", "#9E5FA0", "#D4AF37"],
                                    "case_hex": "#1A1A1E"}),  # Палетка Midnight
    "E003": ("pump_bottle",        {"color_hex": "#F0E3C8"}),     # Тональный Luxe
    "E004": ("brush_set",          {}),                            # Набор кистей
    "E005": ("jar",                {"color_hex": "#FFFFFF", "lid_hex": "#D4AF37"}),  # Крем Anti-Age
    "E006": ("dropper_bottle",     {"color_hex": "#E89850", "dark": True}),  # Сыворотка ретинол
    "E007": ("nail_polish_set",    {"colors": ["#C83A5A", "#E8A0B5", "#6B3E7E", "#D4AF37"]}),  # Гель-лаки
    "E008": ("hair_dryer",         {}),                            # Фен-стайлер
    "E009": ("lipstick_set",       {"colors": ["#C43E57", "#A02B44", "#E89B81", "#7E3F5C"]}),  # Помады Ombre
    "E010": ("perfume",            {"color_hex": "#2E2E5A", "cap_gold": True}),  # Парфюм Velvet Night

    # ─── Legendary ──────────────────────────────────────────────────
    "L001": ("perfume_luxe",       {"color_hex": "#F5D68E"}),     # Парфюм Exclusive №1
    "L002": ("beauty_box",         {}),                            # VIP бьюти-бокс
    "L003": ("straightener",       {"color_hex": "#D4AF37"}),     # Выпрямитель Titan
    "L004": ("haute_couture_set",  {}),                            # Коллекция Haute Couture
    "L005": ("gold_mask_jar",      {}),                            # Золотая маска 24K
}


# Диспетчеры рисования
_DRAWERS = {
    "bottle_tall":      draw_bottle_tall,
    "bottle_big":       draw_bottle_big,
    "tube":             draw_tube,
    "tube_vertical":    draw_tube_vertical,
    "jar":              draw_jar,
    "compact":          draw_compact,
    "palette":          draw_palette,
    "lipstick":         draw_lipstick,
    "lipstick_set":     draw_lipstick_set,
    "mascara":          draw_mascara,
    "eyeliner":         draw_eyeliner,
    "pencil":           draw_pencil,
    "nail_polish":      draw_nail_polish,
    "nail_polish_set":  draw_nail_polish_set,
    "lip_balm_stick":   draw_lip_balm_stick,
    "lip_balm_jar":     draw_lip_balm_jar,
    "cotton_pads":      draw_cotton_pads,
    "sponge":           draw_sponge,
    "sheet_mask":       draw_sheet_mask,
    "deodorant":        draw_deodorant,
    "spray_bottle":     draw_spray_bottle,
    "dropper_bottle":   draw_dropper_bottle,
    "eye_patches":      draw_eye_patches,
    "lip_gloss":        draw_lip_gloss,
    "perfume":          draw_perfume,
    "perfume_luxe":     draw_perfume_luxe,
    "hair_dryer":       draw_hair_dryer,
    "straightener":     draw_straightener,
    "brush_set":        draw_brush_set,
    "beauty_box":       draw_beauty_box,
    "haute_couture_set": draw_haute_couture_set,
    "gold_mask_jar":    draw_gold_mask_jar,
    "pump_bottle":      draw_pump_bottle,
}


def draw_product(img: Image.Image, product_id: str, cx: int, cy: int,
                 size: int) -> None:
    """Главная точка: рисует товар по его product_id на заданном центре."""
    if product_id not in PRODUCT_MAP:
        # fallback — общая бутылочка
        draw_bottle_tall(img, cx, cy, size)
        return
    shape, kwargs = PRODUCT_MAP[product_id]
    drawer = _DRAWERS[shape]
    # имя параметра для size разное; передаём как есть — функции принимают size
    drawer(img, cx, cy, size, **kwargs)
