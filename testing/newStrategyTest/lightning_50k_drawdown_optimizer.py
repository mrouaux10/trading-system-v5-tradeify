#!/usr/bin/env python3
"""
Lightning 50K - Optimizador de Drawdown
======================================
Optimiza parámetros para reducir drawdown manteniendo rentabilidad
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path
import itertools

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

def round_numbers_strategy_backtest(df, params):
    """Ejecutar backtest con parámetros específicos"""
    
    # Configuración Lightning 50K
    initial_balance = 50000
    balance = initial_balance
    position = None
    position_size = 1
    commission = 1.0
    
    # Parámetros del sistema BE Protection
    stop_loss_points = params['stop_loss_points']
    break_even_trigger = params['break_even_trigger'] 
    trailing_trigger = params['trailing_trigger']
    trailing_distance = params['trailing_distance']
    tp_near_rn = params['tp_near_rn']
    tp_normal = params['tp_normal']
    
    # Listas para almacenar trades
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
        """TP dinámico"""
        if is_near_round_number(entry_price):
            return tp_near_rn
        return tp_normal
    
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
    
    return trades, balance, max_drawdown

def optimize_parameters(df):
    """Optimizar parámetros para reducir drawdown"""
    
    logger.info("🔍 INICIANDO OPTIMIZACIÓN DE DRAWDOWN...")
    
    # Parámetros base actuales
    base_params = {
        'stop_loss_points': 1.5,
        'break_even_trigger': 2.5,
        'trailing_trigger': 6.0,
        'trailing_distance': 4.0,
        'tp_near_rn': 28,
        'tp_normal': 18
    }
    
    # Rangos de optimización - MÁS DEFENSIVOS
    param_ranges = {
        'stop_loss_points': [1.0, 1.25, 1.5],  # SL más tight
        'break_even_trigger': [1.5, 2.0, 2.5],  # BE más rápido
        'trailing_trigger': [4.0, 5.0, 6.0],    # Trailing más rápido
        'trailing_distance': [3.0, 3.5, 4.0],   # Trailing más tight
        'tp_near_rn': [22, 25, 28],             # TP más conservador
        'tp_normal': [15, 18, 20]               # TP más conservador
    }
    
    best_params = None
    best_metrics = None
    target_drawdown = 1600  # Objetivo: reducir drawdown a $1600 (20% margen)
    
    # Generar todas las combinaciones
    param_names = list(param_ranges.keys())
    param_values = list(param_ranges.values())
    combinations = list(itertools.product(*param_values))
    
    logger.info(f"🔬 Evaluando {len(combinations)} combinaciones de parámetros...")
    
    results = []
    
    for i, combination in enumerate(combinations):
        params = dict(zip(param_names, combination))
        
        try:
            # Ejecutar backtest
            trades, final_balance, max_drawdown = round_numbers_strategy_backtest(df, params)
            
            if len(trades) > 0:
                # Calcular métricas
                pnl_values = [trade['net_pnl'] for trade in trades]
                total_pnl = sum(pnl_values)
                winners = sum(1 for pnl in pnl_values if pnl > 0)
                win_rate = winners / len(trades) * 100
                
                # Score combinado: priorizar reducción de drawdown
                drawdown_score = max(0, 2000 - max_drawdown) / 2000 * 100  # Mayor score = menor drawdown
                profit_score = max(0, total_pnl) / 1000  # Mantener rentabilidad
                trade_freq_score = len(trades) / 100  # Mantener frecuencia
                
                # Score ponderado - PRIORIDAD A REDUCIR DRAWDOWN
                combined_score = (drawdown_score * 0.6) + (profit_score * 0.25) + (trade_freq_score * 0.15)
                
                metrics = {
                    'params': params,
                    'total_trades': len(trades),
                    'total_pnl': total_pnl,
                    'final_balance': final_balance,
                    'max_drawdown': max_drawdown,
                    'win_rate': win_rate,
                    'drawdown_score': drawdown_score,
                    'combined_score': combined_score
                }
                
                results.append(metrics)
                
                # Logging cada 20 combinaciones
                if i % 20 == 0:
                    logger.info(f"🔬 Progreso: {i+1}/{len(combinations)} - Mejor drawdown: ${min([r['max_drawdown'] for r in results]):.2f}")
        
        except Exception as e:
            logger.warning(f"⚠️ Error en combinación {i+1}: {e}")
            continue
    
    if not results:
        logger.error("❌ No se encontraron resultados válidos")
        return None
    
    # Ordenar por score combinado
    results.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # Mostrar top 5 mejores
    logger.info("\n🏆 TOP 5 MEJORES CONFIGURACIONES:")
    logger.info("=" * 100)
    
    for i, result in enumerate(results[:5]):
        logger.info(f"\n#{i+1} CONFIGURACIÓN:")
        logger.info(f"  📊 Drawdown: ${result['max_drawdown']:.2f} ({2000-result['max_drawdown']:.2f} margen)")
        logger.info(f"  💰 PnL: ${result['total_pnl']:.2f}")
        logger.info(f"  🔢 Trades: {result['total_trades']:,}")
        logger.info(f"  🏆 Win Rate: {result['win_rate']:.1f}%")
        logger.info(f"  📈 Score: {result['combined_score']:.2f}")
        logger.info(f"  ⚙️ Parámetros:")
        for param, value in result['params'].items():
            logger.info(f"    {param}: {value}")
    
    # Seleccionar la mejor configuración
    best_result = results[0]
    
    logger.info("\n" + "=" * 80)
    logger.info("🎯 CONFIGURACIÓN SELECCIONADA:")
    logger.info("=" * 80)
    logger.info(f"📊 Drawdown actual: $1,812.75")
    logger.info(f"📊 Drawdown optimizado: ${best_result['max_drawdown']:.2f}")
    logger.info(f"📈 Mejora en drawdown: ${1812.75 - best_result['max_drawdown']:.2f}")
    logger.info(f"💰 PnL actual: $135,804.50")
    logger.info(f"💰 PnL optimizado: ${best_result['total_pnl']:.2f}")
    logger.info(f"📊 Trades actual: 14,078")
    logger.info(f"📊 Trades optimizado: {best_result['total_trades']:,}")
    
    improvement = 1812.75 - best_result['max_drawdown']
    if improvement > 100:
        logger.info(f"\n✅ OPTIMIZACIÓN EXITOSA: Reducción de ${improvement:.2f} en drawdown")
        return best_result
    else:
        logger.info(f"\n⚠️ MEJORA MARGINAL: Solo ${improvement:.2f} de reducción")
        return None

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
    
    # Ejecutar optimización
    best_result = optimize_parameters(df)
    
    if best_result:
        logger.info("\n🚀 APLICANDO PARÁMETROS OPTIMIZADOS...")
        
        # Crear archivo con los nuevos parámetros
        optimized_config = {
            "strategy_name": "Lightning 50K - Optimized Drawdown",
            "optimization_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "parameters": best_result['params'],
            "performance": {
                "total_trades": best_result['total_trades'],
                "total_pnl": best_result['total_pnl'],
                "max_drawdown": best_result['max_drawdown'],
                "win_rate": best_result['win_rate'],
                "final_balance": best_result['final_balance']
            },
            "improvement": {
                "drawdown_reduction": 1812.75 - best_result['max_drawdown'],
                "compliance_margin": 2000 - best_result['max_drawdown']
            }
        }
        
        # Guardar configuración optimizada
        import json
        config_file = 'results/lightning_50k_optimized_drawdown_config.json'
        with open(config_file, 'w') as f:
            json.dump(optimized_config, f, indent=2)
        
        logger.info(f"💾 Configuración guardada: {config_file}")
        
        return best_result
    else:
        logger.info("\n⚠️ No se encontró una mejora significativa en el drawdown")
        logger.info("💡 Recomendación: Mantener parámetros actuales")
        return None

if __name__ == "__main__":
    result = main()
