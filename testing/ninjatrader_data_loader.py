#!/usr/bin/env python3
"""
Cargador de Datos de NinjaTrader
================================

Carga datos históricos desde archivos .txt exportados de NinjaTrader.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class NinjaTraderDataLoader:
    """Cargador de datos de NinjaTrader"""
    
    def __init__(self):
        """Inicializar cargador"""
        self.data = None
        
    def load_from_txt(self, file_path):
        """Cargar datos desde archivo .txt de NinjaTrader"""
        try:
            print(f"📥 Cargando datos desde: {file_path}")
            
            # Leer archivo .txt
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            print(f"✅ Archivo leído: {len(lines)} líneas")
            
            # Parsear datos
            data_list = []
            for line in lines:
                line = line.strip()
                if line and ';' in line:
                    try:
                        # Formato NinjaTrader: YYYYMMDD HHMMSS;Open;High;Low;Close;Volume
                        parts = line.split(';')
                        if len(parts) >= 6:
                            # Parsear fecha: 20250715 104900 -> 2025-07-15 10:49:00
                            date_str = parts[0]
                            date_part = date_str[:8]  # 20250715
                            time_part = date_str[9:]  # 104900
                            
                            # Formatear fecha
                            formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                            timestamp = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')
                            data_list.append({
                                'timestamp': timestamp,
                                'Open': float(parts[1]),
                                'High': float(parts[2]),
                                'Low': float(parts[3]),
                                'Close': float(parts[4]),
                                'Volume': int(parts[5])
                            })
                    except Exception as e:
                        print(f"⚠️ Error parseando línea: {line[:50]}... - {e}")
                        continue
            
            if not data_list:
                print("❌ No se pudieron parsear datos válidos")
                return False
            
            # Crear DataFrame
            self.data = pd.DataFrame(data_list)
            self.data.set_index('timestamp', inplace=True)
            
            print(f"✅ Datos cargados: {len(self.data)} registros")
            print(f"📅 Período: {self.data.index[0]} a {self.data.index[-1]}")
            
            # Verificar calidad de datos
            self._verify_data_quality()
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando archivo: {e}")
            return False
    
    def _verify_data_quality(self):
        """Verificar calidad de los datos cargados"""
        try:
            print(f"\n🔍 VERIFICACIÓN DE CALIDAD:")
            
            # Verificar timeframe
            if len(self.data) > 1:
                time_diff = self.data.index[1] - self.data.index[0]
                print(f"   ⏰ Timeframe: {time_diff}")
            
            # Verificar horarios
            self.data['hour'] = self.data.index.hour
            trading_hours = self.data[(self.data['hour'] >= 9) & (self.data['hour'] <= 16)]
            non_trading_hours = self.data[(self.data['hour'] < 9) | (self.data['hour'] > 16)]
            
            print(f"   📈 Barras en horario de trading: {len(trading_hours)}")
            print(f"   🌙 Barras fuera de horario: {len(non_trading_hours)}")
            
            # Verificar precios
            min_price = float(self.data['Close'].min())
            max_price = float(self.data['Close'].max())
            avg_price = float(self.data['Close'].mean())
            
            print(f"   💰 Precio mínimo: ${min_price:.2f}")
            print(f"   💰 Precio máximo: ${max_price:.2f}")
            print(f"   💰 Precio promedio: ${avg_price:.2f}")
            
            # Verificar consistencia
            invalid_hl = self.data[self.data['High'] < self.data['Low']]
            invalid_close = self.data[(self.data['Close'] > self.data['High']) | (self.data['Close'] < self.data['Low'])]
            
            print(f"   🔍 Barras con High < Low: {len(invalid_hl)}")
            print(f"   🔍 Barras con Close fuera de High/Low: {len(invalid_close)}")
            
            # Verificar fin de semana
            self.data['weekday'] = self.data.index.weekday
            weekend_data = self.data[self.data['weekday'] >= 5]
            print(f"   📅 Barras en fin de semana: {len(weekend_data)}")
            
            if len(invalid_hl) == 0 and len(invalid_close) == 0 and len(weekend_data) == 0:
                print(f"   ✅ Datos de alta calidad")
            else:
                print(f"   ⚠️ Problemas detectados en los datos")
                
        except Exception as e:
            print(f"❌ Error verificando calidad: {e}")
    
    def get_data(self):
        """Obtener datos cargados"""
        return self.data
    
    def filter_trading_hours(self):
        """Filtrar solo datos de horario de trading"""
        if self.data is not None:
            trading_data = self.data[(self.data.index.hour >= 9) & (self.data.index.hour <= 16)]
            print(f"📊 Datos filtrados: {len(trading_data)} barras de trading")
            return trading_data
        return None

def main():
    """Función principal para probar el cargador"""
    try:
        # Buscar archivo de datos
        data_file = None
        possible_files = [
            'MNQ_09-25_30days_1min.txt',
            'MNQ_09-25.Last',
            'MNQ_09-25.txt'
        ]
        
        for file in possible_files:
            if os.path.exists(file):
                data_file = file
                break
        
        if not data_file:
            print("❌ No se encontró archivo de datos")
            print("📁 Archivos buscados:")
            for file in possible_files:
                print(f"   - {file}")
            return False
        
        # Cargar datos
        loader = NinjaTraderDataLoader()
        if loader.load_from_txt(data_file):
            data = loader.get_data()
            
            # Filtrar horario de trading
            trading_data = loader.filter_trading_hours()
            
            if trading_data is not None and len(trading_data) > 0:
                print(f"\n✅ DATOS LISTOS PARA OPTIMIZACIÓN")
                print(f"   📊 Total de barras: {len(trading_data)}")
                print(f"   📅 Período: {trading_data.index[0]} a {trading_data.index[-1]}")
                print(f"   🎯 Los datos están listos para usar en el optimizador")
                return True
            else:
                print(f"❌ No hay datos válidos de trading")
                return False
        else:
            print(f"❌ Error cargando datos")
            return False
            
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
