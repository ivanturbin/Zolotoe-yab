"""
save_system.py — Serialise / deserialise player progress to JSON.

Stores:
  • owned card counts
  • discount rewards
  • number of packs opened (per type)
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

from utils.config import PLAYER_SAVE_JSON
from utils.logger import get_logger

log = get_logger(__name__)


class SaveSystem:
    """Read/write player_save.json."""

    def __init__(self) -> None:
        self.data: dict = self._empty_save()

    # ── public ────────────────────────────────────────────────────────────

    def load(self) -> dict:
        """Load save file and return its data dict."""
        if not os.path.isfile(PLAYER_SAVE_JSON):
            log.info("No save file found — starting fresh.")
            self.data = self._empty_save()
            return self.data

        try:
            with open(PLAYER_SAVE_JSON, "r", encoding="utf-8") as fh:
                self.data = json.load(fh)
            log.info("Save loaded from %s", PLAYER_SAVE_JSON)
        except (json.JSONDecodeError, OSError) as exc:
            log.error("Corrupted save file: %s — resetting.", exc)
            self.data = self._empty_save()
        return self.data

    def save(self) -> None:
        """Persist current data to disk."""
        try:
            os.makedirs(os.path.dirname(PLAYER_SAVE_JSON), exist_ok=True)
            with open(PLAYER_SAVE_JSON, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, ensure_ascii=False, indent=2)
            log.debug("Progress saved.")
        except OSError as exc:
            log.error("Cannot write save file: %s", exc)

    # ── helpers ───────────────────────────────────────────────────────────

    def record_pack_opened(self, pack_type: str) -> None:
        self.data.setdefault("packs_opened", {})
        self.data["packs_opened"][pack_type] = (
            self.data["packs_opened"].get(pack_type, 0) + 1
        )

    def set_card_counts(self, counts: Dict[str, int]) -> None:
        self.data["card_counts"] = counts

    def set_card_meta(self, meta: List[dict]) -> None:
        self.data["card_meta"] = meta

    def add_discount(self, discount: dict) -> None:
        self.data.setdefault("discounts", []).append(discount)

    def get_discounts(self) -> List[dict]:
        return self.data.get("discounts", [])

    def get_card_counts(self) -> Dict[str, int]:
        return self.data.get("card_counts", {})

    def get_card_meta(self) -> List[dict]:
        return self.data.get("card_meta", [])

    # ── private ───────────────────────────────────────────────────────────

    @staticmethod
    def _empty_save() -> dict:
        return {
            "card_counts": {},
            "card_meta": [],
            "discounts": [],
            "packs_opened": {},
        }
