# 🚀 **TRADING SYSTEM V5 - TRADEIFY COMPLIANT**

## 📋 **DESCRIPCIÓN DEL PROYECTO**

Sistema de trading automatizado diseñado para cumplir con todas las reglas de compliance de Tradeify. El bot implementa la estrategia V5 optimizada con gestión de riesgo integrada y verificación automática de compliance.

**🎯 OBJETIVO:** Sistema de trading automatizado que cumple estrictamente con las reglas de compliance de Tradeify, implementando la estrategia V5 con gestión de riesgo integrada.

## 🎯 **CARACTERÍSTICAS DEL SISTEMA**

### **Sistema de Compliance**
- Verificación automática de reglas de Tradeify
- Control de límites de pérdida diaria
- Gestión de drawdown automática
- Operación en horarios permitidos
- Cumplimiento de reglas de trading

### **Estrategia V5 Optimizada**
- Implementación de estrategia optimizada ($2,031 en 18 trades)
- Win Rate del 77.8% en optimización
- Indicadores técnicos integrados (EMA 34, RSI 14, ATR)
- Filtros de entrada y salida inteligentes
- Gestión de posiciones automática

### **Gestión de Riesgo**
- Stop Loss automático (50 puntos)
- Take Profit configurable (150 puntos)
- Control de tamaño de posición (1 contrato MNQ)
- Gestión de exposición automática
- Sistema de log cronológico completo

### **Sistema de Limpieza Automática**
- Limpieza automática de archivos temporales
- Gestión inteligente de backups
- Optimización continua del sistema
- Mantenimiento automático del proyecto

## 🏗️ **ARQUITECTURA DEL SISTEMA**

### **Scripts Principales:**
- **`tradeify_bot_main.py`** - Bot principal del sistema
- **`tradeify_compliance_system.py`** - Sistema de compliance
- **`tradovate_connector.py`** - Conector con broker
- **`activate_strategy_v5.py`** - Activador de estrategia
- **`cleanup_system.py`** - Sistema de limpieza automática
- **`validate_config_consistency.py`** - Validador de configuración

### **Configuración:**
- **`tradeify_real_config.json`** - Configuración del sistema
- **`strategy_v5.json`** - Parámetros optimizados

## 🚀 **INSTALACIÓN Y USO**

### **Requisitos:**
```bash
pip install -r requirements.txt
```

### **Ejecutar Sistema:**
```bash
# Windows
start_tradeify_bot.bat

# Directo con Python
python3 scripts/tradeify_bot_main.py
```

### **Mantenimiento del Sistema:**
```bash
# Limpieza automática
python3 scripts/cleanup_system.py

# Ejecutar backtest
python3 testing/estrategia_optimizada.py

# Activar estrategia
python3 scripts/activate_strategy_v5.py
```

### **Inicio del Bot:**

#### **🍎 macOS/Linux:**
```bash
# 🎮 MODO DEMO (Sin riesgo real)
export TRADING_MODE=demo && python3 start_bot.py

# 💰 MODO REAL (Con dinero real)
export TRADING_MODE=real && python3 start_bot.py

# 🎯 Scripts auxiliares
python3 startup/start_demo.py      # Modo demo directo
python3 startup/start_real.py      # Modo real directo
```

#### **🪟 Windows:**
```cmd
# 🎮 MODO DEMO
set TRADING_MODE=demo && python start_bot.py

# 💰 MODO REAL
set TRADING_MODE=real && python start_bot.py

# 🎯 Scripts auxiliares
python startup\start_demo.py       # Modo demo directo
python startup\start_real.py       # Modo real directo

# 🪟 Sistema Tradeify completo
startup\start_tradeify_bot.bat
```

#### **💡 Recomendaciones:**
- **👶 Principiantes:** Usar variables de entorno (`TRADING_MODE`)
- **👨‍💻 Avanzados:** Usar scripts auxiliares directamente
- **⚠️ Importante:** Modo REAL = Trading con dinero real

## 📁 **ESTRUCTURA DEL PROYECTO**

