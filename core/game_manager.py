"""
game_manager.py — Central orchestrator wiring every subsystem together.

Owns:
  AssetLoader, ProbabilitySystem, PackSystem, RaritySystem,
  DuplicateSystem, SaveSystem

Exposes high-level actions consumed by the UI layer.
"""

from __future__ import annotations

from typing import List

from utils.asset_loader import AssetLoader
from utils.logger import get_logger

from core.rarity_system import RaritySystem
from core.probability_system import ProbabilitySystem
from core.pack_system import PackSystem, PackResult
from core.duplicate_system import DuplicateSystem, DiscountReward
from core.save_system import SaveSystem

log = get_logger(__name__)


class GameManager:
    """Façade that the UI talks to."""

    def __init__(self) -> None:
        # Sub-systems
        self.assets   = AssetLoader()
        self.rarity   = RaritySystem()
        self.prob     = ProbabilitySystem()
        self.packs    = PackSystem(self.prob)
        self.dupes    = DuplicateSystem()
        self.save     = SaveSystem()

    # ── lifecycle ─────────────────────────────────────────────────────────

    def init(self) -> None:
        """Call once at startup after QApplication is created."""
        self.assets.load_all()
        self._restore_save()
        log.info("GameManager initialised.")

    # ── actions ───────────────────────────────────────────────────────────

    def open_pack(self, pack_type: str) -> tuple[PackResult, List[DiscountReward]]:
        """
        Open a pack:
          1. Draw cards.
          2. Detect duplicates → create discount rewards.
          3. Persist progress.

        Returns (PackResult, list_of_new_discounts).
        """
        result = self.packs.open_pack(pack_type)
        rewards = self.dupes.register_cards(result.cards)

        # Persist
        self.save.record_pack_opened(pack_type)
        counts, meta = self.dupes.export_state()
        self.save.set_card_counts(counts)
        self.save.set_card_meta(meta)
        for r in rewards:
            self.save.add_discount({
                "product_id": r.source_product_id,
                "product_name": r.source_product_name,
                "rarity": r.rarity,
                "discount_percent": r.discount_percent,
            })
        self.save.save()
        return result, rewards

    def get_discounts(self) -> list[dict]:
        return self.save.get_discounts()

    def get_collection_counts(self) -> dict[str, int]:
        return dict(self.dupes.card_counts)

    # ── internal ──────────────────────────────────────────────────────────

    def _restore_save(self) -> None:
        data = self.save.load()
        counts = data.get("card_counts", {})
        meta   = data.get("card_meta", [])
        if counts:
            self.dupes.load_state(counts, meta)
            log.info("Restored %d card entries from save.", len(counts))
