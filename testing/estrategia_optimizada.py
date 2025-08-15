#!/usr/bin/env python3
"""
ESTRATEGIA OPTIMIZADA - IMPLEMENTACIÓN COMPLETA
===============================================

Estrategia ganadora de la optimización:
- P&L máximo: $2,031 en 18 trades
- Win Rate: 77.8%
- Parámetros optimizados
- 1 contrato MNQ
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Importar el cargador de datos
from .ninjatrader_data_loader import NinjaTraderDataLoader

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EstrategiaOptimizada:
    """Estrategia optimizada implementada"""
    
    def __init__(self):
        """Inicializar con parámetros ganadores"""
        # PARÁMETROS OPTIMIZADOS (los que dieron $2,031)
        self.ema_period = 34
        self.rsi_period = 14
        self.rsi_max_long = 60
        self.rsi_min_short = 40
        self.atr_threshold_multiplier = 0.0003
        self.volume_threshold = 0.3
        self.min_ema_crossover_strength = 0.01
        
        # GESTIÓN DE RIESGO
        self.stop_loss = 50
        self.take_profit = 150
        self.max_position_time = 4  # horas
        self.contracts = 1
        
        # Estado
        self.position = None
        self.trades_history = []
        self.current_pnl = 0.0
        
        # SISTEMA DE LOG CRONOLÓGICO
        self.peak_pnl = 0.0  # P&L máximo alcanzado
        self.current_drawdown = 0.0  # Drawdown actual
        self.max_drawdown = 0.0  # Máximo drawdown histórico
        self.trade_log = []  # Log cronológico completo
        self.trade_counter = 0  # Contador de trades
        
        logger.info("🚀 ESTRATEGIA OPTIMIZADA INICIADA")
        logger.info(f"💰 Contratos: {self.contracts}")
        logger.info(f"🛑 Stop Loss: {self.stop_loss} puntos")
        logger.info(f"🎯 Take Profit: {self.take_profit} puntos")
        logger.info("📊 SISTEMA DE LOG CRONOLÓGICO ACTIVADO")
    
    def cargar_datos(self, archivo_datos):
        """Cargar datos de mercado"""
        try:
            logger.info(f"📥 Cargando datos desde: {archivo_datos}")
            
            loader = NinjaTraderDataLoader()
            if not loader.load_from_txt(archivo_datos):
                logger.error("❌ Error cargando datos")
                return False
            
            # Obtener datos filtrados por horario de trading
            self.data = loader.filter_trading_hours()
            
            if self.data is None or len(self.data) == 0:
                logger.error("❌ No hay datos de trading")
                return False
            
            logger.info(f"✅ Datos cargados: {len(self.data)} barras")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            return False
    
    def calcular_indicadores(self):
        """Calcular indicadores técnicos"""
        try:
            logger.info("🔧 Calculando indicadores...")
            
            # EMA 34
            self.data['ema_34'] = self.data['Close'].ewm(span=self.ema_period).mean()
            
            # RSI 14
            delta = self.data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            rs = gain / loss
            self.data['rsi_14'] = 100 - (100 / (1 + rs))
            
            # ATR 14
            high = self.data['High']
            low = self.data['Low']
            close = self.data['Close']
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            self.data['atr_14'] = tr.rolling(window=14).mean()
            
            # Volume SMA
            self.data['volume_sma'] = self.data['Volume'].rolling(window=20).mean()
            
            # Precio vs EMA
            self.data['price_vs_ema'] = self.data['Close'] - self.data['ema_34']
            self.data['ema_crossover_strength'] = self.data['price_vs_ema'].abs() / self.data['Close'] * 100
            
            # Limpiar datos
            self.data = self.data.dropna()
            
            logger.info(f"✅ Indicadores calculados: {len(self.data)} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error calculando indicadores: {e}")
            return False
    
    def verificar_señal_long(self, barra_actual, barra_anterior):
        """Verificar señal de compra (long)"""
        try:
            # EMA crossover (precio cruza por encima de EMA)
            ema_crossover = (float(barra_anterior['Close']) <= float(barra_anterior['ema_34']) and 
                           float(barra_actual['Close']) > float(barra_actual['ema_34']))
            
            if not ema_crossover:
                return False
            
            # RSI
            rsi_ok = float(barra_actual['rsi_14']) < self.rsi_max_long
            
            # ATR
            atr_threshold = float(barra_actual['Close']) * self.atr_threshold_multiplier
            atr_ok = float(barra_actual['atr_14']) > atr_threshold
            
            # Volume
            volume_ok = float(barra_actual['Volume']) > float(barra_actual['volume_sma']) * self.volume_threshold
            
            # EMA strength
            ema_strength_ok = float(barra_actual['ema_crossover_strength']) >= self.min_ema_crossover_strength
            
            # Momentum
            momentum_ok = float(barra_actual['Close']) > float(barra_actual['ema_34'])
            
            return all([ema_crossover, rsi_ok, atr_ok, volume_ok, ema_strength_ok, momentum_ok])
            
        except Exception as e:
            return False
    
    def verificar_señal_short(self, barra_actual, barra_anterior):
        """Verificar señal de venta (short)"""
        try:
            # EMA crossover (precio cruza por debajo de EMA)
            ema_crossover = (float(barra_anterior['Close']) >= float(barra_anterior['ema_34']) and 
                           float(barra_actual['Close']) < float(barra_actual['ema_34']))
            
            if not ema_crossover:
                return False
            
            # RSI
            rsi_ok = float(barra_actual['rsi_14']) > self.rsi_min_short
            
            # ATR
            atr_threshold = float(barra_actual['Close']) * self.atr_threshold_multiplier
            atr_ok = float(barra_actual['atr_14']) > atr_threshold
            
            # Volume
            volume_ok = float(barra_actual['Volume']) > float(barra_actual['volume_sma']) * self.volume_threshold
            
            # EMA strength
            ema_strength_ok = float(barra_actual['ema_crossover_strength']) >= self.min_ema_crossover_strength
            
            # Momentum
            momentum_ok = float(barra_actual['Close']) < float(barra_actual['ema_34'])
            
            return all([ema_crossover, rsi_ok, atr_ok, volume_ok, ema_strength_ok, momentum_ok])
            
        except Exception as e:
            return False
    
    def verificar_salida(self, barra_actual):
        """Verificar condiciones de salida"""
        try:
            if self.position is None:
                return False, ""
            
            precio_actual = float(barra_actual['Close'])
            precio_entrada = self.position['precio_entrada']
            tipo_posicion = self.position['tipo']
            
            # Calcular P&L
            if tipo_posicion == 'long':
                pnl = (precio_actual - precio_entrada) * self.contracts
            else:  # short
                pnl = (precio_entrada - precio_actual) * self.contracts
            
            # Verificar Take Profit
            if pnl >= self.take_profit:
                return True, "TP"
            
            # Verificar Stop Loss
            if pnl <= -self.stop_loss:
                return True, "SL"
            
            # Verificar tiempo máximo en posición
            tiempo_en_posicion = (barra_actual.name - self.position['hora_entrada']).total_seconds() / 3600
            if tiempo_en_posicion >= self.max_position_time:
                return True, "TIME"
            
            return False, ""
            
        except Exception as e:
            return False, ""
    
    def abrir_posicion(self, tipo, precio, hora, barra):
        """Abrir posición"""
        try:
            if self.position is not None:
                logger.warning("⚠️ Ya hay una posición abierta")
                return False
            
            # Crear posición
            self.position = {
                'tipo': tipo,
                'precio_entrada': precio,
                'hora_entrada': hora,
                'barra_entrada': barra
            }
            
            # ACTUALIZAR LOG CRONOLÓGICO
            self.trade_counter += 1
            self.actualizar_log_cronologico("ENTRADA", tipo, precio, hora, 0.0, 0.0, 0.0)
            
            logger.info(f"🎯 POSICIÓN ABIERTA: {tipo.upper()} a ${precio:.2f}")
            logger.info(f"   📅 Hora: {hora}")
            logger.info(f"   📊 RSI: {float(barra['rsi_14']):.1f}")
            logger.info(f"   📈 ATR: {float(barra['atr_14']):.4f}")
            logger.info(f"   📊 Volume: {float(barra['Volume'])}")
            logger.info(f"   📊 Trade #{self.trade_counter}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error abriendo posición: {e}")
            return False
    
    def cerrar_posicion(self, precio_salida, hora_salida, motivo):
        """Cerrar posición"""
        try:
            if self.position is None:
                logger.warning("⚠️ No hay posición para cerrar")
                return False
            
            # Calcular P&L
            precio_entrada = self.position['precio_entrada']
            tipo_posicion = self.position['tipo']
            
            if tipo_posicion == 'long':
                pnl = (precio_salida - precio_entrada) * self.contracts
            else:  # short
                pnl = (precio_entrada - precio_salida) * self.contracts
            
            # Crear registro de trade
            trade = {
                'hora_entrada': self.position['hora_entrada'],
                'hora_salida': hora_salida,
                'precio_entrada': precio_entrada,
                'precio_salida': precio_salida,
                'tipo_posicion': tipo_posicion,
                'pnl': pnl,
                'motivo_salida': motivo
            }
            
            # ACTUALIZAR LOG CRONOLÓGICO
            self.actualizar_log_cronologico("SALIDA", tipo_posicion, precio_salida, hora_salida, pnl, self.current_pnl, self.current_drawdown)
            
            # Actualizar estado
            self.trades_history.append(trade)
            self.current_pnl += pnl
            
            # Limpiar posición
            posicion_anterior = self.position
            self.position = None
            
            logger.info(f"🔒 POSICIÓN CERRADA: {motivo}")
            logger.info(f"   💰 P&L: ${pnl:.2f}")
            logger.info(f"   📅 Duración: {hora_salida - posicion_anterior['hora_entrada']}")
            logger.info(f"   📊 P&L Total: ${self.current_pnl:.2f}")
            logger.info(f"   📊 Drawdown Actual: {self.current_drawdown:.2f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cerrando posición: {e}")
            return False
    
    def actualizar_log_cronologico(self, accion, tipo, precio, hora, pnl_trade, pnl_total, drawdown_actual):
        """Actualizar log cronológico completo de trades"""
        try:
            # Calcular métricas de drawdown
            if pnl_total > self.peak_pnl:
                self.peak_pnl = pnl_total
            
            if self.peak_pnl > 0:
                self.current_drawdown = ((self.peak_pnl - pnl_total) / self.peak_pnl) * 100
                if self.current_drawdown > self.max_drawdown:
                    self.max_drawdown = self.current_drawdown
            
            # Crear entrada del log
            log_entry = {
                'timestamp': hora,
                'trade_num': self.trade_counter,
                'accion': accion,
                'tipo_posicion': tipo,
                'precio': precio,
                'pnl_trade': pnl_trade,
                'pnl_total': pnl_total,
                'drawdown_actual': self.current_drawdown,
                'max_drawdown': self.max_drawdown,
                'peak_pnl': self.peak_pnl
            }
            
            self.trade_log.append(log_entry)
            
        except Exception as e:
            logger.error(f"❌ Error actualizando log cronológico: {e}")
    
    def exportar_log_cronologico(self, nombre_archivo=None):
        """Exportar log cronológico completo a archivo"""
        try:
            if nombre_archivo is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"logs/trade_log_cronologico_{timestamp}.txt"
            
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write("📊 LOG CRONOLÓGICO COMPLETO DE TRADES\n")
                f.write("=" * 80 + "\n")
                f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Estrategia: Estrategia Optimizada V5\n")
                f.write(f"Parámetros: EMA={self.ema_period}, RSI={self.rsi_period}\n")
                f.write("=" * 80 + "\n\n")
                
                for entry in self.trade_log:
                    f.write(f"🕐 {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"   📊 Trade #{entry['trade_num']} - {entry['accion']}\n")
                    f.write(f"   🎯 {entry['tipo_posicion'].upper()} a ${entry['precio']:.2f}\n")
                    f.write(f"   💰 P&L Trade: ${entry['pnl_trade']:.2f}\n")
                    f.write(f"   📈 P&L Total: ${entry['pnl_total']:.2f}\n")
                    f.write(f"   📉 Drawdown Actual: {entry['drawdown_actual']:.2f}%\n")
                    f.write(f"   📊 Máximo Drawdown: {entry['max_drawdown']:.2f}%\n")
                    f.write(f"   🏆 Peak P&L: ${entry['peak_pnl']:.2f}\n")
                    f.write("-" * 50 + "\n")
                
                # Resumen final
                f.write(f"\n📊 RESUMEN FINAL:\n")
                f.write(f"   Total de entradas: {len([e for e in self.trade_log if e['accion'] == 'ENTRADA'])}\n")
                f.write(f"   Total de salidas: {len([e for e in self.trade_log if e['accion'] == 'SALIDA'])}\n")
                f.write(f"   P&L Final: ${self.current_pnl:.2f}\n")
                f.write(f"   Máximo Drawdown: {self.max_drawdown:.2f}%\n")
                f.write(f"   Peak P&L: ${self.peak_pnl:.2f}\n")
            
            logger.info(f"✅ Log cronológico exportado a: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            logger.error(f"❌ Error exportando log cronológico: {e}")
            return None
    
    def ejecutar_backtest(self):
        """Ejecutar backtest completo"""
        try:
            logger.info("🚀 INICIANDO BACKTEST COMPLETO")
            logger.info("=" * 50)
            
            if self.data is None:
                logger.error("❌ No hay datos para backtest")
                return False
            
            # Reiniciar estado
            self.position = None
            self.trades_history = []
            self.current_pnl = 0.0
            
            # Ejecutar simulación
            for i in range(1, len(self.data)):
                barra_actual = self.data.iloc[i]
                barra_anterior = self.data.iloc[i-1]
                
                # Verificar salida si hay posición
                if self.position is not None:
                    debe_salir, motivo = self.verificar_salida(barra_actual)
                    if debe_salir:
                        self.cerrar_posicion(
                            float(barra_actual['Close']),
                            barra_actual.name,
                            motivo
                        )
                        continue
                
                # Verificar señales si no hay posición
                if self.position is None:
                    # Señal long
                    if self.verificar_señal_long(barra_actual, barra_anterior):
                        self.abrir_posicion(
                            'long',
                            float(barra_actual['Close']),
                            barra_actual.name,
                            barra_actual
                        )
                        continue
                    
                    # Señal short
                    if self.verificar_señal_short(barra_actual, barra_anterior):
                        self.abrir_posicion(
                            'short',
                            float(barra_actual['Close']),
                            barra_actual.name,
                            barra_actual
                        )
                        continue
            
            # Cerrar posición final si existe
            if self.position is not None:
                ultima_barra = self.data.iloc[-1]
                self.cerrar_posicion(
                    float(ultima_barra['Close']),
                    ultima_barra.name,
                    "END"
                )
            
            # Mostrar resultados
            self.mostrar_resultados()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en backtest: {e}")
            return False
    
    def mostrar_resultados(self):
        """Mostrar resultados del backtest"""
        try:
            if not self.trades_history:
                print("❌ No hay trades para mostrar")
                return
            
            # Calcular métricas
            total_trades = len(self.trades_history)
            trades_ganadores = len([t for t in self.trades_history if t['pnl'] > 0])
            trades_perdedores = len([t for t in self.trades_history if t['pnl'] < 0])
            
            win_rate = (trades_ganadores / total_trades) * 100 if total_trades > 0 else 0
            
            ganancias = [t['pnl'] for t in self.trades_history if t['pnl'] > 0]
            perdidas = [t['pnl'] for t in self.trades_history if t['pnl'] < 0]
            
            promedio_ganancia = np.mean(ganancias) if ganancias else 0
            promedio_perdida = np.mean(perdidas) if perdidas else 0
            
            profit_factor = abs(sum(ganancias) / sum(perdidas)) if sum(perdidas) != 0 else float('inf')
            
            print(f"\n📊 RESULTADOS DEL BACKTEST")
            print(f"=" * 50)
            print(f"📈 Total de trades: {total_trades}")
            print(f"✅ Trades ganadores: {trades_ganadores}")
            print(f"❌ Trades perdedores: {trades_perdedores}")
            print(f"🎯 Win Rate: {win_rate:.1f}%")
            print(f"💰 P&L Total: ${self.current_pnl:.2f}")
            print(f"📈 Promedio ganancia: ${promedio_ganancia:.2f}")
            print(f"📉 Promedio pérdida: ${promedio_perdida:.2f}")
            print(f"📊 Profit Factor: {profit_factor:.2f}")
            print(f"📉 Máximo Drawdown: {self.max_drawdown:.2f}%")
            print(f"🏆 Peak P&L: ${self.peak_pnl:.2f}")
            
            if self.trades_history:
                print(f"\n🎯 ÚLTIMOS 5 TRADES:")
                for i, trade in enumerate(self.trades_history[-5:], 1):
                    print(f"   {i}. {trade['tipo_posicion'].upper()} - ${trade['pnl']:.2f} - {trade['motivo_salida']}")
            
            # Exportar log cronológico
            archivo_log = self.exportar_log_cronologico()
            if archivo_log:
                print(f"\n📁 Log cronológico exportado a: {archivo_log}")
                print("   📊 Revisa este archivo para análisis detallado de drawdown")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando resultados: {e}")

def main():
    """Función principal"""
    try:
        print("🚀 ESTRATEGIA OPTIMIZADA - BACKTEST")
        print("=" * 50)
        print("📊 SISTEMA DE LOG CRONOLÓGICO ACTIVADO")
        print("   - Cada trade será registrado con timestamp exacto")
        print("   - Se calculará drawdown en tiempo real")
        print("   - Se exportará log completo para análisis manual")
        print("=" * 50)
        
        # Crear estrategia
        estrategia = EstrategiaOptimizada()
        
        # Cargar datos
        if not estrategia.cargar_datos('testing/MNQ_09-25_30days_1min.txt'):
            return False
        
        # Calcular indicadores
        if not estrategia.calcular_indicadores():
            return False
        
        # Ejecutar backtest
        if not estrategia.ejecutar_backtest():
            return False
        
        print("\n✅ Backtest completado exitosamente")
        print("📁 Revisa el archivo de log cronológico para análisis detallado")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en función principal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
