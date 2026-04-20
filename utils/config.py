"""
config.py — Central configuration for Golden Apple Pack Opening Game.

All asset paths, animation timings, pack settings, rarity definitions,
and game-wide constants live here so every module imports from one place.
"""

import os

# ─── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR       = os.path.join(PROJECT_ROOT, "assets")
CARDS_DIR        = os.path.join(ASSETS_DIR, "cards")
PACKS_DIR        = os.path.join(ASSETS_DIR, "packs")
EFFECTS_DIR      = os.path.join(ASSETS_DIR, "effects")
UI_DIR           = os.path.join(ASSETS_DIR, "ui")
SOUNDS_DIR       = os.path.join(ASSETS_DIR, "sounds")

DATA_DIR         = os.path.join(PROJECT_ROOT, "data")
CARDS_JSON       = os.path.join(DATA_DIR, "cards.json")
PROBABILITIES_JSON = os.path.join(DATA_DIR, "probabilities.json")
PLAYER_SAVE_JSON = os.path.join(DATA_DIR, "player_save.json")

PLACEHOLDER_IMAGE = os.path.join(ASSETS_DIR, "placeholder.png")

# ─── Window ───────────────────────────────────────────────────────────────────

WINDOW_TITLE  = "Золотое Яблоко — Коллекционные карточки"
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 800

# ─── Rarity definitions ──────────────────────────────────────────────────────

RARITIES = {
    "Common": {
        "glow_color":         "#9E9E9E",   # gray
        "animation_intensity": 1.0,
        "discount_multiplier": 1.0,
    },
    "Rare": {
        "glow_color":         "#2196F3",   # blue
        "animation_intensity": 1.5,
        "discount_multiplier": 1.5,
    },
    "Epic": {
        "glow_color":         "#9C27B0",   # purple
        "animation_intensity": 2.0,
        "discount_multiplier": 2.0,
    },
    "Legendary": {
        "glow_color":         "#FFD700",   # gold
        "animation_intensity": 3.0,
        "discount_multiplier": 3.0,
    },
}

# Duplicate threshold: how many identical cards trigger a merge
DUPLICATE_THRESHOLD = 3

# Discount reward per rarity when duplicates merge
DUPLICATE_DISCOUNT = {
    "Common":    5,
    "Rare":     10,
    "Epic":     15,
    "Legendary": 25,
}

# ─── Pack settings ────────────────────────────────────────────────────────────

PACK_TYPES = {
    "Common Pack": {
        "cards_count": 3,
        "image":       "common_pack.png",
        "sound":       "open_common.wav",
    },
    "Epic Pack": {
        "cards_count": 4,
        "image":       "epic_pack.png",
        "sound":       "open_epic.wav",
    },
    "Legendary Pack": {
        "cards_count": 5,
        "image":       "legendary_pack.png",
        "sound":       "open_legendary.wav",
    },
}

# ─── Animation timing (milliseconds) ─────────────────────────────────────────

ANIM_COMMON_FADE_MS      = 400
ANIM_COMMON_SPARKLE_MS   = 300

ANIM_EPIC_ROTATION_MS    = 600
ANIM_EPIC_GLOW_PULSE_MS  = 500

ANIM_LEGENDARY_FLASH_MS  = 800
ANIM_LEGENDARY_SHAKE_MS  = 400
ANIM_LEGENDARY_REVEAL_MS = 1200

CARD_REVEAL_INTERVAL_MS  = 700   # delay between revealing each card

# ─── Logging ──────────────────────────────────────────────────────────────────

LOG_FILE = os.path.join(PROJECT_ROOT, "game.log")
LOG_LEVEL = "DEBUG"
