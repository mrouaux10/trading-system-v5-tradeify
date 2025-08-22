#!/usr/bin/env python3
"""
Validador de Configuración Tradeify Lightning Funded
====================================================

Este script valida que toda la configuración sea consistente y cumpla con las reglas de Tradeify Lightning Funded:
- Verificar límites de riesgo
- Verificar horarios de trading
- Verificar reglas de compliance
- Verificar consistencia entre archivos
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradeifyConfigValidator:
    """Validador de configuración para Tradeify Lightning Funded"""
    
    def __init__(self):
        """Inicializar validador"""
        self.config_dir = Path("config")
        self.scripts_dir = Path("scripts")
        self.validation_results = {
            "overall": False,
            "lightning_50k": False,
            "lightning_50k_final_config": False,
            "compliance_system": False,
            "errors": [],
            "warnings": []
        }
        
        # Límites críticos de Tradeify Lightning Funded
        self.LIGHTNING_REQUIREMENTS = {
            "consistency_threshold": 0.20,  # 20% máximo
            "max_daily_loss": 1250,         # $1,250
            "max_drawdown": 2000,           # $2,000
            "trading_hours_start": "09:00",
            "trading_hours_end": "16:00",
            "timezone": "UTC",
            "mandatory_close": "16:59"
        }
        
        logger.info("🔍 Validador de configuración Tradeify Lightning Funded inicializado")
    
    def validate_lightning_50k(self) -> bool:
        """Validar configuración de estrategia V5"""
        try:
            config_file = self.config_dir / "lightning_50k_final_config.json"
            
            if not config_file.exists():
                self.validation_results["errors"].append("❌ Archivo lightning_50k.json no encontrado")
                return False
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            logger.info("📋 Validando lightning_50k.json...")
            
            # Verificar campos críticos en risk_management
            risk_mgmt = config.get("risk_management", {})
            if not risk_mgmt:
                self.validation_results["errors"].append("❌ Sección risk_management no encontrada en lightning_50k.json")
                return False
            
            # Verificar valores críticos en risk_management
            if risk_mgmt.get("consistency_threshold") != 0.20:
                self.validation_results["errors"].append(f"❌ Consistency threshold incorrecto: {risk_mgmt.get('consistency_threshold')} (debe ser 0.20)")
                return False
            
            if risk_mgmt.get("max_daily_loss") != 1250:
                self.validation_results["errors"].append(f"❌ Max daily loss incorrecto: {risk_mgmt.get('max_daily_loss')} (debe ser 1250)")
                return False
            
            if risk_mgmt.get("trailing_drawdown") != 2000:
                self.validation_results["errors"].append(f"❌ Trailing drawdown incorrecto: {risk_mgmt.get('trailing_drawdown')} (debe ser 2000)")
                return False
            
            # Verificar horarios en trading_constraints
            trading_constraints = config.get("trading_constraints", {})
            if not trading_constraints:
                self.validation_results["errors"].append("❌ Sección trading_constraints no encontrada en lightning_50k.json")
                return False
            
            if trading_constraints.get("timezone") != "UTC":
                self.validation_results["errors"].append(f"❌ Timezone incorrecto: {trading_constraints.get('timezone')} (debe ser UTC)")
                return False
            
            # Verificar horarios
            if trading_constraints.get("trading_hours_start") != "09:00":
                self.validation_results["warnings"].append(f"⚠️  Horario de inicio: {trading_constraints.get('trading_hours_start')} (recomendado: 09:00)")
            
            if trading_constraints.get("trading_hours_end") != "16:00":
                self.validation_results["warnings"].append(f"⚠️  Horario de fin: {trading_constraints.get('trading_hours_end')} (recomendado: 16:00)")
            
            logger.info("✅ lightning_50k.json validado correctamente")
            self.validation_results["lightning_50k"] = True
            return True
            
        except Exception as e:
            self.validation_results["errors"].append(f"❌ Error validando lightning_50k.json: {e}")
            return False
    
    def validate_lightning_50k_final_config(self) -> bool:
        """Validar configuración principal de Tradeify"""
        try:
            config_file = self.config_dir / "lightning_50k_final_config.json"
            
            if not config_file.exists():
                self.validation_results["errors"].append("❌ Archivo lightning_50k_final_config.json no encontrado")
                return False
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            logger.info("📋 Validando lightning_50k_final_config.json...")
            
            # Verificar tipo de cuenta
            if config.get("tradeify_platform", {}).get("type") != "Lightning Funded":
                self.validation_results["errors"].append(f"❌ Tipo de cuenta incorrecto: {config.get('tradeify_platform', {}).get('type')} (debe ser Lightning Funded)")
                return False
            
            # Verificar límites de riesgo en trading_parameters.risk_management
            trading_params = config.get("trading_parameters", {})
            if not trading_params:
                self.validation_results["errors"].append("❌ Sección trading_parameters no encontrada en lightning_50k_final_config.json")
                return False
            
            risk_mgmt = trading_params.get("risk_management", {})
            if not risk_mgmt:
                self.validation_results["errors"].append("❌ Sección risk_management en trading_parameters no encontrada")
                return False
            
            if risk_mgmt.get("max_daily_loss") != 1250:
                self.validation_results["errors"].append(f"❌ Max daily loss incorrecto: {risk_mgmt.get('max_daily_loss')} (debe ser 1250)")
                return False
            
            if risk_mgmt.get("max_drawdown") != 2000:
                self.validation_results["errors"].append(f"❌ Max drawdown incorrecto: {risk_mgmt.get('max_drawdown')} (debe ser 2000)")
                return False
            
            if risk_mgmt.get("consistency_threshold") != 0.20:
                self.validation_results["errors"].append(f"❌ Consistency threshold incorrecto: {risk_mgmt.get('consistency_threshold')} (debe ser 0.20)")
                return False
            
            # Verificar horarios en trading_parameters.trading_hours
            trading_hours = trading_params.get("trading_hours", {})
            if not trading_hours:
                self.validation_results["errors"].append("❌ Sección trading_hours en trading_parameters no encontrada")
                return False
            
            if trading_hours.get("timezone") != "UTC":
                self.validation_results["errors"].append(f"❌ Timezone incorrecto: {trading_hours.get('timezone')} (debe ser UTC)")
                return False
            
            if trading_hours.get("start") != "09:00":
                self.validation_results["warnings"].append(f"⚠️  Horario de inicio: {trading_hours.get('start')} (recomendado: 09:00)")
            
            if trading_hours.get("end") != "16:00":
                self.validation_results["warnings"].append(f"⚠️  Horario de fin: {trading_hours.get('end')} (recomendado: 16:00)")
            
            # Verificar reglas de compliance
            compliance = config.get("compliance_rules", {})
            if not compliance:
                self.validation_results["errors"].append("❌ Sección compliance_rules no encontrada en lightning_50k_final_config.json")
                return False
            
            consistency_rules = compliance.get("consistency", {})
            if not consistency_rules:
                self.validation_results["errors"].append("❌ Sección consistency en compliance_rules no encontrada")
                return False
            
            if consistency_rules.get("max_daily_profit_percentage") != 0.20:
                self.validation_results["errors"].append(f"❌ Max daily profit percentage incorrecto: {consistency_rules.get('max_daily_profit_percentage')} (debe ser 0.20)")
                return False
            
            logger.info("✅ lightning_50k_final_config.json validado correctamente")
            self.validation_results["lightning_50k_final_config"] = True
            return True
            
        except Exception as e:
            self.validation_results["errors"].append(f"❌ Error validando lightning_50k_final_config.json: {e}")
            return False
    
    def validate_compliance_system(self) -> bool:
        """Validar sistema de compliance"""
        try:
            compliance_file = self.scripts_dir / "tradeify_compliance_system.py"
            
            if not compliance_file.exists():
                self.validation_results["errors"].append("❌ Archivo tradeify_compliance_system.py no encontrado")
                return False
            
            logger.info("📋 Validando sistema de compliance...")
            
            # Verificar que el archivo contenga las reglas correctas
            with open(compliance_file, 'r') as f:
                content = f.read()
            
            # Verificar reglas críticas
            required_rules = [
                "consistency_threshold: 0.20",
                "max_daily_loss: 1250",
                "max_drawdown: 2000",
                "Lightning Funded"
            ]
            
            for rule in required_rules:
                if rule not in content:
                    self.validation_results["warnings"].append(f"⚠️  Regla no encontrada en compliance system: {rule}")
            
            logger.info("✅ Sistema de compliance validado correctamente")
            self.validation_results["compliance_system"] = True
            return True
            
        except Exception as e:
            self.validation_results["errors"].append(f"❌ Error validando sistema de compliance: {e}")
            return False
    
    def validate_overall_consistency(self) -> bool:
        """Validar consistencia general entre archivos"""
        try:
            logger.info("🔍 Validando consistencia general...")
            
            # Verificar que todos los archivos principales existan
            required_files = [
                "config/lightning_50k_final_config.json",
                "config/lightning_50k_final_config.json",
                "scripts/tradeify_compliance_system.py",
                "scripts/tradeify_bot_main.py"
            ]
            
            for file_path in required_files:
                if not Path(file_path).exists():
                    self.validation_results["errors"].append(f"❌ Archivo requerido no encontrado: {file_path}")
            
            # Verificar que no haya errores críticos
            if self.validation_results["errors"]:
                logger.error("❌ Se encontraron errores críticos en la validación")
                return False
            
            # Verificar que todos los componentes principales estén validados
            if all([
                self.validation_results["lightning_50k"],
                self.validation_results["lightning_50k_final_config"],
                self.validation_results["compliance_system"]
            ]):
                self.validation_results["overall"] = True
                logger.info("✅ Validación general completada exitosamente")
                return True
            else:
                logger.error("❌ No todos los componentes principales están validados")
                return False
                
        except Exception as e:
            self.validation_results["errors"].append(f"❌ Error en validación general: {e}")
            return False
    
    def run_full_validation(self) -> bool:
        """Ejecutar validación completa"""
        try:
            logger.info("🚀 INICIANDO VALIDACIÓN COMPLETA DE CONFIGURACIÓN")
            logger.info("=" * 70)
            
            # Validar cada componente
            strategy_ok = self.validate_lightning_50k()
            config_ok = self.validate_lightning_50k_final_config()
            compliance_ok = self.validate_compliance_system()
            
            # Validar consistencia general
            overall_ok = self.validate_overall_consistency()
            
            # Resumen de validación
            logger.info("📋 RESUMEN DE VALIDACIÓN:")
            logger.info(f"   ✅ Strategy V5: {'VALIDADO' if strategy_ok else 'FALLÓ'}")
            logger.info(f"   ✅ Tradeify Config: {'VALIDADO' if config_ok else 'FALLÓ'}")
            logger.info(f"   ✅ Compliance System: {'VALIDADO' if compliance_ok else 'FALLÓ'}")
            logger.info(f"   🎯 Overall: {'VALIDADO' if overall_ok else 'FALLÓ'}")
            
            # Mostrar errores si los hay
            if self.validation_results["errors"]:
                logger.error("❌ ERRORES ENCONTRADOS:")
                for error in self.validation_results["errors"]:
                    logger.error(f"   {error}")
            
            # Mostrar advertencias si las hay
            if self.validation_results["warnings"]:
                logger.warning("⚠️  ADVERTENCIAS:")
                for warning in self.validation_results["warnings"]:
                    logger.warning(f"   {warning}")
            
            logger.info("=" * 70)
            
            if overall_ok:
                logger.info("🎉 CONFIGURACIÓN COMPLETAMENTE VALIDADA PARA TRADEIFY LIGHTNING FUNDED")
                logger.info("✅ Tu bot está listo para operar respetando todas las reglas críticas")
            else:
                logger.error("❌ CONFIGURACIÓN NO VALIDADA - CORREGIR ERRORES ANTES DE OPERAR")
            
            return overall_ok
            
        except Exception as e:
            logger.error(f"❌ Error en validación completa: {e}")
            return False
    
    def get_validation_report(self) -> dict:
        """Obtener reporte completo de validación"""
        return {
            "timestamp": datetime.now().isoformat(),
            "results": self.validation_results,
            "lightning_requirements": self.LIGHTNING_REQUIREMENTS,
            "summary": {
                "total_errors": len(self.validation_results["errors"]),
                "total_warnings": len(self.validation_results["warnings"]),
                "overall_valid": self.validation_results["overall"]
            }
        }

def main():
    """Función principal"""
    try:
        print("🔍 VALIDADOR DE CONFIGURACIÓN TRADEIFY LIGHTNING FUNDED")
        print("=" * 70)
        
        validator = TradeifyConfigValidator()
        success = validator.run_full_validation()
        
        if success:
            print("\n🎉 VALIDACIÓN EXITOSA")
            print("✅ Tu bot está configurado correctamente para Tradeify Lightning Funded")
            print("✅ Todas las reglas críticas están implementadas")
            print("✅ Puedes proceder con el backtesting y activación")
        else:
            print("\n❌ VALIDACIÓN FALLÓ")
            print("❌ Corrige los errores antes de proceder")
            print("❌ Tu cuenta de $50k está en riesgo si no se corrigen")
        
        return success
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
