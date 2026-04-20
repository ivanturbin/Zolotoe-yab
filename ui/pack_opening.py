"""
pack_opening.py — Экран открытия набора.

Карты появляются СТРОГО ПО ОЧЕРЕДИ: каждая ждёт окончания
предыдущей анимации через .finished → callback, а не по
фиксированному таймеру. Между карт — короткая пауза.

Каждая карта получает анимацию по СВОЕЙ рарности:
  Common    → fade
  Rare      → slide-up + fade
  Epic      → pop + пурпурный glow pulse
  Legendary → pop + золотой glow (двойной pulse)
"""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)

from core.pack_system import Card, PackResult
from core.duplicate_system import DiscountReward
from ui.card_widget import CardWidget
from animation.animation_manager import animate_pack_opening, reveal_card
from utils.config import PACK_TYPES
from utils.theme import (
    heading_family, body_family, body_font,
    COLOR_BG, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_GOLD,
    COLOR_BORDER, COLOR_HOVER,
)

# Пауза между окончанием анимации одной карты и стартом следующей
INTER_CARD_PAUSE_MS = 180


class _CardSlot(QWidget):
    """Wrapper фиксированного размера, внутри которого карта позиционируется
    абсолютно — это нужно чтобы QPropertyAnimation на 'pos' работала
    (в QHBoxLayout layout-менеджер перехватывал бы setPos)."""

    def __init__(self, card_widget: CardWidget,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(card_widget.CARD_W, card_widget.CARD_H)
        self.setStyleSheet("background: transparent;")
        self.card = card_widget
        self.card.setParent(self)
        self.card.move(0, 0)
        self.card.setVisible(False)


class PackOpeningScreen(QWidget):
    """Проигрывает анимацию пака и последовательно раскрывает карточки."""

    go_back = pyqtSignal()

    def __init__(self, asset_loader, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._assets = asset_loader
        self._slots: List[_CardSlot] = []
        self._rarities: List[str] = []
        self._reveal_index = 0
        self._build()

    # ── public ────────────────────────────────────────────────────────────

    def show_result(self, result: PackResult,
                    rewards: List[DiscountReward]) -> None:
        """Запускает последовательный reveal для результата."""
        self._clear_cards()

        label = result.pack_type.replace(" Pack", "").upper()
        self._title.setText(label)
        self._rewards_label.setText("")

        cfg = PACK_TYPES.get(result.pack_type, {})
        self._assets.play_sound(cfg.get("sound", ""))

        # Создаём slot'ы с картами (карты изначально скрыты)
        for card in result.cards:
            pix = self._assets.get_card_texture(
                card.rarity, card.product_id, image_path=card.image
            )
            cw = CardWidget(
                product_name=card.product_name,
                rarity=card.rarity,
                pixmap=pix,
                discount_value=card.discount_value,
            )
            slot = _CardSlot(cw)
            self._cards_row.addWidget(slot, alignment=Qt.AlignmentFlag.AlignCenter)
            self._slots.append(slot)
            self._rarities.append(card.rarity)

        # Готовим отложенный показ наград (считаем когда последняя анимация закончится)
        self._pending_rewards = rewards

        # Сначала — анимация самого пака, потом цепочка reveal'ов
        animate_pack_opening(
            result.pack_type, self._pack_container,
            on_complete=self._start_card_reveal,
        )

    # ── internal ──────────────────────────────────────────────────────────

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 30, 60, 40)
        outer.setSpacing(0)

        # Назад
        top = QHBoxLayout()
        back = QPushButton("←  К выбору набора")
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

        outer.addSpacing(20)

        # Заголовок типа пака
        self._title = QLabel()
        f = QFont(heading_family(), 42)
        f.setWeight(QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.5)
        self._title.setFont(f)
        self._title.setStyleSheet(f"color: {COLOR_TEXT};")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self._title)

        # Контейнер анимации пака
        self._pack_container = QLabel("◉")
        self._pack_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pack_container.setStyleSheet(
            f"color: {COLOR_GOLD}; font-size: 72px;"
        )
        self._pack_container.setFixedHeight(100)
        outer.addWidget(self._pack_container)

        outer.addSpacing(20)

        # Ряд карт (slot'ы)
        self._cards_row = QHBoxLayout()
        self._cards_row.setSpacing(18)
        self._cards_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addLayout(self._cards_row)

        outer.addSpacing(30)

        # Бейдж с вознаграждениями
        self._rewards_label = QLabel()
        self._rewards_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rf = QFont(body_family(), 13)
        rf.setWeight(QFont.Weight.Medium)
        self._rewards_label.setFont(rf)
        self._rewards_label.setStyleSheet(
            f"color: {COLOR_GOLD}; padding: 8px 20px;"
        )
        outer.addWidget(self._rewards_label)

        outer.addStretch()

    def _start_card_reveal(self) -> None:
        """Запуск последовательного раскрытия."""
        self._reveal_index = 0
        self._reveal_next()

    def _reveal_next(self) -> None:
        """Раскрывает очередную карту и по окончании её анимации
        планирует показ следующей."""
        if self._reveal_index >= len(self._slots):
            self._on_all_revealed()
            return

        slot = self._slots[self._reveal_index]
        rarity = self._rarities[self._reveal_index]

        def _after_this_card():
            # Короткая пауза между картами, потом следующая
            self._reveal_index += 1
            QTimer.singleShot(INTER_CARD_PAUSE_MS, self._reveal_next)

        reveal_card(rarity, slot.card, on_done=_after_this_card)

    def _on_all_revealed(self) -> None:
        """Показываем плашку с наградами после завершения всех reveal'ов."""
        if self._pending_rewards:
            lines = [r.label() for r in self._pending_rewards]
            self._rewards_label.setText("✦ " + " • ".join(lines))

    def _clear_cards(self) -> None:
        for slot in self._slots:
            slot.setParent(None)
            slot.deleteLater()
        self._slots.clear()
        self._rarities.clear()
