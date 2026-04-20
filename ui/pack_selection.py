"""
pack_selection.py — Экран выбора набора.

Три пака представлены как «товарные карточки» в стилистике сайта:
белые тайлы с изображением, названием, количеством карт и CTA-кнопкой.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)

from utils.config import PACK_TYPES
from utils.theme import (
    heading_font, body_font, heading_family, body_family,
    COLOR_BG, COLOR_BG_CARD, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_GOLD, COLOR_BORDER, COLOR_HOVER,
    button_primary_qss,
)


class PackTile(QFrame):
    """Карточка пака в духе сайта — белый тайл с рамкой."""

    clicked = pyqtSignal(str)

    def __init__(self, pack_type: str, pixmap: QPixmap | None = None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.pack_type = pack_type
        self.setFixedSize(260, 420)

        self.setStyleSheet(f"""
            PackTile {{
                background: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 20px;
            }}
            PackTile:hover {{
                border-color: {COLOR_TEXT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 28, 20, 24)
        layout.setSpacing(12)

        # Превью пака
        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setFixedHeight(220)
        img.setStyleSheet("background: transparent;")
        if pixmap and not pixmap.isNull():
            img.setPixmap(pixmap.scaled(
                200, 220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        else:
            img.setText("◉")
            img.setStyleSheet(f"color: {COLOR_GOLD}; font-size: 96px;")
        layout.addWidget(img)

        # Название
        name = QLabel(pack_type.replace(" Pack", "").upper())
        f = QFont(heading_family(), 18)
        f.setWeight(QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        name.setFont(f)
        name.setStyleSheet(f"color: {COLOR_TEXT}; background: transparent;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        # Мета
        cfg = PACK_TYPES.get(pack_type, {})
        meta = QLabel(f"{cfg.get('cards_count', '?')} карт в наборе")
        meta.setFont(body_font(12))
        meta.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(meta)

        layout.addStretch()

        # CTA
        btn = QPushButton("Открыть")
        btn.setFixedHeight(42)
        btn.setStyleSheet(button_primary_qss())
        btn.clicked.connect(lambda: self.clicked.emit(self.pack_type))
        layout.addWidget(btn)


class PackSelectionScreen(QWidget):
    """Горизонтальный ряд из трёх тайлов-паков."""

    pack_chosen = pyqtSignal(str)
    go_back = pyqtSignal()

    def __init__(self, asset_loader, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._assets = asset_loader
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(80, 40, 80, 40)
        outer.setSpacing(0)

        # Шапка с кнопкой «назад» слева
        top = QHBoxLayout()
        back = QPushButton("←  Меню")
        back.setFixedHeight(40)
        back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_BORDER};
                border-radius: 20px;
                padding: 8px 20px;
                font-family: '{body_family()}';
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {COLOR_HOVER};
                border-color: {COLOR_TEXT};
            }}
        """)
        back.clicked.connect(self.go_back.emit)
        top.addWidget(back)
        top.addStretch()
        outer.addLayout(top)

        outer.addSpacing(40)

        # Заголовок секции
        title = QLabel("ВЫБЕРИ НАБОР")
        f = QFont(heading_family(), 42)
        f.setWeight(QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        title.setFont(f)
        title.setStyleSheet(f"color: {COLOR_TEXT};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(title)

        sub = QLabel("каждый пак — это шанс получить редкую находку")
        sub.setFont(body_font(14))
        sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(sub)

        outer.addSpacing(40)

        # Тайлы
        row = QHBoxLayout()
        row.setSpacing(24)
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for pack_type, cfg in PACK_TYPES.items():
            pix = self._assets.get_pack_image(cfg["image"])
            tile = PackTile(pack_type, pix)
            tile.clicked.connect(self.pack_chosen.emit)
            row.addWidget(tile)
        outer.addLayout(row)

        outer.addStretch()
