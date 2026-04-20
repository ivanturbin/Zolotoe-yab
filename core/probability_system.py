"""
probability_system.py — Weighted random selection for pack openings.

Reads probabilities from data/probabilities.json and provides a method
to roll *n* rarities according to a given pack type's distribution.
"""

from __future__ import annotations

import json
import random
from typing import Dict, List

from utils.config import PROBABILITIES_JSON
from utils.logger import get_logger

log = get_logger(__name__)

# Default fallback if JSON is missing or corrupted
_DEFAULT_PROBABILITIES: Dict[str, Dict[str, float]] = {
    "Common Pack": {"Common": 0.70, "Rare": 0.20, "Epic": 0.09, "Legendary": 0.01},
    "Epic Pack":   {"Common": 0.40, "Rare": 0.35, "Epic": 0.20, "Legendary": 0.05},
    "Legendary Pack": {"Common": 0.20, "Rare": 0.40, "Epic": 0.30, "Legendary": 0.10},
}


class ProbabilitySystem:
    """Load probability tables and perform weighted rolls."""

    def __init__(self) -> None:
        self.tables: Dict[str, Dict[str, float]] = {}
        self._load()

    # ── public ────────────────────────────────────────────────────────────

    def roll_rarities(self, pack_type: str, count: int) -> List[str]:
        """Return *count* rarity strings sampled from *pack_type* table."""
        table = self.tables.get(pack_type)
        if table is None:
            log.warning("No probability table for '%s' — using Common Pack.", pack_type)
            table = self.tables.get("Common Pack", _DEFAULT_PROBABILITIES["Common Pack"])

        rarities = list(table.keys())
        weights  = [table[r] for r in rarities]
        return random.choices(rarities, weights=weights, k=count)

    # ── internal ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            with open(PROBABILITIES_JSON, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            # Normalise keys and values
            for pack_name, dist in raw.items():
                total = sum(dist.values())
                self.tables[pack_name] = {
                    r: v / total for r, v in dist.items()
                }
            log.info("Probabilities loaded from %s", PROBABILITIES_JSON)
        except FileNotFoundError:
            log.warning("Probabilities file not found — using defaults.")
            self.tables = dict(_DEFAULT_PROBABILITIES)
        except (json.JSONDecodeError, TypeError, KeyError) as exc:
            log.error("Broken probabilities JSON: %s — using defaults.", exc)
            self.tables = dict(_DEFAULT_PROBABILITIES)
