"""
animation_manager.py — High-level animation dispatcher.

The UI calls ``animate_pack_opening(pack_type, widget, callback)``
and this module picks the right choreography.
"""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtWidgets import QWidget

from animation.pack_animations import (
    play_common_animation,
    play_epic_animation,
    play_legendary_animation,
)
from animation.card_animations import reveal_card  # re-export
from utils.logger import get_logger

log = get_logger(__name__)

_PACK_ANIM_MAP = {
    "Common Pack":    play_common_animation,
    "Epic Pack":      play_epic_animation,
    "Legendary Pack": play_legendary_animation,
}


def animate_pack_opening(pack_type: str, widget: QWidget,
                         on_complete: Optional[Callable] = None) -> None:
    """Play the animation sequence matching *pack_type*."""
    fn = _PACK_ANIM_MAP.get(pack_type, play_common_animation)
    log.debug("Playing %s animation.", pack_type)
    fn(widget, on_complete)
