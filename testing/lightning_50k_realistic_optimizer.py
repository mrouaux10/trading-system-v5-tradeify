#!/usr/bin/env python3
"""
🎯 OPTIMIZADOR LIGHTNING 50K REALISTA
===================================

Diseña estrategias específicamente para Lightning 50K considerando:
1. Drawdown trailing desde día 1
2. Crecimiento gradual hasta el lock ($52,100)
3. Mayor agresividad después del lock
4. Supervivencia como prioridad #1
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import json
import itertools
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

class LightningRealisticOptimizer:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data = None
        self.results = []
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'lightning_realistic_optimizer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_data(self, data_file: str):
        """Cargar datos de mercado"""
        try:
            if data_file.endswith('.csv'):
                self.data = pd.read_csv(data_file)
                
                # Corregir parsing de timestamp
                if 'datetime' in self.data.columns:
                    self.data['timestamp'] = pd.to_datetime(self.data['datetime'])
                elif 'timestamp' not in self.data.columns:
                    if 'date' in self.data.columns and 'time' in self.data.columns:
                        self.data['timestamp'] = pd.to_datetime(self.data['date'] + ' ' + self.data['time'])
                    else:
                        self.data['timestamp'] = pd.date_range(start='2024-01-01', periods=len(self.data), freq='1min')
            
            # Asegurar columnas OHLC
            required_columns = ['open', 'high', 'low', 'close']
            for col in required_columns:
                if col not in self.data.columns:
                    raise ValueError(f"Columna requerida '{col}' no encontrada")
            
            # Ordenar y limpiar
            self.data = self.data.sort_values('timestamp').reset_index(drop=True)
            self.data = self.data.dropna()
            
            self.logger.info(f"✅ Datos cargados: {len(self.data):,} registros")
            self.logger.info(f"📅 Período: {self.data['timestamp'].min()} a {self.data['timestamp'].max()}")
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando datos: {e}")
            raise
    
    def generate_conservative_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        """
        Generar señales ULTRA-CONSERVADORAS específicamente para Lightning 50K
        Diseñadas para minimizar drawdown y maximizar supervivencia
        """
        
        # Parámetros conservadores
        ma_short = params.get('ma_short', 20)
        ma_long = params.get('ma_long', 50)
        rsi_period = params.get('rsi_period', 14)
        rsi_oversold = params.get('rsi_oversold', 25)  # Más extremo
        rsi_overbought = params.get('rsi_overbought', 75)  # Más extremo
        
        # Filtros adicionales para reducir volatilidad
        volatility_period = params.get('volatility_period', 20)
        max_volatility = params.get('max_volatility', 0.02)  # Máximo 2% de volatilidad
        
        # Calcular indicadores
        data['ma_short'] = data['close'].rolling(window=ma_short).mean()
        data['ma_long'] = data['close'].rolling(window=ma_long).mean()
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        loss = loss.replace(0, 0.0001)
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # Filtro de volatilidad
        data['volatility'] = data['close'].pct_change().rolling(window=volatility_period).std()
        
        # Señales ULTRA-CONSERVADORAS
        data['signal'] = 0
        
        # Condiciones de compra (MUY restrictivas)
        buy_condition = (
            (data['ma_short'] > data['ma_long']) &  # Tendencia alcista
            (data['ma_short'] > data['ma_short'].shift(1)) &  # MA corta subiendo
            (data['rsi'] < rsi_oversold) &  # RSI oversold
            (data['volatility'] < max_volatility) &  # Baja volatilidad
            (data['close'] > data['ma_short'].shift(5))  # Confirmación adicional
        )
        
        # Condiciones de venta (MUY restrictivas)
        sell_condition = (
            (data['ma_short'] < data['ma_long']) &  # Tendencia bajista
            (data['ma_short'] < data['ma_short'].shift(1)) &  # MA corta bajando
            (data['rsi'] > rsi_overbought) &  # RSI overbought
            (data['volatility'] < max_volatility) &  # Baja volatilidad
            (data['close'] < data['ma_short'].shift(5))  # Confirmación adicional
        )
        
        data.loc[buy_condition, 'signal'] = 1
        data.loc[sell_condition, 'signal'] = -1
        
        # Filtrar señales consecutivas del mismo tipo
        for i in range(1, len(data)):
            if data.loc[i, 'signal'] != 0 and data.loc[i, 'signal'] == data.loc[i-1, 'signal']:
                data.loc[i, 'signal'] = 0
        
        return data
    
    def backtest_lightning_realistic(self, data: pd.DataFrame, params: dict) -> dict:
        """
        Backtest específico para Lightning 50K con todas las reglas reales
        """
        
        # Estado inicial
        balance = 50000
        position = 0
        trades = []
        daily_balances = []
        
        # Lightning 50K tracking
        peak_balance = 50000
        drawdown_level = 48000  # $50K - $2K
        is_locked = False
        locked_drawdown_level = None
        
        # Compliance tracking
        trading_days = 0
        daily_loss_limit = 1250
        consistency_rule_profits = 0
        best_day_profit = 0
        
        # Procesar por días
        data['date'] = data['timestamp'].dt.date
        
        for current_date, day_data in data.groupby('date'):
            day_data = day_data.reset_index(drop=True)
            balance_start = balance
            daily_trades = 0
            
            # Verificar si es día de trading válido
            if len(day_data) == 0:
                continue
            
            # Procesar cada minuto del día
            for _, row in day_data.iterrows():
                signal = row['signal']
                price = row['close']
                
                # Ejecutar trades basados en señales
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
                    
                    # Abrir long (tamaño adaptativo basado en balance)
                    if balance < 52100:  # Pre-lock: ultra conservador
                        contracts = 1
                    else:  # Post-lock: más agresivo
                        contracts = min(2, 5)  # Máximo 5 por reglas Lightning
                    
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
                    
                    # Abrir short (tamaño adaptativo)
                    if balance < 52100:  # Pre-lock: ultra conservador
                        contracts = 1
                    else:  # Post-lock: más agresivo
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
                
                # Verificar Daily Loss Limit en tiempo real
                daily_loss = balance_start - balance
                if daily_loss > daily_loss_limit:
                    # Cerrar todas las posiciones por DLL
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
            
            # Cálculos EOD (End of Day)
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
                        self.logger.info(f"🔒 DRAWDOWN LOCKED at ${drawdown_level:,.0f} on {current_date}")
            
            # Verificar eliminación por drawdown
            if balance < drawdown_level:
                self.logger.warning(f"❌ DRAWDOWN VIOLATION: Balance ${balance:,.0f} < Level ${drawdown_level:,.0f}")
                return {
                    'is_compliant': False,
                    'elimination_reason': f'Drawdown violation on {current_date}',
                    'elimination_day': len(daily_balances) + 1,
                    'final_balance': balance,
                    'total_pnl': balance - 50000,
                    'total_trades': len(trades),
                    'trading_days': trading_days,
                    'peak_reached': peak_balance,
                    'daily_balances': daily_balances
                }
            
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
                compliance_issues.append(f'Consistency rule violation: {best_day_profit:.0f} best day requires {required_profits_for_best_day:.0f} total profits, but only have {consistency_rule_profits:.0f}')
        
        # Final result
        is_compliant = len(compliance_issues) == 0
        
        return {
            'is_compliant': is_compliant,
            'elimination_reason': '; '.join(compliance_issues) if compliance_issues else '',
            'final_balance': balance,
            'total_pnl': balance - 50000,
            'total_trades': len(trades),
            'trading_days': trading_days,
            'peak_reached': peak_balance,
            'is_locked': is_locked,
            'locked_at_balance': balance if is_locked else None,
            'daily_balances': daily_balances,
            'trades': trades,
            'consistency_profits': consistency_rule_profits,
            'best_day_profit': best_day_profit
        }
    
    def optimize_single_strategy(self, params_combo):
        """Optimizar una combinación de parámetros"""
        try:
            params = {
                'ma_short': params_combo[0],
                'ma_long': params_combo[1], 
                'rsi_period': params_combo[2],
                'rsi_oversold': params_combo[3],
                'rsi_overbought': params_combo[4],
                'volatility_period': params_combo[5],
                'max_volatility': params_combo[6],
                'id': hash(params_combo) % 10000
            }
            
            # Generar señales
            data_with_signals = self.generate_conservative_signals(self.data.copy(), params)
            
            # Backtest
            result = self.backtest_lightning_realistic(data_with_signals, params)
            
            if result['is_compliant']:
                result['strategy_name'] = f"LightningRealistic_{params['id']}"
                result['strategy_params'] = params
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error en optimización: {e}")
            return None
    
    def run_optimization(self):
        """Ejecutar optimización completa"""
        
        self.logger.info("🚀 Iniciando optimización Lightning 50K Realista...")
        
        # Cargar datos
        self.load_data(self.data_file)
        
        # Parámetros ULTRA-CONSERVADORES para supervivencia
        param_ranges = {
            'ma_short': [10, 15, 20, 25, 30],  # MAs más largas para menos señales
            'ma_long': [50, 75, 100, 150, 200],  # MAs muy largas para filtrado
            'rsi_period': [14, 21, 28],  # RSI estándar a más largo
            'rsi_oversold': [20, 25, 30],  # Más extremo para menos trades
            'rsi_overbought': [70, 75, 80],  # Más extremo para menos trades
            'volatility_period': [10, 20, 30],  # Períodos de volatilidad
            'max_volatility': [0.01, 0.015, 0.02, 0.025]  # Límites de volatilidad muy bajos
        }
        
        # Generar todas las combinaciones
        param_combinations = list(itertools.product(*param_ranges.values()))
        
        self.logger.info(f"📊 Probando {len(param_combinations):,} combinaciones...")
        
        # Optimización paralela
        compliant_strategies = []
        
        # Usar menos procesos para evitar sobrecarga
        max_workers = min(mp.cpu_count() - 1, 4)
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self.optimize_single_strategy, param_combinations)
            
            for i, result in enumerate(results, 1):
                if i % 100 == 0:
                    self.logger.info(f"📈 Progreso: {i:,}/{len(param_combinations):,} ({i/len(param_combinations)*100:.1f}%)")
                
                if result and result['is_compliant']:
                    compliant_strategies.append(result)
                    self.logger.info(f"✅ Estrategia compliant encontrada: {result['strategy_name']}")
                    self.logger.info(f"   💰 PnL: ${result['total_pnl']:,.0f}")
                    self.logger.info(f"   📊 Trades: {result['total_trades']:,}")
                    self.logger.info(f"   🔒 Locked: {result['is_locked']}")
        
        # Guardar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f'lightning_realistic_results_{timestamp}.json'
        
        final_results = {
            'timestamp': timestamp,
            'total_combinations_tested': len(param_combinations),
            'compliant_strategies_found': len(compliant_strategies),
            'compliant_strategies': compliant_strategies
        }
        
        with open(results_file, 'w') as f:
            json.dump(final_results, f, indent=2)
        
        self.logger.info(f"✅ Optimización completada!")
        self.logger.info(f"📊 Estrategias compliant encontradas: {len(compliant_strategies)}")
        self.logger.info(f"💾 Resultados guardados en: {results_file}")
        
        return final_results

if __name__ == "__main__":
    # Ejecutar optimizador
    data_file = "../backtesting/historical/MNQ_consolidated_2024-2025.csv"
    
    optimizer = LightningRealisticOptimizer(data_file)
    results = optimizer.run_optimization()
