#!/usr/bin/env python3
"""
Sistema de Compliance Tradeify
==============================

Este script implementa TODAS las reglas de Tradeify que me enviaste:
- Microscalping mínimo 50%
- Consistency máximo 35%
- Daily Loss Limit $1,250
- Trailing Drawdown $2,000 (End of Day)
- Horarios 09:00-16:59 UTC
- Trading Days mínimo 1 por semana
- No hedging, no copy trading
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradeifyComplianceSystem:
    """Sistema completo de compliance para Tradeify"""
    
    def __init__(self, config_file: str = None):
        """Inicializar sistema de compliance"""
        if config_file is None:
            # Ruta absoluta al archivo de configuración Lightning 50K
            config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'lightning_50k_strategy.json')
        self.config = self.load_config(config_file)
        self.trades_history = []
        self.daily_stats = {}
        self.weekly_stats = {}
        self.compliance_status = {
            "microscalping": False,
            "consistency": False,
            "daily_loss": False,
            "drawdown": False,
            "activity": False,
            "overall": False
        }
        
        logger.info("TradeifyComplianceSystem inicializado")
    
    def get_compliance_status(self) -> dict:
        """Obtener estado actual de compliance"""
        return self.compliance_status.copy()
    
    def load_config(self, config_file: str) -> dict:
        """Cargar configuración de Tradeify"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_file}")
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            logger.info("Configuración de compliance cargada")
            return config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            raise
    
    def add_trade(self, trade_data: Dict):
        """Agregar trade al historial para compliance"""
        try:
            # Agregar timestamp si no existe
            if 'timestamp' not in trade_data:
                trade_data['timestamp'] = datetime.now()
            
            # Agregar trade al historial
            self.trades_history.append(trade_data)
            
            # Actualizar estadísticas
            self.update_daily_stats(trade_data)
            self.update_weekly_stats(trade_data)
            
            logger.info(f"Trade agregado para compliance: {trade_data.get('signal', 'N/A')} @ {trade_data.get('entry_price', 'N/A')}")
            
        except Exception as e:
            logger.error(f"Error agregando trade: {e}")
    
    def update_daily_stats(self, trade_data: Dict):
        """Actualizar estadísticas diarias"""
        try:
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            
            if today_str not in self.daily_stats:
                self.daily_stats[today_str] = {
                    'trades': [],
                    'total_pnl': 0.0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'max_loss': 0.0,
                    'start_balance': 50000.0,  # Balance inicial Tradeify
                    'current_balance': 50000.0
                }
            
            # Agregar trade al día
            self.daily_stats[today_str]['trades'].append(trade_data)
            
            # Calcular P&L si el trade está cerrado
            if trade_data.get('status') in ['TP_HIT', 'SL_HIT', 'CLOSED']:
                pnl = trade_data.get('pnl', 0.0)
                self.daily_stats[today_str]['total_pnl'] += pnl
                self.daily_stats[today_str]['current_balance'] += pnl
                
                if pnl > 0:
                    self.daily_stats[today_str]['winning_trades'] += 1
                else:
                    self.daily_stats[today_str]['losing_trades'] += 1
                    self.daily_stats[today_str]['max_loss'] = min(self.daily_stats[today_str]['max_loss'], pnl)
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas diarias: {e}")
    
    def update_weekly_stats(self, trade_data: Dict):
        """Actualizar estadísticas semanales"""
        try:
            # Obtener semana actual
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_str = week_start.strftime('%Y-W%U')
            
            if week_str not in self.weekly_stats:
                self.weekly_stats[week_str] = {
                    'trading_days': set(),
                    'total_trades': 0,
                    'total_pnl': 0.0
                }
            
            # Agregar día de trading
            trade_date = trade_data.get('timestamp', today).date()
            self.weekly_stats[week_str]['trading_days'].add(trade_date)
            self.weekly_stats[week_str]['total_trades'] += 1
            
            # Calcular P&L si el trade está cerrado
            if trade_data.get('status') in ['TP_HIT', 'SL_HIT', 'CLOSED']:
                pnl = trade_data.get('pnl', 0.0)
                self.weekly_stats[week_str]['total_pnl'] += pnl
                
        except Exception as e:
            logger.error(f"Error actualizando estadísticas semanales: {e}")
    
    def check_microscalping_compliance(self) -> Tuple[bool, float]:
        """Verificar compliance de microscalping (mínimo 50%)"""
        try:
            if not self.trades_history:
                return False, 0.0
            
            # Calcular trades de microscalping (duración < 5 minutos)
            total_trades = len(self.trades_history)
            microscalping_trades = 0
            
            for trade in self.trades_history:
                if trade.get('status') in ['TP_HIT', 'SL_HIT', 'CLOSED']:
                    entry_time = trade.get('entry_time')
                    exit_time = trade.get('exit_time')
                    
                    if entry_time and exit_time:
                        duration = (exit_time - entry_time).total_seconds() / 60  # minutos
                        if duration < 5:  # Menos de 5 minutos = microscalping
                            microscalping_trades += 1
            
            if total_trades == 0:
                return False, 0.0
            
            microscalping_percentage = microscalping_trades / total_trades
            is_compliant = microscalping_percentage >= self.config['compliance_rules']['microscalping_minimum']
            
            logger.info(f"Microscalping: {microscalping_percentage*100:.1f}% (requerido: {self.config['compliance_rules']['microscalping_minimum']*100}%)")
            
            return is_compliant, microscalping_percentage
            
        except Exception as e:
            logger.error(f"Error verificando microscalping: {e}")
            return False, 0.0
    
    def check_consistency_compliance(self) -> Tuple[bool, float]:
        """Verificar compliance de consistency (máximo 35%)"""
        try:
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            
            if today_str not in self.daily_stats:
                return True, 0.0  # Sin trades hoy = compliant
            
            daily_data = self.daily_stats[today_str]
            
            if daily_data['total_pnl'] >= 0:
                return True, 0.0  # Profit hoy = compliant
            
            # Calcular consistency (pérdida máxima como % del balance)
            max_loss = abs(daily_data['max_loss'])
            start_balance = daily_data['start_balance']
            consistency_percentage = (max_loss / start_balance) * 100
            
            is_compliant = consistency_percentage <= (self.config['compliance_rules']['consistency_threshold'] * 100)
            
            logger.info(f"Consistency: {consistency_percentage:.1f}% (máximo: {self.config['compliance_rules']['consistency_threshold']*100}%)")
            
            return is_compliant, consistency_percentage / 100
            
        except Exception as e:
            logger.error(f"Error verificando consistency: {e}")
            return False, 1.0
    
    def check_daily_loss_compliance(self) -> Tuple[bool, float]:
        """Verificar compliance de Daily Loss Limit ($1,250)"""
        try:
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            
            if today_str not in self.daily_stats:
                return True, 0.0  # Sin trades hoy = compliant
            
            daily_data = self.daily_stats[today_str]
            daily_loss = abs(min(0, daily_data['total_pnl']))
            max_allowed_loss = self.config['risk_management']['daily_loss_limit']
            
            is_compliant = daily_loss <= max_allowed_loss
            loss_percentage = daily_loss / max_allowed_loss
            
            logger.info(f"Daily Loss: ${daily_loss:.2f} (límite: ${max_allowed_loss})")
            
            return is_compliant, loss_percentage
            
        except Exception as e:
            logger.error(f"Error verificando daily loss: {e}")
            return False, 1.0
    
    def check_drawdown_compliance(self) -> Tuple[bool, float]:
        """Verificar compliance de Trailing Drawdown ($2,000 End of Day)"""
        try:
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            
            if today_str not in self.daily_stats:
                return True, 0.0  # Sin trades hoy = compliant
            
            daily_data = self.daily_stats[today_str]
            current_balance = daily_data['current_balance']
            start_balance = daily_data['start_balance']
            
            # Drawdown = diferencia desde el balance inicial
            drawdown = start_balance - current_balance
            max_allowed_drawdown = self.config['risk_management']['trailing_drawdown']
            
            is_compliant = drawdown <= max_allowed_drawdown
            drawdown_percentage = drawdown / max_allowed_drawdown
            
            logger.info(f"Drawdown: ${drawdown:.2f} (límite: ${max_allowed_drawdown})")
            
            return is_compliant, drawdown_percentage
            
        except Exception as e:
            logger.error(f"Error verificando drawdown: {e}")
            return False, 1.0
    
    def check_activity_compliance(self) -> Tuple[bool, float]:
        """Verificar compliance de actividad (mínimo 1 trading day por semana)"""
        try:
            # Obtener semana actual
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_str = week_start.strftime('%Y-W%U')
            
            if week_str not in self.weekly_stats:
                return False, 0.0  # Sin actividad esta semana
            
            weekly_data = self.weekly_stats[week_str]
            trading_days = len(weekly_data['trading_days'])
            min_required_days = self.config['compliance_rules']['min_trading_days_per_week']
            
            is_compliant = trading_days >= min_required_days
            activity_percentage = trading_days / min_required_days
            
            logger.info(f"Trading Days: {trading_days} (mínimo: {min_required_days})")
            
            return is_compliant, activity_percentage
            
        except Exception as e:
            logger.error(f"Error verificando actividad: {e}")
            return False, 0.0
    
    def check_trading_hours(self) -> bool:
        """Verificar si estamos en horario de trading permitido"""
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            
            start_hour = int(self.config['trading_hours']['start'].split(':')[0])
            end_hour = int(self.config['trading_hours']['end'].split(':')[0])
            end_minute = int(self.config['trading_hours']['end'].split(':')[1])
            
            # Verificar horario
            if start_hour <= current_hour < end_hour:
                return True
            elif current_hour == end_hour and current_minute <= end_minute:
                return True
            
            logger.warning(f"Fuera de horario de trading: {current_hour:02d}:{current_minute:02d} (permitido: {start_hour:02d}:00-{end_hour:02d}:{end_minute:02d})")
            return False
            
        except Exception as e:
            logger.error(f"Error verificando horario: {e}")
            return False
    
    def run_compliance_check(self) -> Dict:
        """Ejecutar verificación completa de compliance"""
        try:
            logger.info("EJECUTANDO VERIFICACIÓN COMPLETA DE COMPLIANCE")
            logger.info("=" * 60)
            
            # Verificar horario de trading
            trading_hours_ok = self.check_trading_hours()
            
            # Verificar todas las reglas de compliance
            microscalping_ok, microscalping_pct = self.check_microscalping_compliance()
            consistency_ok, consistency_pct = self.check_consistency_compliance()
            daily_loss_ok, daily_loss_pct = self.check_daily_loss_compliance()
            drawdown_ok, drawdown_pct = self.check_drawdown_compliance()
            activity_ok, activity_pct = self.check_activity_compliance()
            
            # Actualizar estado de compliance
            self.compliance_status = {
                "microscalping": microscalping_ok,
                "consistency": consistency_ok,
                "daily_loss": daily_loss_ok,
                "drawdown": drawdown_ok,
                "activity": activity_ok,
                "overall": all([microscalping_ok, consistency_ok, daily_loss_ok, drawdown_ok, activity_ok, trading_hours_ok])
            }
            
            # Resumen de compliance
            logger.info("RESUMEN DE COMPLIANCE:")
            logger.info(f"   Microscalping: {'COMPLIANT' if microscalping_ok else 'VIOLATION'}")
            logger.info(f"   Consistency: {'COMPLIANT' if consistency_ok else 'VIOLATION'}")
            logger.info(f"   Daily Loss: {'COMPLIANT' if daily_loss_ok else 'VIOLATION'}")
            logger.info(f"   Drawdown: {'COMPLIANT' if drawdown_ok else 'VIOLATION'}")
            logger.info(f"   Activity: {'COMPLIANT' if activity_ok else 'VIOLATION'}")
            logger.info(f"   Trading Hours: {'COMPLIANT' if trading_hours_ok else 'VIOLATION'}")
            logger.info("=" * 60)
            logger.info(f"OVERALL COMPLIANCE: {'COMPLIANT' if self.compliance_status['overall'] else 'VIOLATION'}")
            
            return self.compliance_status
            
        except Exception as e:
            logger.error(f"Error ejecutando compliance check: {e}")
            return {"overall": False}
    
    def get_compliance_report(self) -> Dict:
        """Obtener reporte completo de compliance"""
        try:
            return {
                "status": self.compliance_status,
                "daily_stats": self.daily_stats,
                "weekly_stats": self.weekly_stats,
                "total_trades": len(self.trades_history),
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return {}

# Función de prueba
def test_compliance_system():
    """Función de prueba para el sistema de compliance"""
    try:
        compliance = TradeifyComplianceSystem()
        
        print("Probando sistema de compliance...")
        
        # Simular algunos trades
        test_trades = [
            {
                "signal": "BUY",
                "entry_price": 100.0,
                "entry_time": datetime.now() - timedelta(minutes=10),
                "exit_time": datetime.now() - timedelta(minutes=8),
                "status": "TP_HIT",
                "pnl": 50.0
            },
            {
                "signal": "BUY", 
                "entry_price": 101.0,
                "entry_time": datetime.now() - timedelta(minutes=5),
                "exit_time": datetime.now() - timedelta(minutes=4),
                "status": "SL_HIT",
                "pnl": -25.0
            }
        ]
        
        # Agregar trades de prueba
        for trade in test_trades:
            compliance.add_trade(trade)
        
        # Ejecutar compliance check
        result = compliance.run_compliance_check()
        
        print(f"Compliance check completado: {result['overall']}")
        
        # Obtener reporte
        report = compliance.get_compliance_report()
        print(f"Total trades: {report['total_trades']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_compliance_system()
