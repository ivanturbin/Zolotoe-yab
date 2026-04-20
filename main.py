#!/usr/bin/env python3
"""
main.py — Точка входа в игру «Золотое Яблоко».

Порядок запуска:
  1. QApplication
  2. Загрузка фирменных шрифтов
  3. Применение глобального стиля
  4. Инициализация GameManager
  5. Показ главного окна
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication

from core.game_manager import GameManager
from ui.main_window import MainWindow
from utils.theme import load_brand_fonts, app_stylesheet
from utils.logger import get_logger

log = get_logger("main")


def main() -> None:
    log.info("═══ Золотое Яблоко — запуск ═══")

    app = QApplication(sys.argv)
    app.setApplicationName("Золотое Яблоко")

    # Фирменные шрифты (Unbounded + Inter)
    load_brand_fonts()

    # Фирменный стиль
    app.setStyleSheet(app_stylesheet())

    # Сабсистемы
    game = GameManager()
    game.init()

    window = MainWindow(game)
    window.show()

    log.info("UI готов — запуск event loop.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
