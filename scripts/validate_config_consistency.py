#!/usr/bin/env python3
"""
🔍 VALIDADOR DE CONSISTENCIA DE CONFIGURACIÓN
============================================
Este script valida que todos los archivos de configuración
sean consistentes con los parámetros maestros de la estrategia V5.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

class ConfigValidator:
    """Validador de consistencia de configuración"""
    
    def __init__(self):
        """Inicializar validador"""
        self.config_dir = Path("config")
        self.master_config = None
        self.validation_results = {}
        
    def load_master_config(self) -> bool:
        """Cargar configuración maestra"""
        try:
            master_file = self.config_dir / "config_master.json"
            if not master_file.exists():
                print("❌ Archivo maestro de configuración no encontrado")
                return False
                
            with open(master_file, 'r') as f:
                self.master_config = json.load(f)
            
            print("✅ Configuración maestra cargada")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando configuración maestra: {e}")
            return False
    
    def validate_file(self, filename: str) -> Dict:
        """Validar un archivo de configuración específico"""
        try:
            file_path = self.config_dir / filename
            if not file_path.exists():
                return {"status": "ERROR", "message": f"Archivo no encontrado: {filename}"}
            
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Extraer parámetros de estrategia V5
            strategy_params = self.extract_strategy_params(config, filename)
            
            # Validar contra parámetros maestros
            validation_result = self.validate_strategy_params(strategy_params, filename)
            
            return validation_result
            
        except Exception as e:
            return {"status": "ERROR", "message": f"Error validando {filename}: {e}"}
    
    def extract_strategy_params(self, config: Dict, filename: str) -> Dict:
        """Extraer parámetros de estrategia V5 del archivo"""
        params = {}
        
        if filename == "strategy_v5.json":
            # Archivo maestro de estrategia
            params.update(config.get("core_parameters", {}))
            params.update(config.get("technical_indicators", {}))
            params.update(config.get("trading_constraints", {}))
            params.update(config.get("risk_management", {}))
            params.update(config.get("compliance_rules", {}))
            
        elif "tradeify" in filename:
            # Archivos de configuración de Tradeify
            strategy_config = config.get("strategy_config", {}).get("v5_optimized", {})
            params.update(strategy_config)
            
        return params
    
    def validate_strategy_params(self, params: Dict, filename: str) -> Dict:
        """Validar parámetros contra configuración maestra"""
        if not self.master_config:
            return {"status": "ERROR", "message": "Configuración maestra no cargada"}
        
        master_params = self.master_config["strategy_v5_optimized"]
        
        # Parámetros críticos a validar
        critical_params = [
            "ema_period", "rsi_max", "rsi_min", "atr_threshold",
            "take_profit", "stop_loss"
        ]
        
        validation_result = {
            "status": "PASS",
            "filename": filename,
            "total_params": len(critical_params),
            "valid_params": 0,
            "invalid_params": 0,
            "missing_params": 0,
            "details": []
        }
        
        for param in critical_params:
            if param in params:
                expected_value = self.get_master_value(master_params, param)
                actual_value = params[param]
                
                if expected_value == actual_value:
                    validation_result["valid_params"] += 1
                    validation_result["details"].append({
                        "param": param,
                        "status": "✅",
                        "expected": expected_value,
                        "actual": actual_value
                    })
                else:
                    validation_result["invalid_params"] += 1
                    validation_result["details"].append({
                        "param": param,
                        "status": "❌",
                        "expected": expected_value,
                        "actual": actual_value
                    })
            else:
                validation_result["missing_params"] += 1
                validation_result["details"].append({
                    "param": param,
                    "status": "⚠️",
                    "expected": "N/A",
                    "actual": "MISSING"
                })
        
        # Determinar estado general
        if validation_result["invalid_params"] > 0:
            validation_result["status"] = "FAIL"
        elif validation_result["missing_params"] > 0:
            validation_result["status"] = "WARNING"
        
        return validation_result
    
    def get_master_value(self, master_params: Dict, param: str):
        """Obtener valor maestro para un parámetro"""
        # Buscar en diferentes secciones
        for section in ["core_parameters", "technical_indicators", "trading_constraints", "risk_management"]:
            if section in master_params and param in master_params[section]:
                return master_params[section][param]
        return None
    
    def run_validation(self) -> bool:
        """Ejecutar validación completa"""
        print("🔍 INICIANDO VALIDACIÓN DE CONSISTENCIA DE CONFIGURACIÓN")
        print("=" * 60)
        
        if not self.load_master_config():
            return False
        
        # Archivos a validar
        config_files = [
            "strategy_v5.json",
            "tradeify_real_config.json", 
            "tradeify_demo_config.json"
        ]
        
        all_passed = True
        
        for filename in config_files:
            print(f"\n📋 Validando: {filename}")
            result = self.validate_file(filename)
            self.validation_results[filename] = result
            
            if result["status"] == "PASS":
                print(f"   ✅ {filename}: CONSISTENTE")
            elif result["status"] == "WARNING":
                print(f"   ⚠️ {filename}: ADVERTENCIA")
                all_passed = False
            else:
                print(f"   ❌ {filename}: INCONSISTENTE")
                all_passed = False
        
        # Resumen detallado
        self.print_detailed_results()
        
        return all_passed
    
    def print_detailed_results(self):
        """Imprimir resultados detallados de validación"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DETALLADOS DE VALIDACIÓN")
        print("=" * 60)
        
        for filename, result in self.validation_results.items():
            if result["status"] == "ERROR":
                print(f"\n❌ {filename}: {result['message']}")
                continue
                
            print(f"\n📋 {filename}:")
            print(f"   Estado: {result['status']}")
            print(f"   Parámetros válidos: {result['valid_params']}/{result['total_params']}")
            
            if result["details"]:
                print("   Detalles:")
                for detail in result["details"]:
                    status = detail["status"]
                    param = detail["param"]
                    expected = detail["expected"]
                    actual = detail["actual"]
                    print(f"      {status} {param}: esperado={expected}, actual={actual}")
        
        # Resumen general
        total_files = len(self.validation_results)
        passed_files = sum(1 for r in self.validation_results.values() if r["status"] == "PASS")
        warning_files = sum(1 for r in self.validation_results.values() if r["status"] == "WARNING")
        failed_files = sum(1 for r in self.validation_results.values() if r["status"] == "FAIL")
        
        print(f"\n" + "=" * 60)
        print("🎯 RESUMEN GENERAL")
        print("=" * 60)
        print(f"📁 Total de archivos: {total_files}")
        print(f"✅ Archivos consistentes: {passed_files}")
        print(f"⚠️ Archivos con advertencias: {warning_files}")
        print(f"❌ Archivos inconsistentes: {failed_files}")
        
        if failed_files == 0 and warning_files == 0:
            print("\n🎉 ¡TODA LA CONFIGURACIÓN ES CONSISTENTE!")
        elif failed_files == 0:
            print("\n⚠️ Configuración mayormente consistente (algunas advertencias)")
        else:
            print("\n❌ Se encontraron inconsistencias que requieren corrección")

def main():
    """Función principal"""
    validator = ConfigValidator()
    success = validator.run_validation()
    
    if success:
        print("\n✅ Validación completada exitosamente")
        exit(0)
    else:
        print("\n❌ Validación completada con errores")
        exit(1)

if __name__ == "__main__":
    main()
