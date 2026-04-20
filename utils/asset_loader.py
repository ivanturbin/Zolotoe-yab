"""
asset_loader.py — Automatic texture & sound loading system.

• Scans assets/cards/<rarity>/ and builds textures[rarity][card_name]
• Loads pack images, glow effects, UI backgrounds
• Falls back to a generated placeholder when an image is missing
• Loads sounds via pygame.mixer
"""

from __future__ import annotations

import os
from typing import Dict, Optional

from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PyQt6.QtCore import Qt

from utils.config import (
    ASSETS_DIR, CARDS_DIR, PACKS_DIR, EFFECTS_DIR,
    UI_DIR, SOUNDS_DIR, PLACEHOLDER_IMAGE, RARITIES,
)
from utils.logger import get_logger

log = get_logger(__name__)

# Try to import pygame for sound; gracefully degrade if unavailable
try:
    import pygame
    pygame.mixer.init()
    _SOUND_AVAILABLE = True
except Exception:
    _SOUND_AVAILABLE = False
    log.warning("pygame.mixer not available — sounds disabled.")


class AssetLoader:
    """Singleton-style loader; call ``load_all()`` once at startup."""

    def __init__(self) -> None:
        # textures[rarity][card_stem] = QPixmap
        self.textures: Dict[str, Dict[str, QPixmap]] = {}
        # Fast lookup by relative image path (e.g. "cards/epic/perfume1.png")
        self._by_image_path: Dict[str, QPixmap] = {}
        # pack_images[pack_filename] = QPixmap
        self.pack_images: Dict[str, QPixmap] = {}
        # glow_images[rarity] = QPixmap
        self.glow_images: Dict[str, QPixmap] = {}
        # ui_images[filename] = QPixmap
        self.ui_images: Dict[str, QPixmap] = {}
        # sounds[filename] = pygame.mixer.Sound | None
        self.sounds: Dict[str, object] = {}

        self._placeholder: Optional[QPixmap] = None

    # ── public API ────────────────────────────────────────────────────────

    def load_all(self) -> None:
        """Load every asset category."""
        log.info("Asset loading started …")
        self._load_card_textures()
        self._load_pack_images()
        self._load_glow_effects()
        self._load_ui_images()
        self._load_sounds()
        log.info("Asset loading complete.")

    def get_card_texture(self, rarity: str, card_name: str,
                         image_path: str = "") -> QPixmap:
        """Return card QPixmap.

        Tries (in order):
          1. Exact image_path lookup (e.g. "cards/epic/perfume1.png")
          2. rarity + card_name stem lookup
          3. Placeholder
        """
        # 1. By relative image path
        if image_path:
            pix = self._by_image_path.get(image_path)
            if pix and not pix.isNull():
                return pix
        # 2. By rarity dict
        pix = self.textures.get(rarity, {}).get(card_name)
        if pix and not pix.isNull():
            return pix
        return self._get_placeholder()

    def get_pack_image(self, filename: str) -> QPixmap:
        return self.pack_images.get(filename, self._get_placeholder())

    def get_glow(self, rarity: str) -> QPixmap:
        return self.glow_images.get(rarity, self._get_placeholder())

    def get_ui(self, filename: str) -> QPixmap:
        return self.ui_images.get(filename, self._get_placeholder())

    def play_sound(self, filename: str) -> None:
        if not _SOUND_AVAILABLE:
            return
        snd = self.sounds.get(filename)
        if snd:
            snd.play()
        else:
            log.warning("Sound not found: %s", filename)

    # ── internal loaders ──────────────────────────────────────────────────

    def _load_card_textures(self) -> None:
        """Scan assets/cards/<rarity>/ and populate self.textures + _by_image_path."""
        for rarity in RARITIES:
            rarity_dir = os.path.join(CARDS_DIR, rarity.lower())
            self.textures[rarity] = {}
            if not os.path.isdir(rarity_dir):
                log.warning("Card folder missing: %s", rarity_dir)
                continue
            for fname in sorted(os.listdir(rarity_dir)):
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    path = os.path.join(rarity_dir, fname)
                    stem = os.path.splitext(fname)[0]
                    pix = QPixmap(path)
                    if pix.isNull():
                        log.warning("Failed to load card image: %s", path)
                        pix = self._get_placeholder()
                    self.textures[rarity][stem] = pix
                    # Also index by relative path (e.g. "cards/epic/perfume1.png")
                    rel = f"cards/{rarity.lower()}/{fname}"
                    self._by_image_path[rel] = pix
                    log.debug("Loaded card texture [%s] %s", rarity, stem)

    def _load_pack_images(self) -> None:
        if not os.path.isdir(PACKS_DIR):
            log.warning("Packs directory missing: %s", PACKS_DIR)
            return
        for fname in os.listdir(PACKS_DIR):
            if fname.lower().endswith((".png", ".jpg")):
                pix = QPixmap(os.path.join(PACKS_DIR, fname))
                self.pack_images[fname] = pix if not pix.isNull() else self._get_placeholder()

    def _load_glow_effects(self) -> None:
        if not os.path.isdir(EFFECTS_DIR):
            log.warning("Effects directory missing: %s", EFFECTS_DIR)
            return
        for rarity in RARITIES:
            fname = f"glow_{rarity.lower()}.png"
            path = os.path.join(EFFECTS_DIR, fname)
            if os.path.isfile(path):
                pix = QPixmap(path)
                self.glow_images[rarity] = pix if not pix.isNull() else self._get_placeholder()
            else:
                log.debug("Glow effect missing for %s — will use generated glow.", rarity)

    def _load_ui_images(self) -> None:
        if not os.path.isdir(UI_DIR):
            return
        for fname in os.listdir(UI_DIR):
            if fname.lower().endswith((".png", ".jpg")):
                pix = QPixmap(os.path.join(UI_DIR, fname))
                self.ui_images[fname] = pix if not pix.isNull() else self._get_placeholder()

    def _load_sounds(self) -> None:
        if not _SOUND_AVAILABLE or not os.path.isdir(SOUNDS_DIR):
            return
        for fname in os.listdir(SOUNDS_DIR):
            if fname.lower().endswith((".wav", ".ogg", ".mp3")):
                try:
                    self.sounds[fname] = pygame.mixer.Sound(
                        os.path.join(SOUNDS_DIR, fname)
                    )
                except Exception as exc:
                    log.warning("Cannot load sound %s: %s", fname, exc)

    # ── placeholder generator ─────────────────────────────────────────────

    def _get_placeholder(self) -> QPixmap:
        """Return a simple 256×256 placeholder with a '?' label."""
        if self._placeholder is not None:
            return self._placeholder

        # Try loading an external placeholder first
        if os.path.isfile(PLACEHOLDER_IMAGE):
            pix = QPixmap(PLACEHOLDER_IMAGE)
            if not pix.isNull():
                self._placeholder = pix
                return pix

        # Generate one programmatically
        img = QImage(256, 256, QImage.Format.Format_ARGB32)
        img.fill(QColor(40, 40, 40))
        painter = QPainter(img)
        painter.setPen(QColor(200, 200, 200))
        font = QFont("Arial", 64, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, "?")
        painter.end()
        self._placeholder = QPixmap.fromImage(img)
        return self._placeholder
