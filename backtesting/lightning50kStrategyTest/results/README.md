# Lightning 50K - Resultados de Backtesting

## Archivo de Resultados

**`lightning_50k_results.csv`** - Resultados completos del backtesting

### Estructura del CSV (12 columnas)

1. **Date** - Fecha del trade
2. **Time** - Hora del trade  
3. **MNQ Price** - Precio del MNQ
4. **Operation type** - Tipo de operación (Long/Short)
5. **Contracts** - Cantidad de contratos
6. **Trade duration** - Duración del trade
7. **Close Reason** - Razón de cierre (Stop Loss/Break Even/Round Number)
8. **Net P&L** - P&L neto del trade
9. **Daily P&L** - P&L del trade individual
10. **Balance** - Balance acumulado
11. **Day** - Número del día de trading
12. **Daily P&L Total** - P&L total diario

## Estadísticas Actuales

- **Trades Totales**: 14,084
- **P&L Total**: $192,698.50
- **Win Rate**: 67.5%
- **Max Drawdown**: $581.00
- **Período**: 2024-01-02 a 2025-08-19 (422 días)
- **Promedio**: 33.4 trades/día

## Generación

Para regenerar este archivo:
```bash
python lightning_50k_custom_format.py
```

El archivo `lightning_50k_results.csv` será sobrescrito automáticamente con los nuevos datos.
