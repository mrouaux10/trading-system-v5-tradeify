#!/usr/bin/env python3
"""
SISTEMA DE LIMPIEZA AUTOMÁTICA
================================

Script para limpiar archivos temporales y mantener el sistema optimizado.
"""

import os
import glob
import shutil
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingSystemCleaner:
    """Limpiador automático del sistema de trading"""
    
    def __init__(self):
        """Inicializar limpiador"""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.cleanup_patterns = [
            # Logs temporales
            "*.log",
            "bot_*.log",
            "demo_*.log",
            
            # Logs de trades temporales
            "trade_log_cronologico_*.txt",
            
            # Archivos temporales
            "*.tmp",
            "*.temp",
            "*.bak",
            
            # Caché de Python
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            
            # Archivos del sistema
            ".DS_Store",
            "Thumbs.db"
        ]
        
        # Archivos a NO eliminar
        self.protected_files = [
            "requirements.txt",
            "README.md",
            "config/tradeify_real_config.json",
            "config/strategy_v5.json",
            "config/tradeify_demo_config.json",
            "config/config_master.json",
            "testing/MNQ_09-25_30days_1min.txt"
        ]
    
    def is_protected_file(self, file_path):
        """Verificar si un archivo está protegido"""
        for protected in self.protected_files:
            if protected in file_path:
                return True
        return False
    
    def cleanup_logs(self):
        """Limpiar logs temporales"""
        try:
            logger.info("🧹 Limpiando logs temporales...")
            
            # Buscar logs en el directorio raíz y carpeta logs
            log_files = glob.glob(os.path.join(self.project_root, "*.log"))
            log_files.extend(glob.glob(os.path.join(self.project_root, "*.txt")))
            
            # Buscar logs en la carpeta logs
            logs_dir = os.path.join(self.project_root, "logs")
            if os.path.exists(logs_dir):
                log_files.extend(glob.glob(os.path.join(logs_dir, "*.log")))
                log_files.extend(glob.glob(os.path.join(logs_dir, "*.txt")))
            
            cleaned_count = 0
            for log_file in log_files:
                if not self.is_protected_file(log_file):
                    # Verificar si es un log temporal
                    filename = os.path.basename(log_file)
                    if (filename.startswith("bot_") or 
                        filename.startswith("demo_") or
                        filename.startswith("trade_log_cronologico_")):
                        
                        try:
                            os.remove(log_file)
                            logger.info(f"   ✅ Eliminado: {filename}")
                            cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"   ⚠️ No se pudo eliminar {filename}: {e}")
            
            logger.info(f"✅ Logs limpiados: {cleaned_count} archivos")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Error limpiando logs: {e}")
            return 0
    
    def cleanup_cache(self):
        """Limpiar caché de Python"""
        try:
            logger.info("🧹 Limpiando caché de Python...")
            
            # Buscar directorios __pycache__
            cache_dirs = []
            for root, dirs, files in os.walk(self.project_root):
                if "__pycache__" in dirs:
                    cache_dirs.append(os.path.join(root, "__pycache__"))
            
            cleaned_count = 0
            for cache_dir in cache_dirs:
                try:
                    shutil.rmtree(cache_dir)
                    logger.info(f"   ✅ Eliminado: {cache_dir}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"   ⚠️ No se pudo eliminar {cache_dir}: {e}")
            
            # Buscar archivos .pyc y .pyo
            pyc_files = glob.glob(os.path.join(self.project_root, "**/*.pyc"), recursive=True)
            pyc_files.extend(glob.glob(os.path.join(self.project_root, "**/*.pyo"), recursive=True))
            
            for pyc_file in pyc_files:
                try:
                    os.remove(pyc_file)
                    logger.info(f"   ✅ Eliminado: {pyc_file}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"   ⚠️ No se pudo eliminar {pyc_file}: {e}")
            
            logger.info(f"✅ Caché limpiado: {cleaned_count} elementos")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Error limpiando caché: {e}")
            return 0
    
    def cleanup_old_backups(self, days_old=7):
        """Limpiar backups antiguos"""
        try:
            logger.info(f"🧹 Limpiando backups antiguos (más de {days_old} días)...")
            
            backup_dir = os.path.join(self.project_root, "config", "backups")
            if not os.path.exists(backup_dir):
                logger.info("   ℹ️ No hay directorio de backups")
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for backup_file in os.listdir(backup_dir):
                if backup_file.endswith('.json'):
                    backup_path = os.path.join(backup_dir, backup_file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
                    
                    if file_time < cutoff_date:
                        try:
                            os.remove(backup_path)
                            logger.info(f"   ✅ Eliminado backup antiguo: {backup_file}")
                            cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"   ⚠️ No se pudo eliminar {backup_file}: {e}")
            
            logger.info(f"✅ Backups antiguos limpiados: {cleaned_count} archivos")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Error limpiando backups: {e}")
            return 0
    
    def cleanup_old_reports(self, days_old=3):
        """Limpiar reportes antiguos"""
        try:
            logger.info(f"🧹 Limpiando reportes antiguos (más de {days_old} días)...")
            
            logs_dir = os.path.join(self.project_root, "logs")
            if not os.path.exists(logs_dir):
                logger.info("   ℹ️ No hay directorio de logs")
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for report_file in os.listdir(logs_dir):
                if report_file.startswith("activation_report_") and report_file.endswith('.txt'):
                    report_path = os.path.join(logs_dir, report_file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(report_path))
                    
                    if file_time < cutoff_date:
                        try:
                            os.remove(report_path)
                            logger.info(f"   ✅ Eliminado reporte antiguo: {report_file}")
                            cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"   ⚠️ No se pudo eliminar {report_file}: {e}")
            
            logger.info(f"✅ Reportes antiguos limpiados: {cleaned_count} archivos")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Error limpiando reportes: {e}")
            return 0
    
    def run_full_cleanup(self):
        """Ejecutar limpieza completa"""
        try:
            logger.info("🚀 INICIANDO LIMPIEZA COMPLETA DEL SISTEMA")
            logger.info("=" * 60)
            
            total_cleaned = 0
            
            # Limpiar logs
            total_cleaned += self.cleanup_logs()
            
            # Limpiar caché
            total_cleaned += self.cleanup_cache()
            
            # Limpiar backups antiguos
            total_cleaned += self.cleanup_old_backups()
            
            # Limpiar reportes antiguos
            total_cleaned += self.cleanup_old_reports()
            
            logger.info("=" * 60)
            logger.info(f"🎉 LIMPIEZA COMPLETADA: {total_cleaned} elementos eliminados")
            logger.info("✅ Sistema optimizado y listo")
            
            return total_cleaned
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza completa: {e}")
            return 0

def main():
    """Función principal"""
    try:
        cleaner = TradingSystemCleaner()
        total_cleaned = cleaner.run_full_cleanup()
        
        if total_cleaned > 0:
            print(f"\n🎉 Sistema limpiado exitosamente: {total_cleaned} elementos eliminados")
        else:
            print("\n✨ Sistema ya está limpio y optimizado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en función principal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
