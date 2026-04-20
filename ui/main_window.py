"""
main_window.py — Главное окно с навигацией между экранами.

Стилистика соответствует сайту goldapple.ru:
  • Кремовый фон, чёрный текст
  • Шрифт Unbounded для заголовков
  • Минимум украшательства, много воздуха
  • Золотые и зелёные акценты
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
)

from core.game_manager import GameManager
from ui.pack_selection import PackSelectionScreen
from ui.pack_opening import PackOpeningScreen
from ui.collection_screen import CollectionScreen
from ui.discount_screen import DiscountScreen
from utils.config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from utils.theme import (
    heading_font, body_font,
    COLOR_BG, COLOR_TEXT, COLOR_GOLD, COLOR_BORDER, COLOR_HOVER,
    button_primary_qss, heading_family, body_family,
)


class MainWindow(QMainWindow):
    """Корневое окно приложения."""

    MENU       = 0
    PACKS      = 1
    OPENING    = 2
    COLLECTION = 3
    DISCOUNTS  = 4

    def __init__(self, game: GameManager) -> None:
        super().__init__()
        self._game = game
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._build_screens()
        self._show_screen(self.MENU)

    # ── построение экранов ────────────────────────────────────────────────

    def _build_screens(self) -> None:
        self._stack.addWidget(self._build_menu())          # 0
        self._pack_sel = PackSelectionScreen(self._game.assets)
        self._pack_sel.pack_chosen.connect(self._on_pack_chosen)
        self._pack_sel.go_back.connect(lambda: self._show_screen(self.MENU))
        self._stack.addWidget(self._pack_sel)              # 1

        self._pack_open = PackOpeningScreen(self._game.assets)
        self._pack_open.go_back.connect(lambda: self._show_screen(self.PACKS))
        self._stack.addWidget(self._pack_open)             # 2

        self._collection = CollectionScreen(self._game.assets)
        self._collection.go_back.connect(lambda: self._show_screen(self.MENU))
        self._stack.addWidget(self._collection)            # 3

        self._discounts = DiscountScreen()
        self._discounts.go_back.connect(lambda: self._show_screen(self.MENU))
        self._stack.addWidget(self._discounts)             # 4

    def _build_menu(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(80, 60, 80, 60)
        outer.setSpacing(0)

        # ── Верхняя навигация (минималистичная шапка) ─────────────────
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 40)

        logo_mark = QLabel("◉")
        logo_mark.setStyleSheet(f"color: {COLOR_GOLD}; font-size: 24px;")

        logo_text = QLabel("ЗОЛОТОЕ ЯБЛОКО")
        f = QFont(heading_family(), 14)
        f.setWeight(QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        logo_text.setFont(f)
        logo_text.setStyleSheet(f"color: {COLOR_TEXT};")

        top_bar.addWidget(logo_mark)
        top_bar.addSpacing(10)
        top_bar.addWidget(logo_text)
        top_bar.addStretch()
        outer.addLayout(top_bar)

        # ── Центральный блок ──────────────────────────────────────────
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.setSpacing(16)

        # Хиро-заголовок
        hero = QLabel("Коллекция\nкрасоты")
        f = QFont(heading_family(), 72)
        f.setWeight(QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 94)
        hero.setFont(f)
        hero.setStyleSheet(f"color: {COLOR_TEXT}; line-height: 0.9;")
        hero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(hero)

        # Подзаголовок
        sub = QLabel("Открывай наборы. Собирай карточки. Получай скидки.")
        sub.setFont(body_font(15))
        sub.setStyleSheet("color: #5a5754;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(sub)

        center.addSpacing(40)

        # CTA кнопки
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cta = QPushButton("Открыть набор")
        cta.setFixedHeight(52)
        cta.setMinimumWidth(200)
        cta.setStyleSheet(button_primary_qss())
        cta.clicked.connect(lambda: self._show_screen(self.PACKS))
        btn_row.addWidget(cta)

        collect_btn = self._secondary_button("Коллекция")
        collect_btn.clicked.connect(lambda: self._show_screen(self.COLLECTION))
        btn_row.addWidget(collect_btn)

        disc_btn = self._secondary_button("Мои скидки")
        disc_btn.clicked.connect(lambda: self._show_screen(self.DISCOUNTS))
        btn_row.addWidget(disc_btn)

        center.addLayout(btn_row)

        outer.addLayout(center)
        outer.addStretch()

        # ── Подвал ────────────────────────────────────────────────────
        footer = QLabel("beauty • perfume • gift")
        footer.setFont(body_font(11))
        footer.setStyleSheet("color: #aaa7a3; letter-spacing: 2px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(footer)

        return page

    def _secondary_button(self, label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(52)
        btn.setMinimumWidth(160)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_BORDER};
                border-radius: 26px;
                padding: 12px 28px;
                font-family: '{body_family()}';
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {COLOR_HOVER};
                border-color: {COLOR_TEXT};
            }}
        """)
        return btn

    # ── навигация ─────────────────────────────────────────────────────────

    def _show_screen(self, index: int) -> None:
        if index == self.COLLECTION:
            counts, meta = self._game.dupes.export_state()
            self._collection.refresh(counts, meta)
        elif index == self.DISCOUNTS:
            self._discounts.refresh(self._game.get_discounts())
        self._stack.setCurrentIndex(index)

    def _on_pack_chosen(self, pack_type: str) -> None:
        result, rewards = self._game.open_pack(pack_type)
        self._show_screen(self.OPENING)
        self._pack_open.show_result(result, rewards)
