# 🚀 Scripts de Inicio - Trading Bot

Esta carpeta contiene los scripts auxiliares para iniciar el bot de trading en diferentes modos.

## 📁 Contenido:

### **🎮 `start_demo.py`**
- **Propósito:** Iniciar bot en modo DEMO (sin riesgo real)
- **Uso:** `python3 start_demo.py`
- **Resultado:** Bot ejecutándose con API de prueba

### **💰 `start_real.py`**
- **Propósito:** Iniciar bot en modo REAL (con dinero real)
- **Uso:** `python3 start_real.py`
- **Resultado:** Bot ejecutándose con API de producción
- **⚠️ ADVERTENCIA:** Trading con dinero real

### **🪟 `start_tradeify_bot.bat`**
- **Propósito:** Script Windows para sistema Tradeify completo
- **Uso:** `start_tradeify_bot.bat` (desde cmd)
- **Resultado:** Sistema completo de Tradeify ejecutándose

## 🎯 **¿CUÁL USAR?**

### **Para usuarios principiantes:**
- **macOS/Linux:** Ejecuta `python3 ../start_bot.py` desde la raíz
- **Windows:** Ejecuta `start_tradeify_bot.bat` desde esta carpeta

### **Para usuarios avanzados:**
- **Modo Demo:** `python3 start_demo.py`
- **Modo Real:** `python3 start_real.py`
- **Sistema completo:** `start_tradeify_bot.bat`

## 💡 **NOTA IMPORTANTE:**

Estos scripts son **AUXILIARES**. El bot principal es `start_bot.py` en la raíz del proyecto.

**🚀 USO RECOMENDADO:**
```bash
# Desde la raíz del proyecto
export TRADING_MODE=demo && python3 start_bot.py
export TRADING_MODE=real && python3 start_bot.py

# O usar los scripts de startup (más fácil)
cd startup
python3 start_demo.py    # Para modo demo
python3 start_real.py    # Para modo real
```
