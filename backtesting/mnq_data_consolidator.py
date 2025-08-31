#!/usr/bin/env python3
"""
Consolidador de datos MNQ - Unifica todos los contratos en un dataset continuo
Optimizado para las reglas Tradeify Lightning Funded 50K
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MNQDataConsolidator:
    def __init__(self, data_dir="./historical/"):
        self.data_dir = data_dir
        self.consolidated_data = None
        
    def load_all_mnq_files(self):
        """Cargar todos los archivos MNQ y consolidarlos"""
        logger.info("Iniciando consolidación de archivos MNQ...")
        
        # Buscar todos los archivos MNQ
        pattern = os.path.join(self.data_dir, "MNQ*.txt")
        files = glob.glob(pattern)
        files.sort()  # Ordenar por nombre
        
        logger.info(f"Archivos encontrados: {len(files)}")
        for file in files:
            logger.info(f"  - {os.path.basename(file)}")
        
        all_data = []
        total_bars = 0
        
        for file_path in files:
            logger.info(f"Procesando: {os.path.basename(file_path)}")
            
            try:
                # Leer archivo con formato: YYYYMMDD HHMMSS;O;H;L;C;V
                df = pd.read_csv(file_path, sep=';', header=None,
                               names=['datetime_str', 'open', 'high', 'low', 'close', 'volume'])
                
                # Convertir datetime
                df['datetime'] = pd.to_datetime(df['datetime_str'], format='%Y%m%d %H%M%S')
                
                # Filtrar horarios de trading (6:30 AM - 5:00 PM CT)
                df['hour'] = df['datetime'].dt.hour
                df['minute'] = df['datetime'].dt.minute
                
                # Horarios de trading: 6:30-17:00 CT (12:30-23:00 UTC)
                trading_hours = (
                    ((df['hour'] >= 12) & (df['hour'] < 23)) |  # 12:30-22:59 UTC
                    ((df['hour'] == 23) & (df['minute'] == 0))   # 23:00 UTC exacto
                )
                
                df_filtered = df[trading_hours].copy()
                
                # Limpiar datos inválidos
                df_filtered = df_filtered[
                    (df_filtered['open'] > 0) & 
                    (df_filtered['high'] >= df_filtered['low']) &
                    (df_filtered['close'] > 0) &
                    (df_filtered['volume'] >= 0)
                ]
                
                bars_loaded = len(df_filtered)
                logger.info(f"  Barras cargadas: {bars_loaded:,}")
                
                if bars_loaded > 0:
                    all_data.append(df_filtered)
                    total_bars += bars_loaded
                
            except Exception as e:
                logger.error(f"  Error procesando {file_path}: {e}")
                continue
        
        if not all_data:
            raise ValueError("No se pudieron cargar datos válidos")
        
        # Consolidar todos los dataframes
        logger.info("Consolidando datasets...")
        consolidated = pd.concat(all_data, ignore_index=True)
        
        # Ordenar por datetime y eliminar duplicados
        consolidated = consolidated.sort_values('datetime').drop_duplicates(subset=['datetime'])
        
        # Seleccionar columnas finales
        self.consolidated_data = consolidated[['datetime', 'open', 'high', 'low', 'close', 'volume']].reset_index(drop=True)
        
        logger.info(f"Consolidación completada:")
        logger.info(f"  Total de barras: {len(self.consolidated_data):,}")
        logger.info(f"  Período: {self.consolidated_data['datetime'].min()} - {self.consolidated_data['datetime'].max()}")
        
        return self.consolidated_data
    
    def save_consolidated_data(self, output_file="MNQ_consolidated_2024-2025.csv"):
        """Guardar datos consolidados"""
        if self.consolidated_data is None:
            raise ValueError("No hay datos consolidados para guardar")
        
        output_path = os.path.join(self.data_dir, output_file)
        self.consolidated_data.to_csv(output_path, index=False)
        logger.info(f"Datos guardados en: {output_path}")
        
        return output_path
    
    def get_data_summary(self):
        """Obtener resumen de los datos consolidados"""
        if self.consolidated_data is None:
            return None
        
        data = self.consolidated_data
        
        summary = {
            'total_bars': len(data),
            'start_date': data['datetime'].min(),
            'end_date': data['datetime'].max(),
            'trading_days': data['datetime'].dt.date.nunique(),
            'avg_volume': data['volume'].mean(),
            'price_range': {
                'min': data['low'].min(),
                'max': data['high'].max()
            }
        }
        
        return summary

def main():
    """Función principal"""
    logger.info("Iniciando consolidador MNQ...")
    
    consolidator = MNQDataConsolidator()
    
    try:
        # Cargar y consolidar datos
        data = consolidator.load_all_mnq_files()
        
        # Guardar datos consolidados
        output_file = consolidator.save_consolidated_data()
        
        # Mostrar resumen
        summary = consolidator.get_data_summary()
        
        logger.info("\n" + "="*50)
        logger.info("RESUMEN DE DATOS CONSOLIDADOS:")
        logger.info("="*50)
        logger.info(f"Total de barras: {summary['total_bars']:,}")
        logger.info(f"Período: {summary['start_date']} - {summary['end_date']}")
        logger.info(f"Días de trading: {summary['trading_days']:,}")
        logger.info(f"Rango de precios: ${summary['price_range']['min']:.2f} - ${summary['price_range']['max']:.2f}")
        logger.info(f"Volumen promedio: {summary['avg_volume']:.0f}")
        logger.info(f"Archivo guardado: {output_file}")
        logger.info("="*50)
        
        logger.info("Consolidación completada exitosamente!")
        
    except Exception as e:
        logger.error(f"Error en consolidación: {e}")
        raise

if __name__ == "__main__":
    main()
