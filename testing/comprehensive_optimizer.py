#!/usr/bin/env python3
"""
Optimizador Completo de Estrategia
==================================

Optimiza TODOS los aspectos de la estrategia:
- Horarios de trading
- Sentidos de operación (long/short)
- Parámetros de indicadores
- Filtros adicionales
- Estrategias alternativas

Uso:
    python3 comprehensive_optimizer.py          # Optimización completa
    python3 comprehensive_optimizer.py --test   # Modo de prueba (más rápido)
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from itertools import product
import json
import argparse

# Importar el cargador de datos
from .ninjatrader_data_loader import NinjaTraderDataLoader

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveOptimizer:
    """Optimizador completo de estrategia"""
    
    def __init__(self, test_mode=False):
        """Inicializar optimizador"""
        self.data = None
        self.results = []
        self.best_results = []
        self.test_mode = test_mode
        
        if test_mode:
            logger.info("🧪 MODO DE PRUEBA ACTIVADO - Optimización reducida para pruebas rápidas")
        else:
            logger.info("🚀 MODO COMPLETO - Optimización exhaustiva de todos los parámetros")
    
    def load_data(self):
        """Cargar datos"""
        try:
            logger.info("📥 Cargando datos...")
            
            loader = NinjaTraderDataLoader()
            data_file = 'testing/MNQ_09-25_30days_1min.txt'
            
            if not loader.load_from_txt(data_file):
                logger.error("❌ Error cargando datos")
                return False
            
            # Obtener datos filtrados
            self.data = loader.filter_trading_hours()
            
            if self.data is None or len(self.data) == 0:
                logger.error("❌ No hay datos de trading")
                return False
            
            logger.info(f"✅ Datos cargados: {len(self.data)} barras")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            return False
    
    def calculate_indicators(self, data):
        """Calcular indicadores técnicos"""
        try:
            # EMA 34
            data['ema_34'] = data['Close'].ewm(span=34).mean()
            
            # RSI 14
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi_14'] = 100 - (100 / (1 + rs))
            
            # ATR 14
            high = data['High']
            low = data['Low']
            close = data['Close']
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            data['atr_14'] = tr.rolling(window=14).mean()
            
            # Volume SMA
            data['volume_sma'] = data['Volume'].rolling(window=20).mean()
            
            # Precio vs EMA
            data['price_vs_ema'] = data['Close'] - data['ema_34']
            data['ema_crossover_strength'] = data['price_vs_ema'].abs() / data['Close'] * 100
            
            # Indicadores adicionales
            data['ema_8'] = data['Close'].ewm(span=8).mean()
            data['ema_21'] = data['Close'].ewm(span=21).mean()
            data['sma_50'] = data['Close'].rolling(window=50).mean()
            
            # Volatilidad
            data['volatility'] = data['Close'].rolling(window=20).std()
            
            # Momentum
            data['momentum'] = data['Close'] - data['Close'].shift(5)
            
            return data.dropna()
            
        except Exception as e:
            logger.error(f"❌ Error calculando indicadores: {e}")
            return None
    
    def filter_by_time(self, data, start_hour=9, end_hour=16):
        """Filtrar por horario de trading"""
        try:
            filtered = data[
                (data.index.hour >= start_hour) & 
                (data.index.hour < end_hour)
            ].copy()
            return filtered
        except Exception as e:
            logger.error(f"❌ Error filtrando por tiempo: {e}")
            return data
    
    def check_long_signal(self, data, i, params):
        """Verificar señal de compra (long)"""
        try:
            if i < 1:
                return False
                
            bar = data.iloc[i]
            prev_bar = data.iloc[i-1]
            
            # EMA crossover (precio cruza por encima de EMA)
            ema_crossover = (float(prev_bar['Close']) <= float(prev_bar['ema_34']) and 
                           float(bar['Close']) > float(bar['ema_34']))
            
            if not ema_crossover:
                return False
            
            # RSI
            rsi_ok = float(bar['rsi_14']) < params['rsi_max']
            
            # ATR
            atr_threshold = float(bar['Close']) * params['atr_threshold_multiplier']
            atr_ok = float(bar['atr_14']) > atr_threshold
            
            # Volume
            volume_ok = float(bar['Volume']) > (float(bar['volume_sma']) * params['volume_threshold'])
            
            # EMA strength
            ema_strength_ok = float(bar['ema_crossover_strength']) >= params['min_ema_crossover_strength']
            
            # Momentum
            momentum_ok = float(bar['Close']) > float(bar['ema_34'])
            
            return all([ema_crossover, rsi_ok, atr_ok, volume_ok, ema_strength_ok, momentum_ok])
            
        except Exception as e:
            return False
    
    def check_short_signal(self, data, i, params):
        """Verificar señal de venta (short)"""
        try:
            if i < 1:
                return False
                
            bar = data.iloc[i]
            prev_bar = data.iloc[i-1]
            
            # EMA crossover (precio cruza por debajo de EMA)
            ema_crossover = (float(prev_bar['Close']) >= float(prev_bar['ema_34']) and 
                           float(bar['Close']) < float(bar['ema_34']))
            
            if not ema_crossover:
                return False
            
            # RSI
            rsi_ok = float(bar['rsi_14']) > params['rsi_min']
            
            # ATR
            atr_threshold = float(bar['Close']) * params['atr_threshold_multiplier']
            atr_ok = float(bar['atr_14']) > atr_threshold
            
            # Volume
            volume_ok = float(bar['Volume']) > (float(bar['volume_sma']) * params['volume_threshold'])
            
            # EMA strength
            ema_strength_ok = float(bar['ema_crossover_strength']) >= params['min_ema_crossover_strength']
            
            # Momentum
            momentum_ok = float(bar['Close']) < float(bar['ema_34'])
            
            return all([ema_crossover, rsi_ok, atr_ok, volume_ok, ema_strength_ok, momentum_ok])
            
        except Exception as e:
            return False
    
    def run_backtest(self, data, params, trade_direction='long'):
        """Ejecutar backtest con parámetros dados"""
        try:
            trades = []
            position = None
            entry_price = 0
            entry_time = None
            
            for i in range(1, len(data)):
                bar = data.iloc[i]
                
                # Verificar señal según dirección
                if trade_direction == 'long':
                    signal = self.check_long_signal(data, i, params)
                elif trade_direction == 'short':
                    signal = self.check_short_signal(data, i, params)
                else:  # both
                    long_signal = self.check_long_signal(data, i, params)
                    short_signal = self.check_short_signal(data, i, params)
                    signal = long_signal or short_signal
                
                # Si no hay posición y hay señal, abrir posición
                if position is None and signal:
                    position = 'long' if trade_direction == 'long' or (trade_direction == 'both' and long_signal) else 'short'
                    entry_price = float(bar['Close'])
                    entry_time = bar.name
                
                # Si hay posición, verificar salida
                elif position is not None:
                    exit_price = float(bar['Close'])
                    pnl = (exit_price - entry_price) if position == 'long' else (entry_price - exit_price)
                    
                    # Salida por Take Profit o Stop Loss
                    tp_hit = pnl >= params['take_profit']
                    sl_hit = pnl <= -params['stop_loss']
                    
                    # Salida por tiempo (máximo 4 horas)
                    time_exit = (bar.name - entry_time).total_seconds() / 3600 >= 4
                    
                    if tp_hit or sl_hit or time_exit:
                        trades.append({
                            'entry_time': entry_time,
                            'exit_time': bar.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'position': position,
                            'pnl': pnl,
                            'exit_reason': 'TP' if tp_hit else 'SL' if sl_hit else 'TIME'
                        })
                        position = None
            
            return trades
            
        except Exception as e:
            logger.error(f"❌ Error en backtest: {e}")
            return []
    
    def calculate_metrics(self, trades):
        """Calcular métricas de rendimiento"""
        try:
            if not trades:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'profit_factor': 0,
                    'max_drawdown': 0,
                    'sharpe_ratio': 0
                }
            
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['pnl'] > 0])
            losing_trades = len([t for t in trades if t['pnl'] < 0])
            
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            total_pnl = sum(t['pnl'] for t in trades)
            
            wins = [t['pnl'] for t in trades if t['pnl'] > 0]
            losses = [t['pnl'] for t in trades if t['pnl'] < 0]
            
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            
            profit_factor = abs(sum(wins) / sum(losses)) if sum(losses) != 0 else float('inf')
            
            # Calcular drawdown
            cumulative_pnl = np.cumsum([t['pnl'] for t in trades])
            running_max = np.maximum.accumulate(cumulative_pnl)
            drawdown = cumulative_pnl - running_max
            max_drawdown = abs(np.min(drawdown)) if len(drawdown) > 0 else 0
            
            # Sharpe ratio simplificado
            returns = [t['pnl'] for t in trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) != 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando métricas: {e}")
            return {}
    
    def optimize_strategy(self):
        """Optimizar estrategia completa"""
        try:
            logger.info("🚀 INICIANDO OPTIMIZACIÓN COMPLETA")
            logger.info("=" * 50)
            
            # Calcular indicadores
            data_with_indicators = self.calculate_indicators(self.data.copy())
            if data_with_indicators is None:
                return False
            
            # Definir rangos de optimización
            if self.test_mode:
                # MODO DE PRUEBA: Menos combinaciones para pruebas rápidas
                optimization_configs = [
                    # Configuración 1: Estrategia Long con horario estándar (reducida)
                    {
                        'name': 'Long Strategy - Standard Hours (TEST)',
                        'trade_direction': 'long',
                        'time_filter': {'start_hour': 9, 'end_hour': 16},
                        'params': {
                            'rsi_max': [65, 70, 75],
                            'atr_threshold_multiplier': [0.0002, 0.0003, 0.0004],
                            'volume_threshold': [0.4, 0.5, 0.6],
                            'min_ema_crossover_strength': [0.02, 0.05, 0.1],
                            'take_profit': [100, 150],
                            'stop_loss': [50, 75]
                        }
                    },
                    # Configuración 2: Estrategia Both (reducida)
                    {
                        'name': 'Both Directions Strategy (TEST)',
                        'trade_direction': 'both',
                        'time_filter': {'start_hour': 9, 'end_hour': 16},
                        'params': {
                            'rsi_max': [65, 70, 75],
                            'rsi_min': [25, 30, 35],
                            'atr_threshold_multiplier': [0.0002, 0.0003, 0.0004],
                            'volume_threshold': [0.4, 0.5, 0.6],
                            'min_ema_crossover_strength': [0.02, 0.05, 0.1],
                            'take_profit': [100, 150],
                            'stop_loss': [50, 75]
                        }
                    }
                ]
                logger.info("🧪 MODO DE PRUEBA: Usando configuración reducida para pruebas rápidas")
            else:
                # MODO COMPLETO: Todas las combinaciones
                optimization_configs = [
                    # Configuración 1: Estrategia Long con horario estándar
                    {
                        'name': 'Long Strategy - Standard Hours',
                        'trade_direction': 'long',
                        'time_filter': {'start_hour': 9, 'end_hour': 16},
                        'params': {
                            'rsi_max': [60, 65, 70, 75, 80],
                            'atr_threshold_multiplier': [0.0001, 0.0002, 0.0003, 0.0004, 0.0005],
                            'volume_threshold': [0.3, 0.4, 0.5, 0.6, 0.7],
                            'min_ema_crossover_strength': [0.01, 0.02, 0.05, 0.1, 0.2],
                            'take_profit': [50, 100, 150, 200],
                            'stop_loss': [25, 50, 75, 100]
                        }
                    },
                    # Configuración 2: Estrategia Long con horario extendido
                    {
                        'name': 'Long Strategy - Extended Hours',
                        'trade_direction': 'long',
                        'time_filter': {'start_hour': 8, 'end_hour': 17},
                        'params': {
                            'rsi_max': [60, 65, 70, 75, 80],
                            'atr_threshold_multiplier': [0.0001, 0.0002, 0.0003, 0.0004, 0.0005],
                            'volume_threshold': [0.3, 0.4, 0.5, 0.6, 0.7],
                            'min_ema_crossover_strength': [0.01, 0.02, 0.05, 0.1, 0.2],
                            'take_profit': [50, 100, 150, 200],
                            'stop_loss': [25, 50, 75, 100]
                        }
                    },
                    # Configuración 3: Estrategia Both (Long + Short)
                    {
                        'name': 'Both Directions Strategy',
                        'trade_direction': 'both',
                        'time_filter': {'start_hour': 9, 'end_hour': 16},
                        'params': {
                            'rsi_max': [60, 65, 70, 75, 80],
                            'rsi_min': [20, 25, 30, 35, 40],
                            'atr_threshold_multiplier': [0.0001, 0.0002, 0.0003, 0.0004, 0.0005],
                            'volume_threshold': [0.3, 0.4, 0.5, 0.6, 0.7],
                            'min_ema_crossover_strength': [0.01, 0.02, 0.05, 0.1, 0.2],
                            'take_profit': [50, 100, 150, 200],
                            'stop_loss': [25, 50, 75, 100]
                        }
                    }
                ]
                logger.info("🚀 MODO COMPLETO: Usando todas las combinaciones de parámetros")
            
            total_combinations = 0
            for config in optimization_configs:
                param_combinations = list(product(*config['params'].values()))
                total_combinations += len(param_combinations)
            
            logger.info(f"📊 Total de combinaciones a probar: {total_combinations}")
            
            # Estimar tiempo de ejecución
            if self.test_mode:
                estimated_time = total_combinations * 0.1  # ~0.1 segundos por combinación en modo test
                logger.info(f"⏱️  Tiempo estimado: ~{estimated_time:.1f} segundos (modo de prueba)")
            else:
                estimated_time = total_combinations * 0.5  # ~0.5 segundos por combinación en modo completo
                estimated_time_minutes = estimated_time / 60
                if estimated_time_minutes > 60:
                    estimated_time_hours = estimated_time_minutes / 60
                    logger.info(f"⏱️  Tiempo estimado: ~{estimated_time_hours:.1f} horas (modo completo)")
                else:
                    logger.info(f"⏱️  Tiempo estimado: ~{estimated_time_minutes:.1f} minutos (modo completo)")
            
            combination_count = 0
            
            for config in optimization_configs:
                logger.info(f"\n🔧 Probando configuración: {config['name']}")
                
                # Filtrar datos por horario
                filtered_data = self.filter_by_time(
                    data_with_indicators, 
                    config['time_filter']['start_hour'], 
                    config['time_filter']['end_hour']
                )
                
                logger.info(f"   📅 Datos filtrados: {len(filtered_data)} barras")
                
                # Generar combinaciones de parámetros
                param_names = list(config['params'].keys())
                param_values = list(config['params'].values())
                param_combinations = list(product(*param_values))
                
                for param_combo in param_combinations:
                    combination_count += 1
                    
                    # Crear diccionario de parámetros
                    params = dict(zip(param_names, param_combo))
                    
                    # Ejecutar backtest
                    trades = self.run_backtest(filtered_data, params, config['trade_direction'])
                    
                    # Calcular métricas
                    metrics = self.calculate_metrics(trades)
                    
                    # Crear resultado
                    result = {
                        'config_name': config['name'],
                        'trade_direction': config['trade_direction'],
                        'time_filter': config['time_filter'],
                        'params': params,
                        'trades': trades,
                        'metrics': metrics
                    }
                    
                    self.results.append(result)
                    
                    # Mostrar progreso más frecuente en modo de prueba
                    if self.test_mode:
                        if combination_count % 10 == 0:  # Cada 10 en modo test
                            logger.info(f"   🧪 Progreso TEST: {combination_count}/{total_combinations} ({combination_count/total_combinations*100:.1f}%)")
                    else:
                        if combination_count % 100 == 0:  # Cada 100 en modo completo
                            logger.info(f"   📈 Progreso: {combination_count}/{total_combinations} ({combination_count/total_combinations*100:.1f}%)")
            
            # Analizar resultados
            self._analyze_results()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en optimización: {e}")
            return False
    
    def _analyze_results(self):
        """Analizar y mostrar mejores resultados"""
        try:
            logger.info("\n📊 ANÁLISIS DE RESULTADOS")
            logger.info("=" * 50)
            
            # Filtrar resultados con al menos 5 trades
            valid_results = [r for r in self.results if r['metrics']['total_trades'] >= 5]
            
            if not valid_results:
                logger.warning("⚠️ No hay resultados válidos con suficientes trades")
                return
            
            # Ordenar por diferentes criterios
            by_pnl = sorted(valid_results, key=lambda x: x['metrics']['total_pnl'], reverse=True)
            by_win_rate = sorted(valid_results, key=lambda x: x['metrics']['win_rate'], reverse=True)
            by_profit_factor = sorted(valid_results, key=lambda x: x['metrics']['profit_factor'], reverse=True)
            by_sharpe = sorted(valid_results, key=lambda x: x['metrics']['sharpe_ratio'], reverse=True)
            
            # Mostrar mejores resultados por P&L
            print(f"\n🏆 TOP 10 POR P&L TOTAL:")
            for i, result in enumerate(by_pnl[:10], 1):
                m = result['metrics']
                p = result['params']
                print(f"   {i:2d}. {result['config_name']}")
                print(f"       💰 P&L: ${m['total_pnl']:.2f} | 📊 Trades: {m['total_trades']} | 🎯 Win Rate: {m['win_rate']:.1f}%")
                print(f"       📈 RSI: {p.get('rsi_max', p.get('rsi_min', 'N/A'))} | 📊 ATR: {p['atr_threshold_multiplier']:.4f}")
                print(f"       📊 Volume: {p['volume_threshold']} | 📈 EMA Strength: {p['min_ema_crossover_strength']}")
                print(f"       🎯 TP: {p['take_profit']} | 🛑 SL: {p['stop_loss']}")
                print()
            
            # Mostrar mejores resultados por Win Rate
            print(f"\n🎯 TOP 10 POR WIN RATE:")
            for i, result in enumerate(by_win_rate[:10], 1):
                m = result['metrics']
                p = result['params']
                print(f"   {i:2d}. {result['config_name']}")
                print(f"       🎯 Win Rate: {m['win_rate']:.1f}% | 💰 P&L: ${m['total_pnl']:.2f} | 📊 Trades: {m['total_trades']}")
                print(f"       📈 RSI: {p.get('rsi_max', p.get('rsi_min', 'N/A'))} | 📊 ATR: {p['atr_threshold_multiplier']:.4f}")
                print()
            
            # Mostrar mejores resultados por Profit Factor
            print(f"\n📈 TOP 10 POR PROFIT FACTOR:")
            for i, result in enumerate(by_profit_factor[:10], 1):
                m = result['metrics']
                p = result['params']
                print(f"   {i:2d}. {result['config_name']}")
                print(f"       📈 Profit Factor: {m['profit_factor']:.2f} | 💰 P&L: ${m['total_pnl']:.2f} | 📊 Trades: {m['total_trades']}")
                print(f"       📈 RSI: {p.get('rsi_max', p.get('rsi_min', 'N/A'))} | 📊 ATR: {p['atr_threshold_multiplier']:.4f}")
                print()
            
            # Análisis por configuración
            print(f"\n📊 ANÁLISIS POR CONFIGURACIÓN:")
            configs = {}
            for result in valid_results:
                config_name = result['config_name']
                if config_name not in configs:
                    configs[config_name] = []
                configs[config_name].append(result)
            
            for config_name, results in configs.items():
                avg_pnl = np.mean([r['metrics']['total_pnl'] for r in results])
                avg_trades = np.mean([r['metrics']['total_trades'] for r in results])
                avg_win_rate = np.mean([r['metrics']['win_rate'] for r in results])
                best_pnl = max([r['metrics']['total_pnl'] for r in results])
                
                print(f"   📊 {config_name}:")
                print(f"       💰 P&L Promedio: ${avg_pnl:.2f} | 🎯 Mejor P&L: ${best_pnl:.2f}")
                print(f"       📊 Trades Promedio: {avg_trades:.1f} | 🎯 Win Rate Promedio: {avg_win_rate:.1f}%")
                print()
            
            # Guardar mejores resultados
            self.best_results = by_pnl[:20]
            
            # Guardar resultados en archivo
            self._save_results()
            
        except Exception as e:
            logger.error(f"❌ Error analizando resultados: {e}")
    
    def _save_results(self):
        """Guardar resultados en archivo"""
        try:
            # Preparar datos para guardar
            save_data = []
            for result in self.best_results:
                save_data.append({
                    'config_name': result['config_name'],
                    'trade_direction': result['trade_direction'],
                    'time_filter': result['time_filter'],
                    'params': result['params'],
                    'metrics': result['metrics']
                })
            
            # Guardar en JSON
            with open('optimization_results.json', 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            logger.info("💾 Resultados guardados en 'optimization_results.json'")
            
        except Exception as e:
            logger.error(f"❌ Error guardando resultados: {e}")

def main():
    """Función principal"""
    try:
        parser = argparse.ArgumentParser(description="Optimizador Completo de Estrategia")
        parser.add_argument("--test", action="store_true", help="Ejecutar en modo de prueba (más rápido)")
        args = parser.parse_args()

        optimizer = ComprehensiveOptimizer(test_mode=args.test)
        
        if not optimizer.load_data():
            return False
        
        if not optimizer.optimize_strategy():
            return False
        
        if args.test:
            logger.info("🧪 MODO DE PRUEBA COMPLETADO - Para optimización completa, ejecuta sin --test")
        else:
            logger.info("🚀 OPTIMIZACIÓN COMPLETA FINALIZADA - Todos los parámetros han sido optimizados")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en función principal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
