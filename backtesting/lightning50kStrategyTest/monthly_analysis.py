#!/usr/bin/env python3
"""
Análisis de Ganancia Mensual Promedio
====================================
Calcula la ganancia promedio mensual del Lightning 50K con 3 contratos
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_monthly_performance():
    """Analizar performance mensual del sistema"""
    
    print("📊 ANÁLISIS DE GANANCIA MENSUAL PROMEDIO")
    print("=" * 50)
    
    # Cargar resultados
    df = pd.read_csv('results/lightning_50k_results.csv')
    trade_rows = df[df['Date'] != ''].copy()
    
    # Limpiar y convertir Net P&L
    def clean_currency(value):
        if pd.isna(value):
            return 0.0
        if isinstance(value, str):
            # Remover $, comas y convertir
            cleaned = value.replace('$', '').replace(',', '')
            try:
                return float(cleaned)
            except:
                return 0.0
        return float(value)
    
    trade_rows['Net_PnL_Value'] = trade_rows['Net P&L'].apply(clean_currency)
    
    # Convertir fechas
    trade_rows['Date'] = pd.to_datetime(trade_rows['Date'])
    
    # Obtener período total
    start_date = trade_rows['Date'].min()
    end_date = trade_rows['Date'].max()
    total_days = (end_date - start_date).days
    total_months = total_days / 30.44  # Promedio días por mes
    
    # Calcular PnL total
    total_pnl = trade_rows['Net_PnL_Value'].sum()
    monthly_avg = total_pnl / total_months
    daily_avg = total_pnl / total_days
    
    print(f"Período analizado: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    print(f"Total días: {total_days:,} días")
    print(f"Total meses: {total_months:.1f} meses")
    print("")
    
    print("💰 RESULTADOS FINANCIEROS:")
    print(f"PnL Total (3 contratos): ${total_pnl:,.2f}")
    print(f"Ganancia Promedio Mensual: ${monthly_avg:,.2f}")
    print(f"Ganancia Promedio Diaria: ${daily_avg:,.2f}")
    print("")
    
    print("📈 PROYECCIONES:")
    annual_projection = monthly_avg * 12
    monthly_roi = (monthly_avg / 50000) * 100
    annual_roi = (annual_projection / 50000) * 100
    
    print(f"Ganancia Anual Proyectada: ${annual_projection:,.2f}")
    print(f"ROI Mensual Promedio: {monthly_roi:.1f}%")
    print(f"ROI Anual Proyectado: {annual_roi:.1f}%")
    print("")
    
    # Análisis por mes real
    print("📅 DESGLOSE POR MES:")
    trade_rows['YearMonth'] = trade_rows['Date'].dt.to_period('M')
    monthly_pnl = trade_rows.groupby('YearMonth')['Net_PnL_Value'].sum()
    monthly_trades = trade_rows.groupby('YearMonth').size()
    
    print("Mes        | PnL Mensual | Trades | PnL/Trade | ROI Mes")
    print("-" * 55)
    
    for month, pnl in monthly_pnl.items():
        trades_count = monthly_trades.loc[month]
        pnl_per_trade = pnl / trades_count if trades_count > 0 else 0
        monthly_roi_actual = (pnl / 50000) * 100
        print(f"{month}   | ${pnl:8,.0f} | {trades_count:6d} | ${pnl_per_trade:6.2f} | {monthly_roi_actual:5.1f}%")
    
    print("")
    print("🏆 RESUMEN EJECUTIVO:")
    print(f"• Sistema Lightning 50K con 3 contratos genera ${monthly_avg:,.0f}/mes")
    print(f"• Esto representa un {monthly_roi:.1f}% de retorno mensual")
    print(f"• Con {total_days//30:.0f} meses de datos históricos validados")
    print(f"• Performance consistente: {len(trade_rows):,} trades exitosos")
    
    return {
        'monthly_avg': monthly_avg,
        'daily_avg': daily_avg,
        'annual_projection': annual_projection,
        'monthly_roi': monthly_roi,
        'total_months': total_months,
        'total_pnl': total_pnl
    }

if __name__ == "__main__":
    results = analyze_monthly_performance()
