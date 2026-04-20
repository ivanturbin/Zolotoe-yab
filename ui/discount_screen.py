"""
discount_screen.py — Экран активных скидок.

Чистые белые тайлы в списке, крупная цифра процента как акцент.
"""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame,
)

from utils.theme import (
    heading_family, body_family, body_font,
    COLOR_BG, COLOR_BG_CARD, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_BORDER, COLOR_HOVER, RARITY_COLORS_HEX,
)


class DiscountTile(QFrame):
    """Большая горизонтальная плашка скидки."""

    TILE_H = 104

    def __init__(self, discount: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        rarity = discount.get("rarity", "Common")
        accent = RARITY_COLORS_HEX.get(rarity, RARITY_COLORS_HEX["Common"])
        pct = discount.get("discount_percent", 0)
        name = discount.get("product_name", "???")

        self.setStyleSheet(f"""
            DiscountTile {{
                background: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 16px;
            }}
        """)
        # Фиксируем высоту — чтобы плашка не растягивалась вертикально
        self.setFixedHeight(self.TILE_H)

        row = QHBoxLayout(self)
        row.setContentsMargins(28, 18, 28, 18)
        row.setSpacing(24)

        # Крупный процент — достаточная ширина для "−25%" в Unbounded Black
        pct_label = QLabel(f"−{pct}%")
        pf = QFont(heading_family(), 34)
        pf.setWeight(QFont.Weight.Black)
        pct_label.setFont(pf)
        pct_label.setStyleSheet(f"color: {accent}; background: transparent;")
        # минимальная ширина под длинные значения вроде "−25%"
        pct_label.setMinimumWidth(140)
        pct_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        row.addWidget(pct_label, 0, Qt.AlignmentFlag.AlignVCenter)

        # Инфо (название + рарность)
        info = QVBoxLayout()
        info.setSpacing(4)
        info.setContentsMargins(0, 0, 0, 0)
        prod = QLabel(name)
        nf = QFont(body_family(), 14)
        nf.setWeight(QFont.Weight.Medium)
        prod.setFont(nf)
        prod.setStyleSheet(f"color: {COLOR_TEXT}; background: transparent;")
        info.addWidget(prod)

        rar = QLabel(rarity.upper())
        rf = QFont(heading_family(), 10)
        rf.setWeight(QFont.Weight.Bold)
        rf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        rar.setFont(rf)
        rar.setStyleSheet(f"color: {accent}; background: transparent;")
        info.addWidget(rar)
        # убран info.addStretch() — плашка больше не растягивается
        row.addLayout(info, 1)

        # «Активна» метка
        status = QLabel("активна")
        status.setFont(body_font(12))
        status.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        row.addWidget(status, 0, Qt.AlignmentFlag.AlignVCenter)


class DiscountScreen(QWidget):
    """Список активных скидок игрока."""

    go_back = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build()

    def refresh(self, discounts: List[dict]) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self._count_label.setText(
            f"{len(discounts)} активных" if discounts else "пока нет скидок"
        )

        if not discounts:
            empty = QLabel(
                "Соберите 3 одинаковые карточки —\n"
                "получите персональную скидку."
            )
            empty.setFont(body_font(14))
            empty.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; padding: 60px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
            return

        for d in discounts:
            self._list_layout.addWidget(DiscountTile(d))
        self._list_layout.addStretch()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(80, 40, 80, 40)
        outer.setSpacing(0)

        # Назад
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

        outer.addSpacing(30)

        # Заголовок
        title = QLabel("МОИ СКИДКИ")
        f = QFont(heading_family(), 42)
        f.setWeight(QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.5)
        title.setFont(f)
        title.setStyleSheet(f"color: {COLOR_TEXT};")
        outer.addWidget(title)

        self._count_label = QLabel()
        self._count_label.setFont(body_font(13))
        self._count_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        outer.addWidget(self._count_label)

        outer.addSpacing(24)

        # Скролл-список
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        container.setStyleSheet(f"background: {COLOR_BG};")
        self._list_layout = QVBoxLayout(container)
        self._list_layout.setSpacing(12)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(container)
        outer.addWidget(scroll, stretch=1)
