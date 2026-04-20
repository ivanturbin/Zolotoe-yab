"""
theme.py — Фирменный стиль «Золотое Яблоко».

Собран по мотивам айдентики goldapple.ru:
  • Золотая гамма (редизайн апреля 2025): #D4AF37, #E8C547
  • Фирменный зелёный (историческая айдентика):  #9FE85A
  • Белый/кремовый фон, чёрный текст — чистый европейский минимализм
  • Шрифт Unbounded (Yandex) — жирный гротеск без засечек для заголовков
  • Inter — body-шрифт
"""

from __future__ import annotations

import os
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import QDir

from utils.config import ASSETS_DIR
from utils.logger import get_logger

log = get_logger(__name__)

FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# ─── Brand colors ────────────────────────────────────────────────────────────

COLOR_BG          = "#F7F5F0"   # кремовый фон (как на сайте)
COLOR_BG_DARK     = "#0F0F0F"   # для паков
COLOR_BG_CARD     = "#FFFFFF"   # карточки товаров
COLOR_TEXT        = "#0F0F0F"   # основной текст
COLOR_TEXT_MUTED  = "#8A8680"   # приглушённый текст
COLOR_GOLD        = "#D4AF37"   # золото — основной акцент
COLOR_GOLD_LIGHT  = "#E8C547"   # светлое золото
COLOR_GOLD_DARK   = "#A8871C"   # тёмное золото
COLOR_GREEN       = "#9FE85A"   # фирменный зелёный (историч.)
COLOR_BORDER      = "#E8E4DC"   # тонкие разделители
COLOR_HOVER       = "#EDE9E0"   # наведение

# Rarity palette — подобрано в духе бренда (spare, premium)
RARITY_COLORS_HEX = {
    "Common":    "#8A8680",    # серо-бежевый (низкая рарность)
    "Rare":      "#4A6FA5",    # приглушённый синий
    "Epic":      "#7C4A8C",    # приглушённый пурпур
    "Legendary": "#D4AF37",    # золото (флагман бренда)
}


# ─── Font loading ────────────────────────────────────────────────────────────

_loaded: bool = False
_family_heading: str = "Arial"
_family_body: str = "Arial"


def load_brand_fonts() -> None:
    """Регистрирует Unbounded и Inter в QFontDatabase.

    Должна вызываться ОДИН раз после создания QApplication.
    """
    global _loaded, _family_heading, _family_body
    if _loaded:
        return

    heading_files = [
        "Unbounded-Medium.ttf",
        "Unbounded-Bold.ttf",
        "Unbounded-Black.ttf",
    ]
    body_files = [
        "Inter-Regular.ttf",
        "Inter-Medium.ttf",
        "Inter-Bold.ttf",
    ]

    heading_family = None
    body_family = None

    for fname in heading_files:
        path = os.path.join(FONTS_DIR, fname)
        if os.path.isfile(path):
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id != -1:
                fams = QFontDatabase.applicationFontFamilies(font_id)
                if fams:
                    heading_family = fams[0]
                    log.debug("Loaded heading font: %s (%s)", fname, heading_family)

    for fname in body_files:
        path = os.path.join(FONTS_DIR, fname)
        if os.path.isfile(path):
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id != -1:
                fams = QFontDatabase.applicationFontFamilies(font_id)
                if fams:
                    body_family = fams[0]
                    log.debug("Loaded body font: %s (%s)", fname, body_family)

    _family_heading = heading_family or "Arial"
    _family_body = body_family or "Arial"
    _loaded = True
    log.info("Brand fonts loaded: headings=%s, body=%s",
             _family_heading, _family_body)


def heading_family() -> str:
    return _family_heading


def body_family() -> str:
    return _family_body


def heading_font(size: int, weight: QFont.Weight = QFont.Weight.Bold) -> QFont:
    """Заголовочный Unbounded."""
    f = QFont(_family_heading, size)
    f.setWeight(weight)
    return f


def body_font(size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    """Текстовый Inter."""
    f = QFont(_family_body, size)
    f.setWeight(weight)
    return f


# ─── Global stylesheet ───────────────────────────────────────────────────────

def app_stylesheet() -> str:
    """QSS с применённым брендом.

    Важно: НЕ задаём font-size в QWidget, чтобы per-widget QFont.setPointSize
    корректно применялся (CSS font-size в QSS имеет приоритет над QFont).
    """
    return f"""
        QWidget {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
            font-family: '{_family_body}', 'Inter', Arial, sans-serif;
        }}
        QScrollArea, QScrollArea > QWidget > QWidget {{
            background-color: {COLOR_BG};
            border: none;
        }}
        QScrollBar:vertical {{
            background: {COLOR_BG};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {COLOR_BORDER};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLOR_GOLD};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
    """


def button_primary_qss() -> str:
    """Чёрная кнопка с золотым hover — как на сайте."""
    return f"""
        QPushButton {{
            background: {COLOR_TEXT};
            color: {COLOR_BG};
            border: none;
            border-radius: 24px;
            padding: 12px 28px;
            font-family: '{_family_heading}';
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{
            background: {COLOR_GOLD_DARK};
            color: white;
        }}
        QPushButton:pressed {{
            background: {COLOR_GOLD};
        }}
    """


def button_ghost_qss() -> str:
    """Полупрозрачная кнопка с рамкой."""
    return f"""
        QPushButton {{
            background: transparent;
            color: {COLOR_TEXT};
            border: 1px solid {COLOR_BORDER};
            border-radius: 24px;
            padding: 10px 24px;
            font-family: '{_family_body}';
            font-weight: 500;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background: {COLOR_HOVER};
            border-color: {COLOR_TEXT};
        }}
    """
