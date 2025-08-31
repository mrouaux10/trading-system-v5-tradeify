#!/usr/bin/env python3
"""
Validador Simple para Lightning 50K Strategy
===========================================
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_lightning_50k_strategy():
    """Validar configuración básica de lightning_50k_strategy"""
    try:
        config_file = Path("config/lightning_50k_strategy.json")
        
        if not config_file.exists():
            logger.error("Archivo lightning_50k_strategy.json no encontrado")
            return False
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        logger.info("Validando lightning_50k_strategy.json...")
        
        # Verificaciones básicas
        errors = []
        warnings = []
        
        # Verificar que existe la configuración
        if not config.get("strategy_name"):
            errors.append("strategy_name no encontrado")
        
        if not config.get("version"):
            errors.append("version no encontrada")
        
        # Verificar account settings
        account_settings = config.get("account_settings", {})
        if account_settings.get("account_type") != "Lightning 50K Funded":
            warnings.append(f"Tipo de cuenta: {account_settings.get('account_type')}")
        
        if account_settings.get("initial_balance") != 50000:
            errors.append(f"Balance inicial incorrecto: {account_settings.get('initial_balance')}")
        
        # Verificar risk management si existe
        risk_mgmt = config.get("risk_management", {})
        if risk_mgmt:
            if risk_mgmt.get("max_drawdown") and risk_mgmt.get("max_drawdown") != 2000:
                warnings.append(f"Max drawdown: {risk_mgmt.get('max_drawdown')} (esperado: 2000)")
            
            if risk_mgmt.get("daily_loss_limit") and risk_mgmt.get("daily_loss_limit") != 1250:
                warnings.append(f"Daily loss limit: {risk_mgmt.get('daily_loss_limit')} (esperado: 1250)")
        
        # Verificar trading rules si existe
        trading_rules = config.get("trading_rules", {})
        if trading_rules:
            consistency = trading_rules.get("consistency_rule_percentage")
            if consistency and consistency != 20:
                warnings.append(f"Consistency rule: {consistency}% (esperado: 20%)")
        
        # Mostrar resultados
        if errors:
            logger.error("ERRORES ENCONTRADOS:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        if warnings:
            logger.warning("ADVERTENCIAS:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        logger.info("✅ Configuración básica validada correctamente")
        logger.info(f"Strategy: {config.get('strategy_name')} v{config.get('version')}")
        logger.info(f"Status: {config.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validando configuración: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("VALIDADOR SIMPLE LIGHTNING 50K STRATEGY")
    print("="*60)
    
    if validate_lightning_50k_strategy():
        print("\n✅ VALIDACIÓN EXITOSA")
        exit(0)
    else:
        print("\n❌ VALIDACIÓN FALLÓ")
        exit(1)
