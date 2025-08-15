@echo off
echo ========================================
echo    💰 BOT DE TRADING - MODO REAL
echo ========================================
echo.
echo 🌐 API Real: live.tradovateapi.com
echo ⚠️  ATENCIÓN: Trading con dinero real
echo.

REM Configurar modo real
set TRADING_MODE=real

echo 🚀 Iniciando bot en modo REAL...
cd ..
python3 start_bot.py

echo.
echo ========================================
echo ✅ Bot finalizado
echo ========================================
pause
