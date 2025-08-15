#!/usr/bin/env python3
"""
Activador de Estrategia V5 Optimizada
=====================================

Este script activa la estrategia V5 optimizada con los parámetros
de máxima rentabilidad encontrados en la optimización.
"""

import sys
import os
import json
import logging
from datetime import datetime
import shutil

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrategyV5Activator:
    """Activador de la estrategia V5 optimizada"""
    
    def __init__(self):
        """Inicializar activador"""
        self.config_dir = "config"
        self.strategy_config = "strategy_v5.json"
        self.main_config = "tradeify_real_config.json"
        self.backup_dir = "config/backups"
        
    def create_backup(self):
        """Crear backup de la configuración actual"""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_dir}/config_backup_{timestamp}.json"
            
            if os.path.exists(f"{self.config_dir}/{self.main_config}"):
                shutil.copy2(f"{self.config_dir}/{self.main_config}", backup_file)
                logger.info(f"✅ Backup creado: {backup_file}")
                return True
            else:
                logger.warning("⚠️ No se encontró configuración principal para hacer backup")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False
    
    def load_strategy_config(self):
        """Cargar configuración de la estrategia optimizada"""
        try:
            config_path = f"{self.config_dir}/{self.strategy_config}"
            if not os.path.exists(config_path):
                logger.error(f"❌ No se encontró: {config_path}")
                return None
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            logger.info(f"✅ Configuración cargada: {config['strategy_name']} v{config['version']}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            return None
    
    def update_main_config(self, strategy_config):
        """Actualizar configuración principal con parámetros optimizados"""
        try:
            main_config_path = f"{self.config_dir}/{self.main_config}"
            
            if not os.path.exists(main_config_path):
                logger.error(f"❌ No se encontró configuración principal: {main_config_path}")
                return False
            
            # Cargar configuración principal
            with open(main_config_path, 'r') as f:
                main_config = json.load(f)
            
            # Actualizar parámetros de estrategia
            main_config['strategy_config']['v5_optimized'] = {
                "rsi_max": strategy_config['core_parameters']['rsi_max'],
                "rsi_min": strategy_config['core_parameters']['rsi_min'],
                "atr_threshold": strategy_config['core_parameters']['atr_threshold'],
                "volume_threshold_min": strategy_config['core_parameters']['volume_threshold_min'],
                "volume_threshold_max": strategy_config['core_parameters']['volume_threshold_max'],
                "ema_crossover_strength": strategy_config['core_parameters']['ema_crossover_strength'],
                "take_profit": strategy_config['core_parameters']['take_profit'],
                "stop_loss": strategy_config['core_parameters']['stop_loss'],
                "ema_period": strategy_config['technical_indicators']['ema_period'],
                "rsi_period": strategy_config['technical_indicators']['rsi_period'],
                "atr_period": strategy_config['technical_indicators']['atr_period'],
                "max_trades_per_day": strategy_config['trading_constraints']['max_trades_per_day'],
                "min_trade_duration": strategy_config['trading_constraints']['min_trade_duration'],
                "trading_hours_start": strategy_config['trading_constraints']['trading_hours_start'],
                "trading_hours_end": strategy_config['trading_constraints']['trading_hours_end']
            }
            
            # Actualizar horarios de trading
            main_config['trading_hours']['start'] = strategy_config['trading_constraints']['trading_hours_start']
            main_config['trading_hours']['end'] = strategy_config['trading_constraints']['trading_hours_end']
            
            # Guardar configuración actualizada
            with open(main_config_path, 'w') as f:
                json.dump(main_config, f, indent=2)
            
            logger.info("✅ Configuración principal actualizada con parámetros optimizados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando configuración principal: {e}")
            return False
    
    def create_activation_report(self, strategy_config):
        """Crear reporte de activación"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"logs/activation_report_{timestamp}.txt"
            
            with open(report_file, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("REPORTE DE ACTIVACIÓN - ESTRATEGIA V5 OPTIMIZADA\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"📅 Fecha de Activación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"🚀 Estrategia: {strategy_config['strategy_name']} v{strategy_config['version']}\n")
                f.write(f"📊 Período de Optimización: {strategy_config['backtest_period']}\n")
                f.write(f"⏱️ Duración de Optimización: {strategy_config['optimization_duration']}\n\n")
                
                f.write("🔧 PARÁMETROS OPTIMIZADOS:\n")
                f.write("-" * 30 + "\n")
                for key, value in strategy_config['core_parameters'].items():
                    f.write(f"   {key}: {value}\n")
                
                f.write(f"\n📈 MÉTRICAS DE PERFORMANCE:\n")
                f.write("-" * 30 + "\n")
                f.write(f"   Win Rate: {strategy_config['performance_metrics']['win_rate']}%\n")
                f.write(f"   Total Trades: {strategy_config['performance_metrics']['total_trades']}\n")
                f.write(f"   P&L Total: ${strategy_config['performance_metrics']['total_pnl']:.2f}\n")
                f.write(f"   Profit Factor: {strategy_config['performance_metrics']['profit_factor']}\n")
                
                f.write(f"\n✅ ESTADO: {strategy_config['activation_status']}\n")
                f.write(f"🎯 LISTA PARA TRADING EN VIVO\n")
            
            logger.info(f"✅ Reporte de activación creado: {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando reporte: {e}")
            return False
    
    def activate_strategy(self):
        """Activar la estrategia V5 optimizada"""
        try:
            logger.info("🚀 INICIANDO ACTIVACIÓN DE ESTRATEGIA V5 OPTIMIZADA")
            logger.info("=" * 60)
            
            # 1. Crear backup
            logger.info("📦 Creando backup de configuración actual...")
            if not self.create_backup():
                logger.warning("⚠️ Continuando sin backup...")
            
            # 2. Cargar configuración optimizada
            logger.info("📋 Cargando configuración optimizada...")
            strategy_config = self.load_strategy_config()
            if not strategy_config:
                return False
            
            # 3. Actualizar configuración principal
            logger.info("⚙️ Actualizando configuración principal...")
            if not self.update_main_config(strategy_config):
                return False
            
            # 4. Crear reporte de activación
            logger.info("📊 Generando reporte de activación...")
            if not self.create_activation_report(strategy_config):
                logger.warning("⚠️ No se pudo crear reporte...")
            
            # 5. Verificar activación
            logger.info("🔍 Verificando activación...")
            if self.verify_activation():
                logger.info("✅ ESTRATEGIA V5 OPTIMIZADA ACTIVADA EXITOSAMENTE")
                logger.info("🎯 LISTA PARA TRADING EN VIVO")
                return True
            else:
                logger.error("❌ Error en verificación de activación")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en activación: {e}")
            return False
    
    def verify_activation(self):
        """Verificar que la activación fue exitosa"""
        try:
            main_config_path = f"{self.config_dir}/{self.main_config}"
            
            with open(main_config_path, 'r') as f:
                config = json.load(f)
            
            # Verificar que los parámetros estén presentes
            strategy_config = config.get('strategy_config', {}).get('v5_optimized', {})
            
            required_params = [
                'rsi_max', 'rsi_min', 'atr_threshold', 'take_profit', 'stop_loss'
            ]
            
            for param in required_params:
                if param not in strategy_config:
                    logger.error(f"❌ Parámetro faltante: {param}")
                    return False
            
            logger.info("✅ Verificación exitosa - Todos los parámetros presentes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en verificación: {e}")
            return False

def main():
    """Función principal"""
    try:
        activator = StrategyV5Activator()
        
        if activator.activate_strategy():
            print("\n" + "=" * 60)
            print("🎉 ¡ESTRATEGIA V5 OPTIMIZADA ACTIVADA EXITOSAMENTE!")
            print("=" * 60)
            print("✅ Parámetros optimizados aplicados")
            print("✅ Configuración actualizada")
            print("✅ Backup creado")
            print("✅ Reporte generado")
            print("🎯 LISTA PARA TRADING EN VIVO")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ ERROR EN LA ACTIVACIÓN")
            print("=" * 60)
            print("Revise los logs para más detalles")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en función principal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
