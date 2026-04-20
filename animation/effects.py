"""
effects.py — Reusable visual effects: glow, flash, shake, sparkle.

Each effect is a callable that modifies a QWidget's paint or geometry
over time using QPropertyAnimation or QTimeLine.

IMPORTANT: all animations are parented to the target widget or stored in
``widget._ga_anims`` to prevent premature garbage collection.
"""

from __future__ import annotations

import random
from typing import Optional

from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint, QTimer,
    QSequentialAnimationGroup,
)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


def _keep(widget: QWidget, obj: object) -> None:
    """Store *obj* on *widget* so the GC doesn't destroy it mid-flight."""
    if not hasattr(widget, "_ga_anims"):
        widget._ga_anims = []
    widget._ga_anims.append(obj)


def fade_in(widget: QWidget, duration_ms: int = 400,
            callback: Optional[callable] = None) -> QPropertyAnimation:
    """Animate widget opacity from 0 → 1."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    if callback:
        anim.finished.connect(callback)
    _keep(widget, anim)
    _keep(widget, effect)
    anim.start()
    return anim


def glow_pulse(widget: QWidget, duration_ms: int = 500,
               loops: int = 2) -> QPropertyAnimation:
    """Pulse opacity between 0.4 and 1.0 to mimic a glow."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(0.4)
    anim.setEndValue(1.0)
    anim.setLoopCount(loops)
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    _keep(widget, anim)
    _keep(widget, effect)
    anim.start()
    return anim


def screen_shake(widget: QWidget, intensity: int = 8,
                 duration_ms: int = 400) -> None:
    """Jitter widget position randomly for *duration_ms*."""
    origin = widget.pos()
    elapsed = {"t": 0}
    interval = 30  # ms per frame

    timer = QTimer(widget)

    def _tick():
        elapsed["t"] += interval
        if elapsed["t"] >= duration_ms:
            timer.stop()
            widget.move(origin)
            return
        dx = random.randint(-intensity, intensity)
        dy = random.randint(-intensity, intensity)
        widget.move(origin + QPoint(dx, dy))

    timer.timeout.connect(_tick)
    _keep(widget, timer)
    timer.start(interval)


def golden_flash(widget: QWidget, duration_ms: int = 800) -> None:
    """Quick flash: opacity 0→1→0 with gold-tinted overlay."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    group = QSequentialAnimationGroup(widget)

    fade_up = QPropertyAnimation(effect, b"opacity")
    fade_up.setDuration(duration_ms // 2)
    fade_up.setStartValue(0.0)
    fade_up.setEndValue(1.0)
    fade_up.setEasingCurve(QEasingCurve.Type.OutQuad)

    fade_down = QPropertyAnimation(effect, b"opacity")
    fade_down.setDuration(duration_ms // 2)
    fade_down.setStartValue(1.0)
    fade_down.setEndValue(0.0)
    fade_down.setEasingCurve(QEasingCurve.Type.InQuad)

    group.addAnimation(fade_up)
    group.addAnimation(fade_down)
    _keep(widget, group)
    _keep(widget, effect)
    group.start()
