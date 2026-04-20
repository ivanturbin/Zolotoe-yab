#!/bin/bash
echo ""
echo "  ==================================="
echo "   Золотое Яблоко — локальный сервер"
echo "  ==================================="
echo ""
echo "  Открой в браузере: http://localhost:8000"
echo "  Для остановки нажми Ctrl+C"
echo ""
python3 -m http.server 8000 &
sleep 1
if command -v xdg-open &>/dev/null; then xdg-open http://localhost:8000
elif command -v open &>/dev/null; then open http://localhost:8000
fi
wait
