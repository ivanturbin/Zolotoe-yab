"""
duplicate_system.py — Tracks card counts and converts triples into discounts.

When a player accumulates DUPLICATE_THRESHOLD copies of the same card,
the extras are consumed and a discount reward is generated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from utils.config import DUPLICATE_THRESHOLD, DUPLICATE_DISCOUNT
from utils.logger import get_logger
from core.pack_system import Card

log = get_logger(__name__)


@dataclass
class DiscountReward:
    """A discount voucher earned from duplicate merging."""
    source_product_id: str
    source_product_name: str
    rarity: str
    discount_percent: int

    def label(self) -> str:
        return f"{self.discount_percent}% скидка ({self.source_product_name})"


class DuplicateSystem:
    """Maintains per-card counts and checks for mergeable duplicates."""

    def __init__(self) -> None:
        # card_counts[product_id] = count
        self.card_counts: Dict[str, int] = {}
        # Stored metadata so we can build DiscountReward later
        self._card_meta: Dict[str, Card] = {}

    # ── public ────────────────────────────────────────────────────────────

    def register_cards(self, cards: List[Card]) -> List[DiscountReward]:
        """Add new cards and return any discount rewards generated."""
        rewards: List[DiscountReward] = []
        for card in cards:
            self.card_counts[card.product_id] = (
                self.card_counts.get(card.product_id, 0) + 1
            )
            self._card_meta[card.product_id] = card

        # Check for merges
        for card in cards:
            reward = self._try_merge(card.product_id)
            if reward:
                rewards.append(reward)
        return rewards

    def get_count(self, product_id: str) -> int:
        return self.card_counts.get(product_id, 0)

    def load_state(self, counts: Dict[str, int], meta_list: List[dict]) -> None:
        """Restore state from save data."""
        self.card_counts = dict(counts)
        for m in meta_list:
            self._card_meta[m["product_id"]] = Card(**m)

    def export_state(self) -> Tuple[Dict[str, int], List[dict]]:
        """Return serialisable state."""
        meta = [
            {
                "product_id": c.product_id,
                "product_name": c.product_name,
                "brand": c.brand,
                "category": c.category,
                "rarity": c.rarity,
                "image": c.image,
                "discount_value": c.discount_value,
            }
            for c in self._card_meta.values()
        ]
        return dict(self.card_counts), meta

    # ── internal ──────────────────────────────────────────────────────────

    def _try_merge(self, product_id: str) -> DiscountReward | None:
        count = self.card_counts.get(product_id, 0)
        if count < DUPLICATE_THRESHOLD:
            return None

        card = self._card_meta.get(product_id)
        if card is None:
            return None

        # Consume the duplicates
        self.card_counts[product_id] -= DUPLICATE_THRESHOLD
        discount = DUPLICATE_DISCOUNT.get(card.rarity, 5)

        log.info(
            "Merged %dx '%s' → %d%% discount.",
            DUPLICATE_THRESHOLD, card.product_name, discount,
        )
        return DiscountReward(
            source_product_id=product_id,
            source_product_name=card.product_name,
            rarity=card.rarity,
            discount_percent=discount,
        )
