#!/usr/bin/env python3
"""
Lightning 50K - Formato CSV Personalizado
=========================================
Genera CSV con columnas específicas del usuario
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_ema(prices, period):
    """Calcular EMA de forma vectorizada"""
    return prices.ewm(span=period, adjust=False).mean()

def detect_signals(df):
    """Detectar señales de trading"""
    df = df.copy()
    
    # Calcular EMAs
    df['ema_9'] = calculate_ema(df['close'], 9)
    df['ema_21'] = calculate_ema(df['close'], 21)
    
    # Detectar cruces
    df['ema_diff'] = df['ema_9'] - df['ema_21']
    df['ema_diff_prev'] = df['ema_diff'].shift(1)
    
    # Señales de trading
    df['bullish_cross'] = (df['ema_diff'] > 0) & (df['ema_diff_prev'] <= 0)
    df['bearish_cross'] = (df['ema_diff'] < 0) & (df['ema_diff_prev'] >= 0)
    
    return df

def round_numbers_strategy_backtest(df):
    """Ejecutar backtest completo con Break Even Protection optimizado"""
    
    logger.info("🚀 INICIANDO LIGHTNING 50K BACKTEST - FORMATO PERSONALIZADO")
    logger.info(f"📊 Barras totales: {len(df):,}")
    logger.info(f"📅 Período: {df.datetime.min()} → {df.datetime.max()}")
    
    # Configuración Lightning 50K
    initial_balance = 50000
    balance = initial_balance
    position = None
    position_size = 1
    commission = 1.0
    
    # Parámetros del sistema BE Protection - OPTIMIZADOS
    stop_loss_points = 1.0     # Optimizado (era 1.5)
    break_even_trigger = 1.5   # Optimizado (era 2.5) 
    trailing_trigger = 4.0     # Optimizado (era 6.0)
    trailing_distance = 3.0    # Optimizado (era 4.0)
    tp_near_rn = 22           # Optimizado (era 28)
    tp_normal = 15            # Optimizado (era 18)    # Listas para almacenar trades
    trades = []
    equity_curve = []
    max_drawdown = 0
    peak_balance = initial_balance
    
    # Round Numbers Logic
    def get_round_number_target(price, direction):
        """Obtener número redondo más cercano"""
        if direction == 'long':
            return (int(price / 100) + 1) * 100
        else:
            return int(price / 100) * 100
    
    def is_near_round_number(price, threshold=25):
        """Verificar si está cerca de un número redondo"""
        remainder = price % 100
        return remainder <= threshold or remainder >= (100 - threshold)
    
    def get_dynamic_tp(entry_price, direction):
        """TP dinámico más conservador para compliance"""
        if is_near_round_number(entry_price):
            return 28  # 28 puntos cerca de números redondos
        return 18  # 18 puntos en otros casos
    
    for i in range(len(df)):
        row = df.iloc[i]
        current_time = row.datetime
        current_price = row.close
        high = row.high
        low = row.low
        
        # Actualizar peak balance y drawdown
        if balance > peak_balance:
            peak_balance = balance
        current_drawdown = peak_balance - balance
        if current_drawdown > max_drawdown:
            max_drawdown = current_drawdown
        
        # Manejar posición existente
        if position is not None:
            entry_price = position['entry_price']
            direction = position['direction']
            entry_time = position['entry_time']
            current_sl = position['current_sl']
            break_even_moved = position.get('break_even_moved', False)
            trailing_active = position.get('trailing_active', False)
            max_favorable = position.get('max_favorable', entry_price)
            tp_points = position['tp_points']
            
            # Actualizar máximo favorable
            if direction == 'long':
                max_favorable = max(max_favorable, high)
                profit_points = max_favorable - entry_price
            else:
                max_favorable = min(max_favorable, low)
                profit_points = entry_price - max_favorable
            
            position['max_favorable'] = max_favorable
            
            # Calcular targets
            if direction == 'long':
                tp_price = entry_price + tp_points
                rn_price = get_round_number_target(entry_price, 'long')
                
                # Break Even Protection Logic
                if not break_even_moved and profit_points >= break_even_trigger:
                    current_sl = entry_price + 0.25  # BE + 1 tick
                    position['current_sl'] = current_sl
                    position['break_even_moved'] = True
                    break_even_moved = True
                
                # Trailing Stop Logic
                if break_even_moved and profit_points >= trailing_trigger:
                    new_sl = max_favorable - trailing_distance
                    if new_sl > current_sl:
                        current_sl = new_sl
                        position['current_sl'] = current_sl
                        position['trailing_active'] = True
                        trailing_active = True
                
            else:  # short
                tp_price = entry_price - tp_points
                rn_price = get_round_number_target(entry_price, 'short')
                
                # Break Even Protection Logic
                if not break_even_moved and profit_points >= break_even_trigger:
                    current_sl = entry_price - 0.25  # BE - 1 tick
                    position['current_sl'] = current_sl
                    position['break_even_moved'] = True
                    break_even_moved = True
                
                # Trailing Stop Logic
                if break_even_moved and profit_points >= trailing_trigger:
                    new_sl = max_favorable + trailing_distance
                    if new_sl < current_sl:
                        current_sl = new_sl
                        position['current_sl'] = current_sl
                        position['trailing_active'] = True
                        trailing_active = True
            
            # Verificar salidas
            exit_price = None
            exit_reason = None
            
            if direction == 'long':
                if low <= current_sl:
                    exit_price = current_sl
                    exit_reason = 'Break Even' if break_even_moved and abs(current_sl - entry_price) < 1 else 'Stop Loss'
                elif high >= rn_price and rn_price < tp_price:
                    exit_price = rn_price
                    exit_reason = 'Round Number'
                elif high >= tp_price:
                    exit_price = tp_price
                    exit_reason = 'Take Profit'
            else:  # short
                if high >= current_sl:
                    exit_price = current_sl
                    exit_reason = 'Break Even' if break_even_moved and abs(current_sl - entry_price) < 1 else 'Stop Loss'
                elif low <= rn_price and rn_price > tp_price:
                    exit_price = rn_price
                    exit_reason = 'Round Number'
                elif low <= tp_price:
                    exit_price = tp_price
                    exit_reason = 'Take Profit'
            
            # Ejecutar salida si hay trigger
            if exit_price is not None:
                if direction == 'long':
                    gross_pnl = (exit_price - entry_price) * position_size * 5
                else:
                    gross_pnl = (entry_price - exit_price) * position_size * 5
                
                net_pnl = gross_pnl - commission
                balance += net_pnl
                
                # Calcular duración en horas
                duration = current_time - entry_time
                duration_hours = duration.total_seconds() / 3600
                
                # Guardar trade con formato personalizado del usuario
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': current_time,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'direction': direction,
                    'position_size': position_size,
                    'duration_hours': duration_hours,
                    'exit_reason': exit_reason,
                    'net_pnl': net_pnl,
                    'balance_after': balance
                })
                
                position = None
                
                if exit_reason == 'Round Number':
                    logger.info(f"💰 RN: {direction} @ {entry_price} → {exit_price} = ${net_pnl:.2f}")
                elif exit_reason == 'Break Even':
                    logger.info(f"🛡️ BE: {direction} @ {entry_price} → {exit_price} = ${net_pnl:.2f}")
        
        # Buscar nuevas entradas si no hay posición
        if position is None:
            if row.bullish_cross and not pd.isna(row.bullish_cross) and row.bullish_cross:
                # Entrada LONG
                entry_price = current_price
                tp_points = get_dynamic_tp(entry_price, 'long')
                initial_sl = entry_price - stop_loss_points
                
                position = {
                    'direction': 'long',
                    'entry_price': entry_price,
                    'entry_time': current_time,
                    'quantity': position_size,
                    'current_sl': initial_sl,
                    'tp_points': tp_points,
                    'break_even_moved': False,
                    'trailing_active': False,
                    'max_favorable': entry_price
                }
                
            elif row.bearish_cross and not pd.isna(row.bearish_cross) and row.bearish_cross:
                # Entrada SHORT
                entry_price = current_price
                tp_points = get_dynamic_tp(entry_price, 'short')
                initial_sl = entry_price + stop_loss_points
                
                position = {
                    'direction': 'short',
                    'entry_price': entry_price,
                    'entry_time': current_time,
                    'quantity': position_size,
                    'current_sl': initial_sl,
                    'tp_points': tp_points,
                    'break_even_moved': False,
                    'trailing_active': False,
                    'max_favorable': entry_price
                }
        
        # Progress cada 10,000 barras
        if i % 10000 == 0:
            logger.info(f"📊 Progreso: {i:,}/{len(df):,} barras ({i/len(df)*100:.1f}%)")
    
    return trades, balance, max_drawdown

def format_custom_csv(trades):
    """Convertir trades al formato específico del usuario con separadores diarios"""
    
    custom_trades = []
    daily_pnl_accumulator = {}  # Diccionario para acumular PnL por día
    running_balance = 50000  # Balance corriente que se actualiza trade por trade
    initial_balance = 50000
    
    # Agrupar trades por día
    trades_by_date = {}
    for trade in trades:
        entry_datetime = pd.to_datetime(trade['entry_time'])
        date = entry_datetime.strftime('%Y-%m-%d')
        
        if date not in trades_by_date:
            trades_by_date[date] = []
        trades_by_date[date].append(trade)
    
    # Procesar cada día ordenadamente
    for date in sorted(trades_by_date.keys()):
        daily_trades = trades_by_date[date]
        
        # Procesar trades del día
        for trade in daily_trades:
            entry_datetime = pd.to_datetime(trade['entry_time'])
            time = entry_datetime.strftime('%H:%M:%S')
            
            # Actualizar balance corriente trade por trade
            running_balance += trade['net_pnl']
            
            # Acumular P&L diario
            if date not in daily_pnl_accumulator:
                daily_pnl_accumulator[date] = 0
            daily_pnl_accumulator[date] += trade['net_pnl']
            
            # Mapear tipo de operación
            operation_type = 'BUY' if trade['direction'] == 'long' else 'SELL'
            
            # Formatear duración
            duration = f"{trade['duration_hours']:.2f}h"
            
            custom_trade = {
                'Date': date,
                'Time': time,
                'MNQ Price': trade['entry_price'],
                'Operation type': operation_type,
                'Contracts': trade['position_size'],
                'Trade duration': duration,
                'Close Reason': trade['exit_reason'],
                'Net P&L': f"${trade['net_pnl']:.2f}",
                'Daily P&L': f"${daily_pnl_accumulator[date]:.2f}",
                'Balance': f"${running_balance:.2f}"
            }
            
            custom_trades.append(custom_trade)
        
        # Agregar fila separadora al final de cada día
        separator_row = {
            'Date': f"Final P&L Day: {daily_pnl_accumulator[date]:.2f}",
            'Time': '',
            'MNQ Price': '',
            'Operation type': '',
            'Contracts': '',
            'Trade duration': '',
            'Close Reason': '',
            'Net P&L': '',
            'Daily P&L': '',
            'Balance': ''
        }
        custom_trades.append(separator_row)
    
    return custom_trades

def main():
    """Función principal"""
    
    # Cargar datos consolidados
    data_file = "/Users/matiasrouaux/Documents/projects/My trading system/backtesting/historical/MNQ_consolidated_2024-2025.csv"
    
    logger.info(f"📥 Cargando archivo: {data_file}")
    df = pd.read_csv(data_file)
    
    # Convertir datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()
    
    # Filtrar solo días de trading (lunes-viernes)
    df = df[df.index.dayofweek < 5]  # 0=Monday, 4=Friday
    
    logger.info(f"✅ Datos cargados: {len(df):,} barras")
    logger.info(f"📅 Período: {df.index.min()} → {df.index.max()}")
    
    # Reset index para trabajar con datetime como columna
    df = df.reset_index()
    
    # Detectar señales
    logger.info("🔍 Detectando señales de trading...")
    df = detect_signals(df)
    
    # Ejecutar backtest
    logger.info("🚀 Ejecutando Lightning 50K con Break Even Protection...")
    trades, final_balance, max_drawdown = round_numbers_strategy_backtest(df)
    
    # Convertir al formato personalizado del usuario
    logger.info("📝 Formateando CSV personalizado...")
    custom_trades = format_custom_csv(trades)
    custom_df = pd.DataFrame(custom_trades)
    
    # Crear directorio results si no existe
    Path('results').mkdir(exist_ok=True)
    
    # Eliminar archivos CSV anteriores
    old_files = [
        'results/complete_18_months_trades.csv',
        'results/backtest_results_detailed.csv',
        'results/best_strategy_trades.csv',
        'results/lightning_50k_complete_18_months.csv',
        'results/lightning_50k_optimized_compliance.csv'
    ]
    
    for old_file in old_files:
        if Path(old_file).exists():
            Path(old_file).unlink()
            logger.info(f"🗑️ Eliminado: {old_file}")
    
    # Guardar CSV con formato personalizado
    output_file = 'results/Lightning_50K_Optimized_Complete.csv'
    custom_df.to_csv(output_file, index=False)
    
    # Estadísticas finales
    if len(custom_df) > 0:
        # Filtrar solo filas de trades (excluir separadores)
        trade_rows = custom_df[~custom_df['Date'].str.startswith('Final P&L Day:', na=False)]
        total_trades = len(trade_rows)
        
        # Convertir Net P&L de string a float para cálculos
        pnl_values = [float(pnl.replace('$', '')) for pnl in trade_rows['Net P&L']]
        winners = sum(1 for pnl in pnl_values if pnl > 0)
        win_rate = winners / total_trades * 100
        total_pnl = sum(pnl_values)
        
        # Análisis por tipo de cierre
        close_reasons = trade_rows['Close Reason'].value_counts()
        
    logger.info("=" * 80)
    logger.info("📊 LIGHTNING 50K - FORMATO CSV PERSONALIZADO")
    logger.info("=" * 80)
    logger.info(f"📅 Período: {df.datetime.min()} → {df.datetime.max()}")
    logger.info(f"📊 Barras procesadas: {len(df):,}")
    logger.info(f"🔢 Total trades: {total_trades:,}")
    logger.info(f"💰 PnL total: ${total_pnl:,.2f}")
    logger.info(f"📈 Balance final: ${final_balance:,.2f}")
    logger.info(f"🏆 Win Rate: {win_rate:.1f}%")
    logger.info(f"📊 Max Drawdown: ${max_drawdown:.2f}")
    logger.info("")
    logger.info("📊 ANÁLISIS POR TIPO DE CIERRE:")
    for reason, count in close_reasons.items():
        logger.info(f"  {reason}: {count} trades")
    logger.info("")
    
    # Verificación Lightning 50K
    lightning_compliant = max_drawdown <= 2000
    logger.info("⚡ VERIFICACIÓN LIGHTNING 50K:")
    logger.info(f"📊 Max Drawdown: ${max_drawdown:.2f} / $2,000 {'✅' if lightning_compliant else '❌'}")
    logger.info(f"🏆 Compliance Status: {'COMPLIANT' if lightning_compliant else 'VIOLATION'}")
    logger.info("")
    
    logger.info(f"💾 Archivo guardado: {output_file}")
    logger.info(f"📋 Formato de columnas:")
    for col in custom_df.columns:
        logger.info(f"   - {col}")
    
    # Contar días únicos y filas separadoras
    separator_rows = len([row for _, row in custom_df.iterrows() if row['Date'].startswith('Final P&L Day:')])
    total_trade_rows = len(custom_df) - separator_rows
    
    logger.info("")
    logger.info(f"📊 ESTRUCTURA DEL CSV:")
    logger.info(f"   🔢 Filas de trades: {total_trade_rows:,}")
    logger.info(f"   📅 Filas separadoras: {separator_rows:,}")
    logger.info(f"   📋 Total filas: {len(custom_df):,}")
    
    # Mostrar ejemplo de Daily P&L y Balance diario
    if len(custom_df) > 0:
        # Obtener solo filas de trades (no separadoras)
        trade_rows = custom_df[~custom_df['Date'].str.startswith('Final P&L Day:', na=False)]
        
        # Agrupar por fecha para mostrar totales diarios
        daily_totals = {}
        daily_balances = {}
        for _, row in trade_rows.iterrows():
            date = row['Date']
            daily_pnl = float(row['Daily P&L'].replace('$', ''))
            daily_balance = float(row['Balance'].replace('$', '').replace(',', ''))
            daily_totals[date] = daily_pnl
            daily_balances[date] = daily_balance
        
        logger.info("")
        logger.info("📅 PRIMEROS 5 DÍAS - DAILY P&L Y BALANCE:")
        for i, (date, daily_pnl) in enumerate(list(daily_totals.items())[:5]):
            daily_balance = daily_balances[date]
            logger.info(f"   {date}: Daily P&L ${daily_pnl:.2f} → Balance ${daily_balance:,.2f}")
            if i >= 4:
                break
    
    return custom_df, final_balance

if __name__ == "__main__":
    custom_df, final_balance = main()