```
My trading system/
├── scripts/                    # Scripts principales
│   ├── tradeify_bot_main.py
│   ├── tradeify_compliance_system.py
│   ├── tradovate_connector.py
│   ├── activate_strategy_v5.py # Activador de estrategia V5
│   └── cleanup_system.py       # Sistema de limpieza automática
├── startup/                     # Scripts de inicio auxiliares
│   ├── start_demo.py           # Script modo demo
│   ├── start_real.py           # Script modo real
│   ├── start_tradeify_bot.bat  # Script Windows Tradeify
│   └── README.md               # Documentación de startup
├── config/                     # Configuración
│   ├── tradeify_real_config.json
│   ├── tradeify_demo_config.json
│   ├── strategy_v5.json
│   ├── config_master.json
│   └── backups/               # Backups automáticos
├── logs/                       # Logs del sistema
├── docs/                       # Documentación
│   ├── BOT_OWNERSHIP_DEMONSTRATION.md
│   ├── tradeify_analysis.md
│   ├── tradovate_api_documentation.md
│   └── strategies/
│       └── V5_SIMPLIFIED_STRATEGY.md
├── testing/                    # Estrategias y optimización
│   ├── estrategia_optimizada.py
│   ├── comprehensive_optimizer.py
│   ├── ninjatrader_data_loader.py
│   ├── optimization_results.json
│   ├── backtest_results.json
│   └── MNQ_09-25_30days_1min.txt
├── start_bot.py                 # 🤖 BOT PRINCIPAL UNIFICADO
├── requirements.txt            # Dependencias Python
└── README.md                  # Este archivo
```

## 🖥️ **EJECUCIÓN MULTI-PLATAFORMA**

### **🍎 macOS/Linux:**
- **Comando Python:** `python3`
- **Variables de entorno:** `export TRADING_MODE=demo`
- **Separador de rutas:** `/`
- **Scripts nativos:** `.sh`

### **🪟 Windows:**
- **Comando Python:** `python`
- **Variables de entorno:** `set TRADING_MODE=demo`
- **Separador de rutas:** `\`
- **Scripts nativos:** `.bat`

### **🎯 Configuración Automática:**
- **Modo Demo:** Carga `config/tradeify_demo_config.json`
- **Modo Real:** Carga `config/tradeify_real_config.json`
- **Logs:** `logs/bot_optimized.log` (unificado)

## 🔐 **SEGURIDAD Y COMPLIANCE**

- **Credenciales**: No incluidas en el repositorio
- **Configuración**: Archivos de configuración seguros
- **Compliance**: Verificación automática en tiempo real
- **Logging**: Sistema de auditoría integrado
- **Backups**: Sistema automático de respaldo
- **Limpieza**: Gestión automática de archivos temporales

## 📈 **FUNCIONALIDADES**

1. **Trading automatizado** con estrategia V5 optimizada
2. **Verificación de compliance** en tiempo real
3. **Conexión con broker** Tradovate (API documentada)
4. **Gestión de riesgo** automática con parámetros optimizados
5. **Sistema de log cronológico** para análisis detallado
6. **Optimización automática** de parámetros
7. **Limpieza automática** del sistema
8. **Backups automáticos** de configuración

## 👨‍💻 **DESARROLLADOR**

- **Nombre**: Matias Rouaux
- **Cuenta Tradeify**: TDY030574
- **Contacto**: Via Tradeify Support

## 📄 **LICENCIA**

Proyecto privado desarrollado exclusivamente para Tradeify. Todos los derechos reservados.

## 🧹 **MANTENIMIENTO AUTOMÁTICO**

El sistema incluye un script de limpieza automática que mantiene el proyecto optimizado:

```bash
python3 scripts/cleanup_system.py
```

**Elimina automáticamente:**
- Logs temporales
- Caché de Python
- Backups antiguos (>7 días)
- Reportes antiguos (>3 días)

---

**🎯 OBJETIVO**: Sistema de trading automatizado que cumple estrictamente con las reglas de compliance de Tradeify, implementando la estrategia V5 con gestión de riesgo integrada.
