#!/usr/bin/env python3
"""
Conector de API Tradovate
=========================

Este script maneja la conexión real a Tradovate para:
- Autenticación con credenciales reales
- Obtención de datos de mercado en tiempo real
- Ejecución de trades reales
- Monitoreo de posiciones y órdenes
"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradovateConnector:
    """Conector principal a la API de Tradovate"""
    
    def __init__(self, config_file: str = "config/tradeify_real_config.json"):
        """Inicializar conector"""
        self.config = self.load_config(config_file)
        self.session = requests.Session()
        self.is_connected = False
        self.access_token = None
        self.account_info = None
        
        # Configurar headers por defecto
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TradeifyBot/1.0'
        })
        
        logger.info("TradovateConnector inicializado")
    
    def load_config(self, config_file: str) -> dict:
        """Cargar configuración de Tradeify (que incluye credenciales de Tradovate)"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_file}")
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Verificar credenciales de Tradovate
            credentials = config['account_credentials']
            if not credentials.get('username') or credentials.get('username') == "TU_USERNAME_AQUI":
                raise ValueError("Username de Tradovate no configurado")
            if not credentials.get('password') or credentials.get('password') == "TU_PASSWORD_AQUI":
                raise ValueError("Password de Tradovate no configurado")
            
            logger.info("Configuración de Tradovate cargada")
            return config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            raise
    
    def authenticate(self) -> bool:
        """Autenticar con Tradovate usando credenciales reales"""
        try:
            logger.info("🔐 Autenticando con Tradovate...")
            
            # Obtener credenciales
            username = self.config['account_credentials']['username']
            password = self.config['account_credentials']['password']
            
            # Endpoint de autenticación de Tradovate
            auth_url = "https://live.tradovate.com/v1/auth/access_token"
            
            # Datos de autenticación
            auth_data = {
                "name": username,
                "password": password,
                "appId": "Sample App",
                "appVersion": "1.0",
                "deviceId": "TradeifyBot",
                "cid": username
            }
            
            response = self.session.post(
                auth_url,
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                
                if 'accessToken' in auth_response:
                    self.access_token = auth_response['accessToken']
                    
                    # Actualizar headers con token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    
                    self.is_connected = True
                    logger.info("✅ Autenticación exitosa con Tradovate")
                    return True
                else:
                    logger.error("❌ Respuesta de autenticación sin accessToken")
                    return False
            else:
                logger.error(f"❌ Error de autenticación: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error durante autenticación: {e}")
            return False
    
    def get_account_info(self) -> Optional[Dict]:
        """Obtener información de la cuenta de Tradovate"""
        try:
            if not self.is_connected:
                logger.warning("No hay conexión activa. Autenticando...")
                if not self.authenticate():
                    return None
            
            # Endpoint de información de cuenta
            account_url = "https://live.tradovate.com/v1/account/list"
            response = self.session.get(account_url)
            
            if response.status_code == 200:
                accounts = response.json()
                if accounts and len(accounts) > 0:
                    # Usar la primera cuenta disponible
                    self.account_info = accounts[0]
                    logger.info(f"✅ Información de cuenta obtenida: {self.account_info.get('name', 'N/A')}")
                    logger.info(f"   Account ID: {self.account_info.get('accountId', 'N/A')}")
                    return self.account_info
                else:
                    logger.error("❌ No se encontraron cuentas en Tradovate")
                    return None
            else:
                logger.error(f"❌ Error obteniendo información de cuenta: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo información de cuenta: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Probar conexión completa a Tradovate"""
        try:
            logger.info("🔍 Probando conexión a Tradovate...")
            
            # Paso 1: Autenticación
            if not self.authenticate():
                logger.error("❌ Fallo en autenticación")
                return False
            
            # Paso 2: Información de cuenta
            account_info = self.get_account_info()
            if not account_info:
                logger.error("❌ Fallo obteniendo información de cuenta")
                return False
            
            logger.info("✅ Conexión a Tradovate probada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de Tradovate"""
        try:
            self.session.close()
            self.is_connected = False
            self.access_token = None
            logger.info("✅ Desconectado de Tradovate")
            
        except Exception as e:
            logger.error(f"❌ Error desconectando: {e}")

# Función de prueba
def test_tradovate_connection():
    """Función de prueba para el conector"""
    try:
        connector = TradovateConnector()
        
        print("🔍 Probando conexión a Tradovate...")
        if connector.test_connection():
            print("✅ Conexión exitosa!")
            
            # Mostrar información de cuenta
            if connector.account_info:
                print(f"📊 Cuenta: {connector.account_info.get('name', 'N/A')}")
                print(f"🆔 Account ID: {connector.account_info.get('accountId', 'N/A')}")
                print(f"💰 Tipo: {connector.account_info.get('accountType', 'N/A')}")
            
        else:
            print("❌ Fallo en la conexión")
        
        connector.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_tradovate_connection()
