# Lightning 50K Trading System

Sistema automatizado de trading para la plataforma Tradeify con estrategia optimizada Lightning 50K.

## Rendimiento del Sistema

- **P&L Total**: $192,698.50 
- **Win Rate**: 67.5%
- **Max Drawdown**: $581.00
- **Trades Totales**: 14,084 en 422 días
- **Promedio**: 33.4 trades/día

## Parámetros de Trading

- **Stop Loss**: 1.0 puntos
- **Break Even**: 1.5 puntos  
- **Trailing Stop**: Trigger 4.0pts, Distance 3.0pts
- **Take Profit Long**: 22 puntos
- **Take Profit Short**: 15 puntos
- **Indicadores**: EMA 9/21 crossover

## Estructura del Proyecto

```
/scripts/
├── tradeify_bot_main.py              # Bot principal
├── activate_lightning_50k.py         # Script de activación
├── tradeify_compliance_system.py     # Sistema de compliance
├── tradovate_connector.py            # Conector API
├── test_tradovate_integration.py     # Pruebas de integración
├── simple_validator.py              # Validador del sistema
└── validate_config_consistency.py   # Validador de configuración

/config/
└── lightning_50k_strategy.json      # Configuración del sistema

/docs/
├── LIGHTNING_50K_RULES.md           # Reglas de trading
├── BOT_OWNERSHIP_DEMONSTRATION.md   # Demostración de autoría
├── TRADOVATE_API_DOCUMENTATION.md   # Documentación API
└── ROUND_NUMBERS_STRATEGY_ADOPTED.md # Estrategia Round Numbers

/.venv/                               # Entorno virtual Python

/backtesting/lightning50kStrategyTest/
├── lightning_50k_drawdown_optimizer.py    # Optimizador de parámetros
├── lightning_50k_custom_format.py         # Generador de resultados
└── results/
    └── lightning_50k_results.csv          # Resultados del backtest
```

## Resultados de Backtesting

**Archivo**: `backtesting/lightning50kStrategyTest/results/lightning_50k_results.csv`

### Estructura del CSV (12 columnas):
1. Date - Fecha del trade
2. Time - Hora del trade  
3. MNQ Price - Precio del MNQ
4. Operation type - Tipo de operación (Long/Short)
5. Contracts - Cantidad de contratos
6. Trade duration - Duración del trade
7. Close Reason - Razón de cierre (Stop Loss/Break Even/Round Number)
8. Net P&L - P&L neto del trade
9. Daily P&L - P&L del trade individual
10. Balance - Balance acumulado
11. Day - Número del día de trading
12. Daily P&L Total - P&L total diario
6. Trade duration - Duración del trade
7. Close Reason - Razón de cierre (Stop Loss/Break Even/Round Number)
8. Net P&L - P&L neto del trade
9. Daily P&L - P&L del trade individual
10. Balance - Balance acumulado
11. Day - Número del día de trading
## Activación del Sistema

```bash
# Activar Lightning 50K
python3 scripts/activate_lightning_50k.py
```

## Requisitos

- **Cuenta Tradeify Lightning 50K** fondeada
- **API Tradovate** ($25/mes)
- **Python 3.9+** con entorno virtual
- **Aprobación del bot** en Tradeify

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno virtual
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

El sistema usa `config/lightning_50k_strategy.json` que contiene:
- Parámetros de trading optimizados
- Configuración de la plataforma Tradeify
- Reglas de compliance del lightning_50k_strategy
- Configuración del conector Tradovate

## Generación de Resultados

Para generar/actualizar resultados de backtesting:
```bash
cd backtesting/lightning50kStrategyTest
python lightning_50k_custom_format.py
```

Esto sobrescribe automáticamente `results/lightning_50k_results.csv` con los datos actualizados.
```

### Activación del Sistema (macOS):

```bash
# Desde la raíz del proyecto (macOS/Linux)
python3 scripts/activate_lightning_50k.py
```

**lightning_50k_strategy Optimizado v1.0.0** - Sistema completo optimizado para **macOS** con parámetros validados que lograron $192,698 P&L con solo $581 drawdown en 422 días de trading.

### Plataforma:
- **Desarrollado y probado en**: macOS
- **Compatible con**: macOS, Linux  
- **Activación**: Un solo comando desde terminal

### Requisitos:
1. **Cuenta Tradeify lightning_50k_strategy** fondeada
2. **API Access de Tradovate** ($25/mes)
3. **Bot aprobado** por Tradeify (completado)

### Limpieza Completada:
- ELIMINADO: Todas las estrategias obsoletas (round numbers, EMA 200, etc.)
- ELIMINADO: Archivos de desarrollo y análisis intermedios
- ELIMINADO: Configuraciones duplicadas o experimentales
- ELIMINADO: Backtester intermedios y versiones de prueba
- CONSERVADO: Solo archivos esenciales de la estrategia final optimizada

### Estado Actual:
**SISTEMA 100% LIMPIO Y LISTO PARA TRADING EN VIVO**

---
*Sistema optimizado y limpiado: 31/08/2025*
