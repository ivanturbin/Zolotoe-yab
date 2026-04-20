"""
collection_screen.py — Сетка всех собранных карточек, разбитая по рарности.

Стилистика goldapple.ru: светлый фон, минималистичная типографика,
цветные акценты по рарности.
"""

from __future__ import annotations

from typing import Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout,
)

from core.rarity_system import RARITY_ORDER
from ui.card_widget import CardWidget
from utils.theme import (
    heading_family, body_family, body_font,
    COLOR_BG, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER,
    COLOR_HOVER, RARITY_COLORS_HEX,
)


class CollectionScreen(QWidget):
    """Сетка карточек с секциями по рарности."""

    go_back = pyqtSignal()

    def __init__(self, asset_loader, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._assets = asset_loader
        self._build()

    # ── public ────────────────────────────────────────────────────────────

    def refresh(self, card_counts: Dict[str, int],
                card_meta: list[dict]) -> None:
        # Безопасная очистка grid: takeAt атомарно удаляет item из layout
        # и возвращает его — без риска с dangling pointers.
        while True:
            item = self._grid.takeAt(0)
            if item is None:
                break
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        meta_map = {m["product_id"]: m for m in card_meta}
        row = 0
        total_owned = sum(1 for pid, c in card_counts.items() if c > 0)
        self._meta_label.setText(f"{total_owned} уникальных позиций")

        if total_owned == 0:
            empty = QLabel("Коллекция пока пуста.\nОткройте свой первый набор.")
            empty.setFont(body_font(14))
            empty.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; padding: 60px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid.addWidget(empty, 0, 0, 1, 4)
            return

        for rarity in RARITY_ORDER:
            cards_in_rarity = [
                (pid, count, meta_map[pid])
                for pid, count in card_counts.items()
                if pid in meta_map
                and meta_map[pid].get("rarity") == rarity
                and count > 0
            ]
            if not cards_in_rarity:
                continue

            header = QLabel(f"{rarity.upper()}  ·  {len(cards_in_rarity)}")
            hf = QFont(heading_family(), 14)
            hf.setWeight(QFont.Weight.Bold)
            hf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
            header.setFont(hf)
            header.setStyleSheet(
                f"color: {RARITY_COLORS_HEX[rarity]}; "
                "padding: 24px 0 12px 4px;"
            )
            self._grid.addWidget(header, row, 0, 1, 4)
            row += 1

            col = 0
            for pid, count, meta in cards_in_rarity:
                try:
                    pix = self._assets.get_card_texture(
                        rarity, pid, image_path=meta.get("image", "")
                    )
                    cw = CardWidget(
                        product_name=meta.get("product_name", pid),
                        rarity=rarity,
                        pixmap=pix,
                        discount_value=meta.get("discount_value", 0),
                    )
                except Exception as exc:  # защита от битых данных
                    continue

                if count > 1:
                    badge = QLabel(f"×{count}", cw)
                    bf = QFont(heading_family(), 10)
                    bf.setWeight(QFont.Weight.Bold)
                    badge.setFont(bf)
                    badge.setStyleSheet(
                        f"background: {COLOR_TEXT}; color: white; "
                        "border-radius: 11px; padding: 3px 8px;"
                    )
                    badge.adjustSize()
                    badge.move(cw.CARD_W - badge.width() - 8, 8)
                    badge.show()

                self._grid.addWidget(cw, row, col)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
            if col != 0:
                row += 1

    # ── internal ──────────────────────────────────────────────────────────

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(80, 40, 80, 40)
        outer.setSpacing(0)

        # Верхняя панель
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
        title = QLabel("КОЛЛЕКЦИЯ")
        f = QFont(heading_family(), 42)
        f.setWeight(QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.5)
        title.setFont(f)
        title.setStyleSheet(f"color: {COLOR_TEXT};")
        outer.addWidget(title)

        self._meta_label = QLabel()
        self._meta_label.setFont(body_font(13))
        self._meta_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        outer.addWidget(self._meta_label)

        outer.addSpacing(10)

        # Сетка
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        container.setStyleSheet(f"background: {COLOR_BG};")
        self._grid = QGridLayout(container)
        self._grid.setSpacing(18)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(container)
        outer.addWidget(scroll, stretch=1)
