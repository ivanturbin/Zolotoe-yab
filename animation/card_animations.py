"""
card_animations.py — Анимации появления карточек по рарности.

Каждая функция:
  • делает widget видимым,
  • запускает анимацию,
  • вызывает on_done() когда ПОЛНОСТЬЮ завершилась.

Контракт on_done — именно полное завершение, чтобы внешний код
мог выстраивать последовательные reveal'ы (chain через finished).

Важно: анимации position (QPropertyAnimation на "pos") работают только
если виджет находится в контейнере без layout (wrapper с абсолютным
позиционированием). См. pack_opening.py → _build_card_wrapper().
"""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint, QTimer,
    QParallelAnimationGroup, QSequentialAnimationGroup,
)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
)

from animation.effects import _keep
from utils.theme import RARITY_COLORS_HEX


# ─── Длительности по рарности (ms) ───────────────────────────────────────────

DURATION = {
    "Common":    400,
    "Rare":      550,
    "Epic":      750,
    "Legendary": 1100,
}


def _safe_done(on_done: Optional[Callable]) -> Callable:
    """on_done может быть None — возвращаем noop."""
    return on_done if on_done else (lambda: None)


# ─── Common: простой fade ────────────────────────────────────────────────────

def reveal_common(widget: QWidget, on_done: Optional[Callable] = None) -> None:
    widget.setVisible(True)

    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)

    fade = QPropertyAnimation(effect, b"opacity", widget)
    fade.setDuration(DURATION["Common"])
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
    fade.finished.connect(_safe_done(on_done))

    _keep(widget, fade)
    _keep(widget, effect)
    fade.start()


# ─── Rare: slide-up + fade ───────────────────────────────────────────────────

def reveal_rare(widget: QWidget, on_done: Optional[Callable] = None) -> None:
    widget.setVisible(True)

    origin = widget.pos()
    start = QPoint(origin.x(), origin.y() + 40)
    widget.move(start)

    # Fade
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)
    fade = QPropertyAnimation(effect, b"opacity", widget)
    fade.setDuration(DURATION["Rare"])
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    # Slide
    slide = QPropertyAnimation(widget, b"pos", widget)
    slide.setDuration(DURATION["Rare"])
    slide.setStartValue(start)
    slide.setEndValue(origin)
    slide.setEasingCurve(QEasingCurve.Type.OutCubic)

    group = QParallelAnimationGroup(widget)
    group.addAnimation(fade)
    group.addAnimation(slide)
    group.finished.connect(_safe_done(on_done))

    _keep(widget, group)
    _keep(widget, effect)
    group.start()


# ─── Epic: pop-up + glow pulse ───────────────────────────────────────────────

def reveal_epic(widget: QWidget, on_done: Optional[Callable] = None) -> None:
    """Карта выезжает снизу с overshoot, затем получает пурпурный glow."""
    widget.setVisible(True)

    origin = widget.pos()
    start = QPoint(origin.x(), origin.y() + 70)
    widget.move(start)

    # Фаза 1: slide-up + fade (550ms)
    fade_effect = QGraphicsOpacityEffect(widget)
    fade_effect.setOpacity(0.0)
    widget.setGraphicsEffect(fade_effect)

    fade = QPropertyAnimation(fade_effect, b"opacity", widget)
    fade.setDuration(550)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    slide = QPropertyAnimation(widget, b"pos", widget)
    slide.setDuration(550)
    slide.setStartValue(start)
    slide.setEndValue(origin)
    slide.setEasingCurve(QEasingCurve.Type.OutBack)

    phase1 = QParallelAnimationGroup(widget)
    phase1.addAnimation(fade)
    phase1.addAnimation(slide)

    def _phase2():
        # Фаза 2: замена opacity-effect на drop-shadow glow
        glow = QGraphicsDropShadowEffect(widget)
        glow.setColor(QColor(RARITY_COLORS_HEX["Epic"]))
        glow.setOffset(0, 0)
        glow.setBlurRadius(0)
        widget.setGraphicsEffect(glow)

        pulse = QPropertyAnimation(glow, b"blurRadius", widget)
        pulse.setDuration(200)
        pulse.setStartValue(0.0)
        pulse.setKeyValueAt(0.5, 35.0)
        pulse.setEndValue(0.0)
        pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        pulse.finished.connect(_safe_done(on_done))

        _keep(widget, pulse)
        _keep(widget, glow)
        pulse.start()

    phase1.finished.connect(_phase2)
    _keep(widget, phase1)
    _keep(widget, fade_effect)
    phase1.start()


# ─── Legendary: золотая вспышка + pop + продолжительный glow pulse ───────────

def reveal_legendary(widget: QWidget,
                     on_done: Optional[Callable] = None) -> None:
    widget.setVisible(True)

    origin = widget.pos()
    start = QPoint(origin.x(), origin.y() + 90)
    widget.move(start)

    # Фаза 1: slow fade + slide с overshoot (700ms)
    fade_effect = QGraphicsOpacityEffect(widget)
    fade_effect.setOpacity(0.0)
    widget.setGraphicsEffect(fade_effect)

    fade = QPropertyAnimation(fade_effect, b"opacity", widget)
    fade.setDuration(700)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    slide = QPropertyAnimation(widget, b"pos", widget)
    slide.setDuration(700)
    slide.setStartValue(start)
    slide.setEndValue(origin)
    slide.setEasingCurve(QEasingCurve.Type.OutBack)

    phase1 = QParallelAnimationGroup(widget)
    phase1.addAnimation(fade)
    phase1.addAnimation(slide)

    def _phase2():
        # Фаза 2: золотой glow — двойной pulse (400ms)
        glow = QGraphicsDropShadowEffect(widget)
        glow.setColor(QColor(RARITY_COLORS_HEX["Legendary"]))
        glow.setOffset(0, 0)
        glow.setBlurRadius(0)
        widget.setGraphicsEffect(glow)

        pulse = QPropertyAnimation(glow, b"blurRadius", widget)
        pulse.setDuration(400)
        pulse.setStartValue(0.0)
        pulse.setKeyValueAt(0.25, 50.0)
        pulse.setKeyValueAt(0.5, 15.0)
        pulse.setKeyValueAt(0.75, 50.0)
        pulse.setEndValue(20.0)
        pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        pulse.finished.connect(_safe_done(on_done))

        _keep(widget, pulse)
        _keep(widget, glow)
        pulse.start()

    phase1.finished.connect(_phase2)
    _keep(widget, phase1)
    _keep(widget, fade_effect)
    phase1.start()


# ─── Dispatcher ──────────────────────────────────────────────────────────────

_MAP = {
    "Common":    reveal_common,
    "Rare":      reveal_rare,
    "Epic":      reveal_epic,
    "Legendary": reveal_legendary,
}


def reveal_card(rarity: str, widget: QWidget,
                on_done: Optional[Callable] = None) -> None:
    """Выбирает нужную анимацию по рарности и вызывает её."""
    fn = _MAP.get(rarity, reveal_common)
    fn(widget, on_done)
