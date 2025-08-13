@echo off
REM ==================================================
REM 🚀 TRADEIFY BOT - SISTEMA UNIFICADO COMPLETO
REM ==================================================
REM Desarrollador: Matias Rouaux
REM Cuenta: TDY030574
REM Propósito: Verificación de Tradeify
REM ==================================================

echo.
echo 🚀 INICIANDO BOT PRINCIPAL TRADEIFY
echo ==================================================
echo 👨‍💻 Desarrollador: Matias Rouaux
echo 📧 Cuenta: TDY030574
echo 🎯 Propósito: Verificación de Tradeify
echo ==================================================
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo Por favor, instala Python 3.8+ y agrégalo al PATH
    pause
    exit /b 1
)

echo ✅ Python detectado correctamente
echo.

REM Verificar que los archivos necesarios existan
if not exist "scripts\tradeify_bot_main.py" (
    echo ❌ ERROR: No se encuentra tradeify_bot_main.py
    echo Verifica que el archivo esté en la carpeta scripts/
    pause
    exit /b 1
)

if not exist "scripts\tradeify_compliance_system.py" (
    echo ❌ ERROR: No se encuentra tradeify_compliance_system.py
    echo Verifica que el archivo esté en la carpeta scripts/
    pause
    exit /b 1
)

if not exist "scripts\tradovate_connector.py" (
    echo ❌ ERROR: No se encuentra tradovate_connector.py
    echo Verifica que el archivo esté en la carpeta scripts/
    pause
    exit /b 1
)

echo ✅ Todos los archivos necesarios están presentes
echo.

REM Verificar dependencias de Python
echo 🔍 Verificando dependencias de Python...
python -c "import json, logging, datetime, typing" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Faltan dependencias básicas de Python
    echo Ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencias básicas verificadas
echo.

REM Iniciar el bot principal
echo 🚀 INICIANDO BOT PRINCIPAL...
echo ==================================================
echo.

python scripts\tradeify_bot_main.py

REM Verificar el resultado
if errorlevel 1 (
    echo.
    echo ❌ ERROR: El bot falló durante la ejecución
    echo Revisa los logs anteriores para más detalles
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 ¡BOT EJECUTADO EXITOSAMENTE!
    echo ✅ Sistema listo para verificación de Tradeify
    echo.
)

echo.
echo ==================================================
echo 📱 El equipo de Tradeify puede verificar todo en vivo
echo 👨‍💻 Desarrollador: Matias Rouaux
echo 📧 Cuenta: TDY030574
echo ✅ Sistema listo para aprobación
echo ==================================================
echo.

pause
