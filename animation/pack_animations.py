"""
pack_animations.py — Per-pack-type animation choreography.

Each function takes a widget (the pack / card container) and runs the
appropriate sequence of effects, calling *on_complete* when done.
"""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget

from animation.effects import fade_in, glow_pulse, screen_shake, golden_flash
from utils.config import (
    ANIM_COMMON_FADE_MS, ANIM_COMMON_SPARKLE_MS,
    ANIM_EPIC_ROTATION_MS, ANIM_EPIC_GLOW_PULSE_MS,
    ANIM_LEGENDARY_FLASH_MS, ANIM_LEGENDARY_SHAKE_MS,
    ANIM_LEGENDARY_REVEAL_MS,
)


def play_common_animation(widget: QWidget,
                          on_complete: Optional[Callable] = None) -> None:
    """Fast fade + light sparkle, then callback."""
    def _after_fade():
        glow_pulse(widget, ANIM_COMMON_SPARKLE_MS, loops=1)
        if on_complete:
            QTimer.singleShot(ANIM_COMMON_SPARKLE_MS, on_complete)

    fade_in(widget, ANIM_COMMON_FADE_MS, callback=_after_fade)


def play_epic_animation(widget: QWidget,
                        on_complete: Optional[Callable] = None) -> None:
    """Glow pulse → fade in, then callback."""
    glow_pulse(widget, ANIM_EPIC_GLOW_PULSE_MS, loops=2)
    total_pulse = ANIM_EPIC_GLOW_PULSE_MS * 2

    def _after_pulse():
        fade_in(widget, ANIM_EPIC_ROTATION_MS, callback=on_complete)

    QTimer.singleShot(total_pulse, _after_pulse)


def play_legendary_animation(widget: QWidget,
                             on_complete: Optional[Callable] = None) -> None:
    """Golden flash → screen shake → slow reveal, then callback."""
    golden_flash(widget, ANIM_LEGENDARY_FLASH_MS)

    def _do_shake():
        screen_shake(widget, intensity=12, duration_ms=ANIM_LEGENDARY_SHAKE_MS)

    def _do_reveal():
        fade_in(widget, ANIM_LEGENDARY_REVEAL_MS, callback=on_complete)

    QTimer.singleShot(ANIM_LEGENDARY_FLASH_MS, _do_shake)
    QTimer.singleShot(ANIM_LEGENDARY_FLASH_MS + ANIM_LEGENDARY_SHAKE_MS,
                      _do_reveal)
