"""
card_widget.py — Карточка товара в стилистике goldapple.ru.

Белый тайл со скруглёнными углами, тонкой рамкой, акцентной полоской
рарности наверху и выдержанной типографикой.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

from utils.theme import (
    heading_family, body_family,
    COLOR_BG_CARD, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER,
    RARITY_COLORS_HEX,
)


class CardWidget(QWidget):
    """220×320 карточка с акцент-полоской сверху."""

    CARD_W = 220
    CARD_H = 320

    def __init__(self, product_name: str, rarity: str,
                 pixmap: QPixmap | None = None,
                 discount_value: int = 0,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.product_name = product_name
        self.rarity = rarity
        self.discount_value = discount_value
        self._pixmap = pixmap

        self._accent = QColor(
            RARITY_COLORS_HEX.get(rarity, RARITY_COLORS_HEX["Common"])
        )

        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._build_layout()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 22, 14, 16)
        layout.setSpacing(6)

        # Rarity label
        rarity_lbl = QLabel(self.rarity.upper())
        rf = QFont(heading_family(), 9)
        rf.setWeight(QFont.Weight.Bold)
        rf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        rarity_lbl.setFont(rf)
        rarity_lbl.setStyleSheet(
            f"color: {self._accent.name()}; background: transparent;"
        )
        rarity_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(rarity_lbl)

        # Изображение
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setStyleSheet("background: transparent;")
        if self._pixmap and not self._pixmap.isNull():
            img_label.setPixmap(
                self._pixmap.scaled(
                    self.CARD_W - 40, 180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            img_label.setText("◯")
            img_label.setStyleSheet(
                f"color: {COLOR_BORDER}; font-size: 72px;"
            )
        layout.addWidget(img_label, stretch=1)

        # Название
        name_label = QLabel(self.product_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        nf = QFont(body_family(), 11)
        nf.setWeight(QFont.Weight.Medium)
        name_label.setFont(nf)
        name_label.setStyleSheet(
            f"color: {COLOR_TEXT}; background: transparent;"
        )
        name_label.setMinimumHeight(32)
        layout.addWidget(name_label)

        # Скидка
        if self.discount_value > 0:
            disc = QLabel(f"−{self.discount_value}%")
            df = QFont(heading_family(), 11)
            df.setWeight(QFont.Weight.Bold)
            disc.setFont(df)
            disc.setStyleSheet(
                f"color: {self._accent.name()}; background: transparent;"
            )
            disc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(disc)

    # ── Кастомная отрисовка: тайл + акцент-полоска сверху ────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Белый фон-тайл
        painter.setBrush(QColor(COLOR_BG_CARD))
        painter.setPen(QPen(QColor(COLOR_BORDER), 1))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 16, 16)

        # Верхняя акцент-полоска
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._accent)
        painter.drawRect(16, 0, self.CARD_W - 32, 4)

        painter.end()
        super().paintEvent(event)
