"""
rarity_system.py — Defines rarity tiers and their visual / gameplay properties.

Provides helpers to query glow colours, animation intensities, and
discount multipliers without scattering magic values around the codebase.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from utils.config import RARITIES
from utils.logger import get_logger

log = get_logger(__name__)

# Canonical ordering from lowest to highest
RARITY_ORDER: List[str] = ["Common", "Rare", "Epic", "Legendary"]


@dataclass(frozen=True)
class RarityInfo:
    """Immutable description of a single rarity tier."""
    name: str
    glow_color: str
    animation_intensity: float
    discount_multiplier: float

    @property
    def tier_index(self) -> int:
        """0-based tier index (Common=0 … Legendary=3)."""
        try:
            return RARITY_ORDER.index(self.name)
        except ValueError:
            return -1


class RaritySystem:
    """Registry of all rarity tiers built from config."""

    def __init__(self) -> None:
        self._tiers: Dict[str, RarityInfo] = {}
        self._build()

    def _build(self) -> None:
        for name, props in RARITIES.items():
            self._tiers[name] = RarityInfo(
                name=name,
                glow_color=props["glow_color"],
                animation_intensity=props["animation_intensity"],
                discount_multiplier=props["discount_multiplier"],
            )
        log.info("RaritySystem initialised with %d tiers.", len(self._tiers))

    def get(self, rarity: str) -> RarityInfo:
        """Return RarityInfo for *rarity*; defaults to Common if unknown."""
        info = self._tiers.get(rarity)
        if info is None:
            log.warning("Unknown rarity '%s' — falling back to Common.", rarity)
            info = self._tiers["Common"]
        return info

    @property
    def all_tiers(self) -> List[RarityInfo]:
        return [self._tiers[r] for r in RARITY_ORDER if r in self._tiers]
