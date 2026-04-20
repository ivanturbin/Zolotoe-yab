"""
pack_system.py — Manages pack types and the card-drawing pipeline.

A Pack holds a type definition; calling ``open()`` rolls rarities via the
ProbabilitySystem, then picks concrete cards from the card database.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from utils.config import CARDS_JSON, PACK_TYPES
from utils.logger import get_logger
from core.probability_system import ProbabilitySystem

log = get_logger(__name__)


@dataclass
class Card:
    """Runtime representation of a single card."""
    product_id: str
    product_name: str
    brand: str
    category: str
    rarity: str
    image: str
    discount_value: int

    def key(self) -> str:
        """Unique identity string for duplicate detection."""
        return self.product_id


@dataclass
class PackResult:
    """What the player gets when they open a pack."""
    pack_type: str
    cards: List[Card] = field(default_factory=list)


class PackSystem:
    """Loads card database and opens packs."""

    def __init__(self, probability_system: ProbabilitySystem) -> None:
        self.prob = probability_system
        # card_pool[rarity] = [Card, ...]
        self.card_pool: Dict[str, List[Card]] = {}
        self._load_card_database()

    # ── public ────────────────────────────────────────────────────────────

    def open_pack(self, pack_type: str) -> PackResult:
        """Open a pack and return a ``PackResult`` with drawn cards."""
        cfg = PACK_TYPES.get(pack_type)
        if cfg is None:
            log.error("Unknown pack type '%s'.", pack_type)
            return PackResult(pack_type=pack_type)

        count = cfg["cards_count"]
        rarities = self.prob.roll_rarities(pack_type, count)

        cards: List[Card] = []
        for rarity in rarities:
            card = self._pick_card(rarity)
            if card:
                cards.append(card)
        log.info("Opened %s → %d cards.", pack_type, len(cards))
        return PackResult(pack_type=pack_type, cards=cards)

    # ── internal ──────────────────────────────────────────────────────────

    def _pick_card(self, rarity: str) -> Optional[Card]:
        pool = self.card_pool.get(rarity)
        if not pool:
            log.warning("No cards in pool for rarity '%s'.", rarity)
            # Try to fall back to Common
            pool = self.card_pool.get("Common", [])
        if not pool:
            return None
        return random.choice(pool)

    def _load_card_database(self) -> None:
        try:
            with open(CARDS_JSON, "r", encoding="utf-8") as fh:
                raw: List[dict] = json.load(fh)
            for entry in raw:
                card = Card(
                    product_id=entry["product_id"],
                    product_name=entry["product_name"],
                    brand=entry.get("brand", "Golden Apple"),
                    category=entry.get("category", ""),
                    rarity=entry["rarity"],
                    image=entry.get("image", ""),
                    discount_value=entry.get("discount_value", 0),
                )
                self.card_pool.setdefault(card.rarity, []).append(card)
            total = sum(len(v) for v in self.card_pool.values())
            log.info("Card database loaded: %d cards across %d rarities.",
                     total, len(self.card_pool))
        except FileNotFoundError:
            log.error("Card database not found at %s.", CARDS_JSON)
        except (json.JSONDecodeError, KeyError) as exc:
            log.error("Broken card database: %s", exc)
