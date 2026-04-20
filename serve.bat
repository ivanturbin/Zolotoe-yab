@echo off
echo.
echo  ===================================
echo   Золотое Яблоко — локальный сервер
echo  ===================================
echo.
echo  Открой в браузере: http://localhost:8000
echo  Для остановки нажми Ctrl+C
echo.
start http://localhost:8000
python -m http.server 8000
