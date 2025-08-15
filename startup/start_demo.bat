@echo off
echo ========================================
echo    🎮 BOT DE TRADING - MODO DEMO
echo ========================================
echo.
echo 🌐 API Demo: demo.tradovateapi.com
echo 💰 Sin riesgo real - Solo testing
echo.

REM Configurar modo demo
set TRADING_MODE=demo

echo 🚀 Iniciando bot en modo DEMO...
cd ..
python3 start_bot.py

echo.
echo ========================================
echo ✅ Bot finalizado
echo ========================================
pause
