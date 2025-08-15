#!/usr/bin/env python3
"""
Bot de Trading Unificado con Estrategia V5 Optimizada
=====================================================

Este script inicia el bot de trading con la estrategia V5 optimizada
que ha sido configurada con los parámetros de máxima rentabilidad.
Soporta modo DEMO y modo REAL.

Uso:
    python3 start_bot.py                    # Modo REAL (por defecto)
    python3 start_bot.py --mode demo        # Modo DEMO
    python3 start_bot.py --mode real        # Modo REAL
    export TRADING_MODE=demo && python3 start_bot.py  # Variable de entorno
"""

import sys
import os
import json
import logging
import argparse
from datetime import datetime
import time

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedTradingBot:
    """Bot de trading unificado con estrategia V5 optimizada"""
    
    def __init__(self, mode="real"):
        """Inicializar bot optimizado
        
        Args:
            mode (str): Modo de operación - "demo" o "real"
        """
        self.mode = mode.lower()
        self.config_file = f"config/tradeify_{self.mode}_config.json"
        self.strategy_config = None
        self.trading_active = False
        
        # Configurar logging unificado
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🚀 INICIANDO BOT DE TRADING EN MODO: {self.mode.upper()}")
        self.logger.info("=" * 60)
        
    def load_optimized_config(self):
        """Cargar configuración optimizada"""
        try:
            if not os.path.exists(self.config_file):
                self.logger.error(f"❌ No se encontró archivo de configuración: {self.config_file}")
                self.logger.info(f"💡 Creando configuración {self.mode} por defecto...")
                self.create_default_config()
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.strategy_config = config['strategy_config']['v5_optimized']
            
            self.logger.info("✅ Configuración cargada exitosamente")
            self.logger.info(f"🚀 Estrategia: V5 Optimizada ({self.mode.upper()})")
            self.logger.info(f"🌐 Modo: {self.mode.upper()}")
            self.logger.info(f"📊 RSI Max: {self.strategy_config['rsi_max']}")
            self.logger.info(f"📊 RSI Min: {self.strategy_config['rsi_min']}")
            self.logger.info(f"📊 ATR Threshold: {self.strategy_config['atr_threshold']}")
            self.logger.info(f"💰 Take Profit: ${self.strategy_config['take_profit']}")
            self.logger.info(f"🛑 Stop Loss: ${self.strategy_config['stop_loss']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando configuración: {e}")
            return False
    
    def create_default_config(self):
        """Crear configuración por defecto según el modo"""
        try:
            if self.mode == "demo":
                config = {
                    "strategy_config": {
                        "v5_optimized": {
                            "ema_period": 34,
                            "rsi_period": 14,
                            "rsi_max": 60,
                            "rsi_min": 20,
                            "atr_threshold": 0.0003,
                            "volume_threshold_min": 0.3,
                            "volume_threshold_max": 0.7,
                            "ema_crossover_strength": 0.01,
                            "stop_loss": 50,
                            "take_profit": 150,
                            "max_position_time": 3600,
                            "trading_hours_start": "09:00",
                            "trading_hours_end": "16:00",
                            "max_trades_per_day": 6,
                            "min_trade_duration": 300
                        }
                    },
                    "api_connection": {
                        "base_url": "demo.tradovateapi.com",
                        "api_key": "DEMO_KEY",
                        "secret_key": "DEMO_SECRET"
                    }
                }
            else:  # modo real
                config = {
                    "strategy_config": {
                        "v5_optimized": {
                            "ema_period": 34,
                            "rsi_period": 14,
                            "rsi_max": 60,
                            "rsi_min": 20,
                            "atr_threshold": 0.0003,
                            "volume_threshold_min": 0.3,
                            "volume_threshold_max": 0.7,
                            "ema_crossover_strength": 0.01,
                            "stop_loss": 50,
                            "take_profit": 150,
                            "max_position_time": 3600,
                            "trading_hours_start": "09:00",
                            "trading_hours_end": "16:00",
                            "max_trades_per_day": 6,
                            "min_trade_duration": 300
                        }
                    },
                    "api_connection": {
                        "base_url": "live.tradovateapi.com",
                        "api_key": "REAL_API_KEY",
                        "secret_key": "REAL_SECRET_KEY"
                    }
                }
            
            # Crear directorio config si no existe
            os.makedirs("config", exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"✅ Configuración {self.mode} creada: {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error creando configuración: {e}")
    
    def validate_trading_conditions(self):
        """Validar condiciones de trading"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            start_time = self.strategy_config['trading_hours_start']
            end_time = self.strategy_config['trading_hours_end']
            
            # Verificar horario de trading
            if start_time <= current_time <= end_time:
                self.logger.info(f"✅ Horario de trading válido: {current_time}")
                return True
            else:
                self.logger.warning(f"⚠️ Fuera del horario de trading: {current_time} (Horario: {start_time}-{end_time})")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error validando condiciones: {e}")
            return False
    
    def initialize_trading_system(self):
        """Inicializar sistema de trading"""
        try:
            self.logger.info("🔧 Inicializando sistema de trading...")
            
            # Aquí irían las inicializaciones del sistema según el modo
            if self.mode == "demo":
                self.logger.info("🎮 Inicializando modo DEMO - Sin riesgo real")
            else:
                self.logger.info("💰 Inicializando modo REAL - Trading con dinero real")
            
            self.logger.info("✅ Sistema de trading inicializado")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando sistema: {e}")
            return False
    
    def start_trading(self):
        """Iniciar trading con estrategia optimizada"""
        try:
            self.logger.info("🚀 INICIANDO TRADING CON ESTRATEGIA V5 OPTIMIZADA")
            self.logger.info("=" * 60)
            
            # 1. Cargar configuración
            if not self.load_optimized_config():
                return False
            
            # 2. Validar condiciones
            if not self.validate_trading_conditions():
                self.logger.warning("⚠️ Condiciones de trading no válidas")
                return False
            
            # 3. Inicializar sistema
            if not self.initialize_trading_system():
                return False
            
            # 4. Activar trading
            self.trading_active = True
            self.logger.info("✅ TRADING ACTIVADO - ESTRATEGIA V5 OPTIMIZADA")
            self.logger.info(f"🎯 Bot funcionando en modo {self.mode.upper()} con parámetros optimizados")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando trading: {e}")
            return False
    
    def run_trading_cycle(self):
        """Ejecutar ciclo de trading"""
        try:
            if not self.trading_active:
                self.logger.error("❌ Trading no está activo")
                return False
            
            self.logger.info("🔄 Ejecutando ciclo de trading...")
            
            # Aquí iría la lógica real de trading
            # Por ahora simulamos el ciclo
            
            self.logger.info("✅ Ciclo de trading completado")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo de trading: {e}")
            return False
    
    def stop_trading(self):
        """Detener trading"""
        try:
            self.logger.info("🛑 Deteniendo trading...")
            self.trading_active = False
            logger.info("✅ Trading detenido")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error deteniendo trading: {e}")
            return False

def main():
    """Función principal con soporte para variables de entorno"""
    try:
        # Determinar modo de operación
        trading_mode = os.environ.get('TRADING_MODE', 'real').lower()
        
        # Validar modo
        if trading_mode not in ['demo', 'real']:
            print(f"❌ ERROR: Modo inválido '{trading_mode}'. Usar 'demo' o 'real'")
            print("💡 Ejemplo: export TRADING_MODE=demo && python3 start_optimized_bot.py")
            return False
        
        print(f"🚀 INICIANDO BOT DE TRADING EN MODO: {trading_mode.upper()}")
        print("=" * 60)
        
        # Crear bot con el modo especificado
        bot = OptimizedTradingBot(mode=trading_mode)
        
        # Iniciar trading
        if not bot.start_trading():
            print("❌ No se pudo iniciar trading")
            return False
        
        print("🎉 BOT INICIADO EXITOSAMENTE")
        print(f"🎯 Estrategia V5 Optimizada activa en modo {trading_mode.upper()}")
        print("💰 Parámetros de máxima rentabilidad aplicados")
        print("=" * 60)
        
        # Mantener bot activo
        try:
            while bot.trading_active:
                bot.run_trading_cycle()
                time.sleep(60)  # Ciclo cada minuto
                
        except KeyboardInterrupt:
            print("⚠️ Interrupción del usuario detectada")
            bot.stop_trading()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Bot finalizado exitosamente")
    else:
        print("❌ Bot finalizado con errores")
    exit(0 if success else 1)
