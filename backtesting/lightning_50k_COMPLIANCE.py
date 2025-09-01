#!/usr/bin/env python3
"""
Lightning 50K - COMPLIANCE VERSION
=================================
Versión que mantiene la alta rentabilidad pero cumple con drawdown de $2,000
Basado en el sistema que genera +$189,117 pero con control de riesgo
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

def lightning_compliance_backtest(df):
    """Ejecutar backtest con COMPLIANCE pero manteniendo profitabilidad"""
    
    logger.info("INICIANDO LIGHTNING 50K - COMPLIANCE VERSION")
    logger.info(f"Barras totales: {len(df):,}")
    logger.info(f"Período: {df.datetime.min()} → {df.datetime.max()}")
    
    # Configuración Lightning 50K COMPLIANCE
    initial_balance = 50000
    balance = initial_balance
    position = None
    
    # CONTROL DE RIESGO DINÁMICO
    max_drawdown_limit = 1800  # $200 buffer vs $2K límite 
    base_position_size = 3     # Base 3 contratos
    current_position_size = base_position_size
    commission = 3.0           # Base commission
    
    # PARÁMETROS OPTIMIZADOS PARA COMPLIANCE
    stop_loss_points = 0.8     # Más tight (era 1.0)
    break_even_trigger = 1.2   # Más rápido BE (era 1.5) 
    trailing_trigger = 3.5     # Trailing más temprano (era 4.0)
    trailing_distance = 2.5    # Trailing más cerca (era 3.0)
    tp_near_rn = 18           # TP más conservador (era 22)
    tp_normal = 12            # TP más conservador (era 15)
    
    # Variables de estado
    trades = []
    max_drawdown = 0
    peak_balance = initial_balance
    consecutive_losses = 0
    daily_loss = 0
    last_trade_date = None
    
    # Daily loss control
    daily_loss_limit = 600     # Límite diario de pérdida
    
    def get_dynamic_position_size(balance, peak_balance, consecutive_losses):
        """Position sizing dinámico basado en performance"""
        current_dd = peak_balance - balance
        
        # Reducir size si drawdown alto
        if current_dd > 1200:
            return 1  # Solo 1 contrato si DD > $1200
        elif current_dd > 800:
            return 2  # 2 contratos si DD > $800
        elif consecutive_losses >= 3:
            return 2  # Reducir después de 3 pérdidas consecutivas
        elif consecutive_losses >= 5:
            return 1  # Solo 1 contrato después de 5 pérdidas
        else:
            return base_position_size  # 3 contratos normal
    
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
            return tp_near_rn  # 18 puntos cerca de números redondos
        return tp_normal  # 12 puntos en otros casos
    
    def check_daily_reset(current_date, last_date):
        """Verificar si cambió el día para resetear daily loss"""
        if last_date is None:
            return True, 0
        if current_date.date() != last_date.date():
            return True, 0
        return False, daily_loss
    
    for i in range(len(df)):
        row = df.iloc[i]
        current_time = row.datetime
        current_price = row.close
        high = row.high
        low = row.low
        
        # Check daily reset
        is_new_day, daily_loss = check_daily_reset(current_time, last_trade_date)
        if is_new_day:
            daily_loss = 0
            
        # Actualizar peak balance y drawdown
        if balance > peak_balance:
            peak_balance = balance
        current_drawdown = peak_balance - balance
        if current_drawdown > max_drawdown:
            max_drawdown = current_drawdown
        
        # EMERGENCY STOP si se acerca al límite
        if current_drawdown > max_drawdown_limit:
            logger.warning(f"EMERGENCY: Drawdown {current_drawdown:.2f} cerca del límite {max_drawdown_limit}")
            if position is not None:
                # Cerrar posición inmediatamente
                entry_price = position['entry_price']
                direction = position['direction']
                entry_time = position['entry_time']
                current_size = position['quantity']
                
                if direction == 'long':
                    gross_pnl = (current_price - entry_price) * current_size * 2.0
                else:
                    gross_pnl = (entry_price - current_price) * current_size * 2.0
                
                net_pnl = gross_pnl - (current_size * 1.0)  # Commission
                balance += net_pnl
                daily_loss += net_pnl if net_pnl < 0 else 0
                
                # Registrar emergency exit
                duration = current_time - entry_time
                duration_hours = duration.total_seconds() / 3600
                
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': current_time,
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'direction': direction,
                    'position_size': current_size,
                    'duration_hours': duration_hours,
                    'exit_reason': 'Emergency Stop',
                    'net_pnl': net_pnl,
                    'balance_after': balance
                })
                
                position = None
                last_trade_date = current_time
            continue  # Skip nuevas entradas
        
        # Daily loss limit check
        if abs(daily_loss) > daily_loss_limit:
            continue  # Skip trading si se excedió límite diario
        
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
            current_size = position['quantity']
            
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
                
                # Break Even Protection Logic - MÁS AGRESIVO
                if not break_even_moved and profit_points >= break_even_trigger:
                    current_sl = entry_price + 0.5  # BE + 2 ticks para compliance
                    position['current_sl'] = current_sl
                    position['break_even_moved'] = True
                    break_even_moved = True
                
                # Trailing Stop Logic - MÁS CONSERVADOR
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
                
                # Break Even Protection Logic - MÁS AGRESIVO
                if not break_even_moved and profit_points >= break_even_trigger:
                    current_sl = entry_price - 0.5  # BE - 2 ticks para compliance
                    position['current_sl'] = current_sl
                    position['break_even_moved'] = True
                    break_even_moved = True
                
                # Trailing Stop Logic - MÁS CONSERVADOR
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
                    gross_pnl = (exit_price - entry_price) * current_size * 2.0  # MNQ = $2 por punto
                else:
                    gross_pnl = (entry_price - exit_price) * current_size * 2.0  # MNQ = $2 por punto
                
                net_pnl = gross_pnl - (current_size * 1.0)  # Commission variable
                balance += net_pnl
                last_trade_date = current_time
                
                # Update daily loss
                if net_pnl < 0:
                    daily_loss += net_pnl
                    consecutive_losses += 1
                else:
                    consecutive_losses = 0
                
                # Calcular duración en horas
                duration = current_time - entry_time
                duration_hours = duration.total_seconds() / 3600
                
                # Guardar trade
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': current_time,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'direction': direction,
                    'position_size': current_size,
                    'duration_hours': duration_hours,
                    'exit_reason': exit_reason,
                    'net_pnl': net_pnl,
                    'balance_after': balance
                })
                
                position = None
                
                if exit_reason == 'Round Number':
                    logger.info(f"RN: {direction} @ {entry_price} → {exit_price} = ${net_pnl:.2f}")
                elif exit_reason == 'Break Even':
                    logger.info(f"BE: {direction} @ {entry_price} → {exit_price} = ${net_pnl:.2f}")
        
        # Buscar nuevas entradas si no hay posición
        if position is None and current_drawdown < max_drawdown_limit and abs(daily_loss) < daily_loss_limit:
            # Calcular position size dinámico
            current_position_size = get_dynamic_position_size(balance, peak_balance, consecutive_losses)
            
            if row.bullish_cross and not pd.isna(row.bullish_cross) and row.bullish_cross:
                # Entrada LONG
                entry_price = current_price
                tp_points = get_dynamic_tp(entry_price, 'long')
                initial_sl = entry_price - stop_loss_points
                
                position = {
                    'direction': 'long',
                    'entry_price': entry_price,
                    'entry_time': current_time,
                    'quantity': current_position_size,
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
                    'quantity': current_position_size,
                    'current_sl': initial_sl,
                    'tp_points': tp_points,
                    'break_even_moved': False,
                    'trailing_active': False,
                    'max_favorable': entry_price
                }
        
        # Progress cada 10,000 barras
        if i % 10000 == 0:
            logger.info(f"Progreso: {i:,}/{len(df):,} barras ({i/len(df)*100:.1f}%)")
    
    return trades, balance, max_drawdown

def main():
    """Función principal"""
    
    # Cargar datos consolidados CORREGIDOS
    data_file = "/Users/matiasrouaux/Documents/projects/My trading system/backtesting/historical/MNQ_consolidated_2024-2025_CORRECTED.csv"
    
    logger.info(f"Loading: Cargando archivo CORREGIDO: {data_file}")
    df = pd.read_csv(data_file)
    
    # Convertir datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()
    
    # Filtrar solo días de trading (lunes-viernes)
    df = df[df.index.dayofweek < 5]  # 0=Monday, 4=Friday
    
    logger.info(f"Datos cargados: {len(df):,} barras")
    logger.info(f"Período: {df.index.min()} → {df.index.max()}")
    
    # Reset index para trabajar con datetime como columna
    df = df.reset_index()
    
    # Detectar señales
    logger.info("Detectando señales de trading...")
    df = detect_signals(df)
    
    # Ejecutar backtest
    logger.info("Ejecutando Lightning 50K COMPLIANCE VERSION...")
    trades, final_balance, max_drawdown = lightning_compliance_backtest(df)
    
    # Estadísticas finales
    if len(trades) > 0:
        total_trades = len(trades)
        winners = sum(1 for trade in trades if trade['net_pnl'] > 0)
        win_rate = winners / total_trades * 100
        total_pnl = sum(trade['net_pnl'] for trade in trades)
        
        # Análisis por tipo de cierre
        close_reasons = {}
        for trade in trades:
            reason = trade['exit_reason']
            close_reasons[reason] = close_reasons.get(reason, 0) + 1
        
        # ROI calculation
        roi = (total_pnl / 50000) * 100
        
        logger.info("=" * 80)
        logger.info("LIGHTNING 50K - COMPLIANCE VERSION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Período: {df.datetime.min()} → {df.datetime.max()}")
        logger.info(f"Barras procesadas: {len(df):,}")
        logger.info(f"Total trades: {total_trades:,}")
        logger.info(f"Win Rate: {win_rate:.1f}%")
        logger.info(f"PnL total: ${total_pnl:,.2f}")
        logger.info(f"ROI: {roi:.2f}%")
        logger.info(f"Balance final: ${final_balance:,.2f}")
        logger.info(f"Max Drawdown: ${max_drawdown:.2f}")
        logger.info("")
        logger.info("ANÁLISIS POR TIPO DE CIERRE:")
        for reason, count in close_reasons.items():
            logger.info(f"  {reason}: {count} trades")
        logger.info("")
        
        # Verificación Lightning 50K
        lightning_compliant = max_drawdown <= 2000
        logger.info("VERIFICACIÓN LIGHTNING 50K:")
        logger.info(f"Max Drawdown: ${max_drawdown:.2f} / $2,000 {'COMPLIANT ✅' if lightning_compliant else 'VIOLATION ❌'}")
        logger.info(f"Compliance Status: {'✅ APPROVED FOR FUNDING' if lightning_compliant else '❌ NEEDS ADJUSTMENT'}")
        
        if lightning_compliant and roi > 10:
            logger.info("")
            logger.info("🎯 ¡OBJETIVO CUMPLIDO!")
            logger.info("✅ Drawdown compliance")  
            logger.info("✅ ROI > 10%")
            logger.info("✅ Lista para Lightning 50K Challenge")
    
    return trades, final_balance

if __name__ == "__main__":
    trades, final_balance = main()
