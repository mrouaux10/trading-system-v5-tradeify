#!/usr/bin/env python3
"""
🎯 BUSCADOR DE ESTRATEGIA PERFECTA LIGHTNING 50K
==============================================

Encuentra la estrategia exacta que generó 54 trades y $29,140 PnL
usando ingeniería inversa ultra-precisa de los logs del optimizador.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import logging
import itertools
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

class LightningPerfectStrategyFinder:
    def __init__(self):
        self.data = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, data_file: str):
        """Cargar datos de mercado"""
        try:
            self.data = pd.read_csv(data_file)
            
            if 'datetime' in self.data.columns:
                self.data['timestamp'] = pd.to_datetime(self.data['datetime'])
            elif 'timestamp' not in self.data.columns:
                if 'date' in self.data.columns and 'time' in self.data.columns:
                    self.data['timestamp'] = pd.to_datetime(self.data['date'] + ' ' + self.data['time'])
                else:
                    self.data['timestamp'] = pd.date_range(start='2024-01-01', periods=len(self.data), freq='1min')
            
            self.data = self.data.sort_values('timestamp').reset_index(drop=True)
            self.data = self.data.dropna()
            
            self.logger.info(f"✅ Datos cargados: {len(self.data):,} registros")
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando datos: {e}")
            raise
    
    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        """Generar señales con parámetros específicos"""
        
        # Calcular indicadores
        data['ma_short'] = data['close'].rolling(window=params['ma_short']).mean()
        data['ma_long'] = data['close'].rolling(window=params['ma_long']).mean()
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=params['rsi_period']).mean()
        loss = loss.replace(0, 0.0001)
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # Filtro de volatilidad
        data['volatility'] = data['close'].pct_change().rolling(window=params['volatility_period']).std()
        
        # Señales ultra-conservadoras
        data['signal'] = 0
        
        # Condiciones de compra EXTREMADAMENTE restrictivas
        buy_condition = (
            (data['ma_short'] > data['ma_long']) &  # Tendencia alcista
            (data['ma_short'] > data['ma_short'].shift(1)) &  # MA corta subiendo
            (data['rsi'] < params['rsi_oversold']) &  # RSI oversold
            (data['volatility'] < params['max_volatility']) &  # Baja volatilidad
            (data['close'] > data['ma_short'].shift(5))  # Confirmación adicional
        )
        
        # Condiciones de venta EXTREMADAMENTE restrictivas
        sell_condition = (
            (data['ma_short'] < data['ma_long']) &  # Tendencia bajista
            (data['ma_short'] < data['ma_short'].shift(1)) &  # MA corta bajando
            (data['rsi'] > params['rsi_overbought']) &  # RSI overbought
            (data['volatility'] < params['max_volatility']) &  # Baja volatilidad
            (data['close'] < data['ma_short'].shift(5))  # Confirmación adicional
        )
        
        data.loc[buy_condition, 'signal'] = 1
        data.loc[sell_condition, 'signal'] = -1
        
        # Filtrar señales consecutivas
        for i in range(1, len(data)):
            if data.loc[i, 'signal'] != 0 and data.loc[i, 'signal'] == data.loc[i-1, 'signal']:
                data.loc[i, 'signal'] = 0
        
        return data
    
    def backtest_strategy(self, data: pd.DataFrame) -> dict:
        """Backtest con validación Lightning 50K exacta"""
        
        balance = 50000
        position = 0
        trades = []
        daily_balances = []
        
        peak_balance = 50000
        drawdown_level = 48000
        is_locked = False
        lock_date = None
        
        # Compliance tracking
        trading_days = 0
        consistency_rule_profits = 0
        best_day_profit = 0
        
        data['date'] = data['timestamp'].dt.date
        
        for current_date, day_data in data.groupby('date'):
            day_data = day_data.reset_index(drop=True)
            balance_start = balance
            daily_trades = 0
            
            if len(day_data) == 0:
                continue
            
            # Procesar cada minuto del día
            for _, row in day_data.iterrows():
                signal = row['signal']
                price = row['close']
                
                # Ejecutar trades
                if signal == 1 and position <= 0:  # Buy signal
                    if position < 0:  # Cerrar short
                        entry_price = trades[-1]['entry_price'] if trades else price
                        pnl = abs(position) * (entry_price - price) * 20
                        balance += pnl
                        trades.append({
                            'timestamp': row['timestamp'],
                            'type': 'close_short',
                            'price': price,
                            'quantity': abs(position),
                            'pnl': pnl,
                            'entry_price': entry_price
                        })
                        daily_trades += 1
                        position = 0
                    
                    # Tamaño adaptativo
                    if balance < 52100:  # Pre-lock: ultra conservador
                        contracts = 1
                    else:  # Post-lock: más agresivo
                        contracts = min(2, 5)
                    
                    position = contracts
                    trades.append({
                        'timestamp': row['timestamp'],
                        'type': 'open_long',
                        'price': price,
                        'quantity': contracts,
                        'pnl': 0,
                        'entry_price': price
                    })
                    daily_trades += 1
                
                elif signal == -1 and position >= 0:  # Sell signal
                    if position > 0:  # Cerrar long
                        entry_price = trades[-1]['entry_price'] if trades else price
                        pnl = position * (price - entry_price) * 20
                        balance += pnl
                        trades.append({
                            'timestamp': row['timestamp'],
                            'type': 'close_long',
                            'price': price,
                            'quantity': position,
                            'pnl': pnl,
                            'entry_price': entry_price
                        })
                        daily_trades += 1
                        position = 0
                    
                    # Tamaño adaptativo
                    if balance < 52100:
                        contracts = 1
                    else:
                        contracts = min(2, 5)
                    
                    position = -contracts
                    trades.append({
                        'timestamp': row['timestamp'],
                        'type': 'open_short',
                        'price': price,
                        'quantity': contracts,
                        'pnl': 0,
                        'entry_price': price
                    })
                    daily_trades += 1
                
                # Verificar Daily Loss Limit
                daily_loss = balance_start - balance
                if daily_loss > 1250:
                    # Cerrar posiciones por DLL
                    if position != 0:
                        last_price = price
                        entry_price = trades[-1]['entry_price'] if trades else last_price
                        
                        if position > 0:
                            pnl = position * (last_price - entry_price) * 20
                        else:
                            pnl = abs(position) * (entry_price - last_price) * 20
                        
                        balance += pnl
                        trades.append({
                            'timestamp': row['timestamp'],
                            'type': 'dll_close',
                            'price': last_price,
                            'quantity': abs(position),
                            'pnl': pnl,
                            'entry_price': entry_price
                        })
                        position = 0
                    break  # Parar trading por el día
            
            # Cerrar posiciones al final del día (regla overnight)
            if position != 0:
                last_price = day_data.iloc[-1]['close']
                entry_price = trades[-1]['entry_price'] if trades else last_price
                
                if position > 0:
                    pnl = position * (last_price - entry_price) * 20
                else:
                    pnl = abs(position) * (entry_price - last_price) * 20
                
                balance += pnl
                trades.append({
                    'timestamp': day_data.iloc[-1]['timestamp'],
                    'type': 'eod_close',
                    'price': last_price,
                    'quantity': abs(position),
                    'pnl': pnl,
                    'entry_price': entry_price
                })
                daily_trades += 1
                position = 0
            
            # Cálculos EOD
            daily_pnl = balance - balance_start
            
            # Actualizar peak y drawdown level
            if balance > peak_balance:
                peak_balance = balance
                if not is_locked:
                    drawdown_level = peak_balance - 2000
                    
                    # Verificar lock
                    if balance >= 52100 and not is_locked:
                        is_locked = True
                        locked_drawdown_level = 50100
                        drawdown_level = locked_drawdown_level
                        lock_date = current_date
            
            # Verificar eliminación por drawdown
            if balance < drawdown_level:
                return None  # Estrategia eliminada
            
            # Tracking consistency rule
            if daily_pnl > 0:
                consistency_rule_profits += daily_pnl
                best_day_profit = max(best_day_profit, daily_pnl)
            
            # Contar días de trading
            if daily_trades > 0:
                trading_days += 1
            
            # Guardar balance diario
            daily_balances.append({
                'date': str(current_date),
                'balance': balance,
                'daily_pnl': daily_pnl,
                'trades_count': daily_trades,
                'peak_balance': peak_balance,
                'drawdown_level': drawdown_level,
                'is_locked': is_locked
            })
        
        # Verificar compliance final
        compliance_issues = []
        
        # Minimum trading days
        if trading_days < 7:
            compliance_issues.append(f'Insufficient trading days: {trading_days} < 7')
        
        # Consistency rule (20%)
        if consistency_rule_profits > 0:
            required_profits_for_best_day = best_day_profit / 0.20
            if consistency_rule_profits < required_profits_for_best_day:
                compliance_issues.append(f'Consistency rule violation')
        
        # Final result
        is_compliant = len(compliance_issues) == 0
        
        if not is_compliant:
            return None
        
        return {
            'final_balance': balance,
            'total_pnl': balance - 50000,
            'total_trades': len(trades),
            'is_locked': is_locked,
            'lock_date': str(lock_date) if lock_date else None,
            'peak_reached': peak_balance,
            'trading_days': trading_days,
            'daily_balances': daily_balances,
            'trades': trades,
            'consistency_profits': consistency_rule_profits,
            'best_day_profit': best_day_profit
        }
    
    def test_single_combination(self, params_combo):
        """Probar una combinación específica de parámetros"""
        try:
            params = {
                'ma_short': params_combo[0],
                'ma_long': params_combo[1],
                'rsi_period': params_combo[2],
                'rsi_oversold': params_combo[3],
                'rsi_overbought': params_combo[4],
                'volatility_period': params_combo[5],
                'max_volatility': params_combo[6]
            }
            
            # Generar señales
            data_with_signals = self.generate_signals(self.data.copy(), params)
            
            # Backtest
            result = self.backtest_strategy(data_with_signals)
            
            if result:
                return {
                    'params': params,
                    'result': result,
                    'match_score': self.calculate_match_score(result)
                }
            
            return None
            
        except Exception as e:
            return None
    
    def calculate_match_score(self, result):
        """Calcular qué tan cerca está del resultado target (54 trades, $29,140)"""
        target_trades = 54
        target_pnl = 29140
        
        trades_diff = abs(result['total_trades'] - target_trades)
        pnl_diff = abs(result['total_pnl'] - target_pnl)
        
        # Penalizar más las diferencias en trades que en PnL
        score = 1000 - (trades_diff * 10) - (pnl_diff / 100)
        
        return score
    
    def find_perfect_strategy(self):
        """Buscar la estrategia perfecta que coincida exactamente"""
        
        self.logger.info("🎯 Buscando la estrategia PERFECTA Lightning 50K...")
        
        # Cargar datos
        data_file = "../backtesting/historical/MNQ_consolidated_2024-2025.csv"
        self.load_data(data_file)
        
        # Rangos ultra-específicos basados en que encontramos 12 estrategias idénticas
        # Esto sugiere que hay parámetros muy específicos que funcionan
        param_ranges = {
            'ma_short': [10, 15, 20, 25, 30],
            'ma_long': [50, 75, 100, 150, 200],
            'rsi_period': [14, 21, 28],
            'rsi_oversold': [20, 25, 30],
            'rsi_overbought': [70, 75, 80],
            'volatility_period': [10, 20, 30],
            'max_volatility': [0.01, 0.015, 0.02, 0.025]
        }
        
        # Generar todas las combinaciones
        combinations = list(itertools.product(*param_ranges.values()))
        
        self.logger.info(f"🔍 Probando {len(combinations):,} combinaciones ultra-específicas...")
        
        # Búsqueda paralela
        successful_strategies = []
        
        # Usar menos workers para evitar sobrecarga
        max_workers = min(mp.cpu_count() - 1, 4)
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self.test_single_combination, combinations)
            
            for i, result in enumerate(results, 1):
                if i % 100 == 0:
                    self.logger.info(f"📈 Progreso: {i:,}/{len(combinations):,} ({i/len(combinations)*100:.1f}%)")
                
                if result:
                    successful_strategies.append(result)
                    
                    trades = result['result']['total_trades']
                    pnl = result['result']['total_pnl']
                    locked = result['result']['is_locked']
                    score = result['match_score']
                    
                    self.logger.info(f"✅ Estrategia encontrada!")
                    self.logger.info(f"   📊 Trades: {trades} (target: 54)")
                    self.logger.info(f"   💰 PnL: ${pnl:,.0f} (target: $29,140)")
                    self.logger.info(f"   🔒 Locked: {locked}")
                    self.logger.info(f"   🎯 Match Score: {score:.1f}")
                    
                    # Si encontramos una coincidencia perfecta, parar
                    if trades == 54 and 25000 <= pnl <= 35000 and locked:
                        self.logger.info("🎉 ¡COINCIDENCIA PERFECTA ENCONTRADA!")
                        break
        
        # Ordenar por match score
        successful_strategies.sort(key=lambda x: x['match_score'], reverse=True)
        
        self.logger.info(f"✅ Búsqueda completada!")
        self.logger.info(f"📊 Estrategias exitosas encontradas: {len(successful_strategies)}")
        
        if successful_strategies:
            # Analizar la mejor estrategia
            best_strategy = successful_strategies[0]
            self.analyze_perfect_strategy(best_strategy)
            
            # Guardar todas las estrategias exitosas
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'lightning_perfect_strategies_{timestamp}.json'
            
            # Convertir timestamps para JSON
            def convert_timestamps(obj):
                if isinstance(obj, dict):
                    return {k: convert_timestamps(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_timestamps(item) for item in obj]
                elif hasattr(obj, 'isoformat'):  # datetime/timestamp objects
                    return obj.isoformat()
                else:
                    return obj
            
            strategies_data = {
                'timestamp': timestamp,
                'total_combinations_tested': len(combinations),
                'successful_strategies_found': len(successful_strategies),
                'best_strategy': convert_timestamps(best_strategy),
                'all_strategies': convert_timestamps(successful_strategies[:10])  # Top 10
            }
            
            with open(filename, 'w') as f:
                json.dump(strategies_data, f, indent=2)
            
            self.logger.info(f"💾 Estrategias perfectas guardadas en: {filename}")
            
            return best_strategy
        else:
            self.logger.warning("❌ No se encontraron estrategias exitosas")
            return None
    
    def analyze_perfect_strategy(self, strategy_data):
        """Analizar la estrategia perfecta encontrada"""
        
        params = strategy_data['params']
        result = strategy_data['result']
        
        print("="*80)
        print("🎯 ESTRATEGIA PERFECTA LIGHTNING 50K - LISTA PARA USAR")
        print("="*80)
        
        print(f"\n💰 RENDIMIENTO FINANCIERO:")
        print("-" * 40)
        print(f"   Balance inicial: $50,000")
        print(f"   Balance final: ${result['final_balance']:,.0f}")
        print(f"   PnL total: ${result['total_pnl']:,.0f}")
        print(f"   Return total: {(result['final_balance']/50000-1)*100:.1f}%")
        print(f"   Return mensual promedio: {((result['final_balance']/50000-1)*100)/19:.1f}%")
        print(f"   PnL mensual promedio: ${result['total_pnl']/19:,.0f}")
        
        print(f"\n📊 ESTADÍSTICAS DE TRADING:")
        print("-" * 40)
        print(f"   Total trades: {result['total_trades']:,}")
        print(f"   Días de trading: {result['trading_days']}")
        print(f"   Trades por mes: {result['total_trades']/19:.1f}")
        print(f"   Peak alcanzado: ${result['peak_reached']:,.0f}")
        print(f"   ¿Llegó al lock?: {'✅ SÍ' if result['is_locked'] else '❌ NO'}")
        if result['lock_date']:
            print(f"   Fecha del lock: {result['lock_date']}")
        
        print(f"\n⚙️ PARÁMETROS EXACTOS PARA TU BOT:")
        print("="*80)
        print(f"   MA Rápida (Short): {params['ma_short']}")
        print(f"   MA Lenta (Long): {params['ma_long']}")
        print(f"   RSI Período: {params['rsi_period']}")
        print(f"   RSI Oversold: {params['rsi_oversold']}")
        print(f"   RSI Overbought: {params['rsi_overbought']}")
        print(f"   Volatilidad Período: {params['volatility_period']}")
        print(f"   Volatilidad Máxima: {params['max_volatility']}")
        
        print(f"\n🎯 CONFIGURACIÓN PARA IMPLEMENTACIÓN REAL:")
        print("="*80)
        print(f"   ✅ Tamaño Pre-Lock: 1 contrato máximo")
        print(f"   ✅ Tamaño Post-Lock: 2-3 contratos máximo")
        print(f"   ✅ Daily Loss Limit: $1,250 (usar $1,000 como límite seguro)")
        print(f"   ✅ Stop Loss diario: $800 conservador")
        print(f"   ✅ Horario: 6:00 PM - 4:59 PM ET únicamente")
        print(f"   ✅ Cierre EOD: Obligatorio (sin overnight)")
        
        print(f"\n📈 EXPECTATIVAS REALISTAS:")
        print("-" * 40)
        print(f"   💰 Ganancia mensual esperada: ${result['total_pnl']/19:,.0f}")
        print(f"   📊 Return mensual esperado: {((result['final_balance']/50000-1)*100)/19:.1f}%")
        print(f"   🎯 Trades esperados por mes: {result['total_trades']/19:.0f}")
        print(f"   ⏱️ Actividad: Muy baja (ultra-conservador)")
        print(f"   🔒 Objetivo principal: Llegar al lock ($52,100)")
        
        print(f"\n🚨 RECORDATORIOS CRÍTICOS:")
        print("="*80)
        print(f"   ⚠️ NUNCA violar drawdown de $2,000 desde peak")
        print(f"   ⚠️ NUNCA exceder Daily Loss Limit de $1,250")
        print(f"   ⚠️ SIEMPRE cerrar posiciones antes de 5:00 PM ET")
        print(f"   ⚠️ MONITOREAR balance diario religiosamente")
        print(f"   ⚠️ Una vez locked, más libertad pero mantener disciplina")

if __name__ == "__main__":
    finder = LightningPerfectStrategyFinder()
    perfect_strategy = finder.find_perfect_strategy()
