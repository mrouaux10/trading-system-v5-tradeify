"""
TRADOVATE CONNECTOR - CONECTOR COMPLETO PARA API DE TRADOVATE
Implementación completa basada en la documentación oficial de la API v1.0.0
"""

import json
import logging
import os
import time
import websocket
import threading
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
from dataclasses import dataclass

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class TradovateCredentials:
    """Credenciales de autenticación para Tradovate"""
    name: str
    password: str
    app_id: str = "TradeifyBot"
    app_version: str = "1.0"
    device_id: str = "TradeifyBot"
    cid: str = ""
    sec: str = ""

@dataclass
class TradovateConfig:
    """Configuración de conexión para Tradovate"""
    base_url: str = "https://live.tradovateapi.com"
    websocket_url: str = "wss://live.tradovateapi.com/ws"
    api_version: str = "v1"
    timeout: int = 30
    max_retries: int = 5
    heartbeat_interval: int = 30

class TradovateConnector:
    """
    Conector completo para la API de Tradovate
    Implementa autenticación, gestión de órdenes, datos de mercado y WebSockets
    """
    
    def __init__(self, config_file: str = None):
        """Inicializar el conector con configuración"""
        if config_file is None:
            # Ruta absoluta al archivo de configuración Lightning 50K
            config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'lightning_50k_strategy.json')
        self.config = self.load_config(config_file)
        self.credentials = self.setup_credentials()
        self.api_config = self.setup_api_config()
        
        # Estado de la conexión
        self.access_token = None
        self.token_expiry = None
        self.session = requests.Session()
        self.websocket = None
        self.websocket_connected = False
        self.websocket_thread = None
        
        # Callbacks para datos en tiempo real
        self.quote_callbacks = []
        self.dom_callbacks = []
        self.chart_callbacks = []
        
        # Cache de datos
        self.contracts_cache = {}
        self.accounts_cache = {}
        
        logger.info("Conector Tradovate inicializado")
    
    def load_config(self, config_file: str) -> Dict:
        """Cargar configuración desde archivo"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            raise
    
    def setup_credentials(self) -> TradovateCredentials:
        """Configurar credenciales de autenticación"""
        creds = self.config.get('account_credentials', {})
        return TradovateCredentials(
            name=creds.get('username', ''),
            password=creds.get('password', ''),
            app_id=creds.get('app_id', 'TradeifyBot'),
            app_version=creds.get('app_version', '1.0'),
            device_id=creds.get('device_id', 'TradeifyBot'),
            cid=creds.get('cid', creds.get('username', '')),
            sec=creds.get('sec', '')
        )
    
    def setup_api_config(self) -> TradovateConfig:
        """Configurar parámetros de la API"""
        api_config = self.config.get('api_connection', {})
        return TradovateConfig(
            base_url=api_config.get('base_url', 'https://live.tradovateapi.com'),
            websocket_url=api_config.get('websocket_url', 'wss://live.tradovateapi.com/ws'),
            api_version=api_config.get('api_version', 'v1'),
            timeout=api_config.get('timeout', 30),
            max_retries=api_config.get('max_retries', 5)
        )
    
    def get_api_url(self, endpoint: str) -> str:
        """Construir URL completa para endpoint de la API"""
        return f"{self.api_config.base_url}/{self.api_config.api_version}/{endpoint}"
    
    def authenticate(self) -> bool:
        """
        Autenticarse con la API de Tradovate usando el endpoint correcto
        Endpoint: /auth/accesstokenrequest
        """
        try:
            auth_url = self.get_api_url("auth/accesstokenrequest")
            
            auth_data = {
                "name": self.credentials.name,
                "password": self.credentials.password,
                "appId": self.credentials.app_id,
                "appVersion": self.credentials.app_version,
                "deviceId": self.credentials.device_id,
                "cid": self.credentials.cid,
                "sec": self.credentials.sec
            }
            
            logger.info(f"Autenticando con Tradovate: {self.credentials.name}")
            
            response = self.session.post(
                auth_url, 
                json=auth_data, 
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                
                if 'accessToken' in auth_response:
                    self.access_token = auth_response['accessToken']
                    self.token_expiry = datetime.now() + timedelta(hours=24)
                    
                    # Configurar headers para futuras requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    })
                    
                    logger.info("Autenticación exitosa con Tradovate")
                    return True
                else:
                    logger.error(f"Respuesta de autenticación inválida: {auth_response}")
                    return False
            else:
                logger.error(f"Error de autenticación: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error durante autenticación: {e}")
            return False
    
    def renew_access_token(self) -> bool:
        """
        Renovar el token de acceso
        Endpoint: /auth/renewAccessToken
        """
        try:
            if not self.access_token:
                logger.warning("No hay token para renovar")
                return False
            
            renew_url = self.get_api_url("auth/renewAccessToken")
            renew_data = {"accessToken": self.access_token}
            
            response = self.session.post(
                renew_url,
                json=renew_data,
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                renew_response = response.json()
                if 'accessToken' in renew_response:
                    self.access_token = renew_response['accessToken']
                    self.token_expiry = datetime.now() + timedelta(hours=24)
                    
                    # Actualizar headers
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    
                    logger.info("Token de acceso renovado")
                    return True
                else:
                    logger.error("Respuesta de renovación inválida")
                    return False
            else:
                logger.error(f"Error renovando token: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error renovando token: {e}")
            return False
    
    def check_token_validity(self) -> bool:
        """Verificar si el token actual es válido"""
        if not self.access_token or not self.token_expiry:
            return False
        
        # Renovar si expira en menos de 1 hora
        if datetime.now() + timedelta(hours=1) >= self.token_expiry:
            logger.info("Token próximo a expirar, renovando...")
            return self.renew_access_token()
        
        return True
    
    def get_accounts(self) -> List[Dict]:
        """
        Obtener lista de cuentas del usuario
        Endpoint: /account/list
        """
        try:
            if not self.check_token_validity():
                if not self.authenticate():
                    return []
            
            accounts_url = self.get_api_url("account/list")
            response = self.session.get(accounts_url, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                accounts = response.json()
                self.accounts_cache = {acc['id']: acc for acc in accounts}
                logger.info(f"Obtenidas {len(accounts)} cuentas")
                return accounts
            else:
                logger.error(f"Error obteniendo cuentas: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo cuentas: {e}")
            return []
    
    def get_cash_balance_snapshot(self, account_id: int) -> Optional[Dict]:
        """
        Obtener snapshot del balance de efectivo
        Endpoint: /cashBalance/getCashBalanceSnapshot
        """
        try:
            if not self.check_token_validity():
                return None
            
            balance_url = self.get_api_url("cashBalance/getCashBalanceSnapshot")
            params = {"accountId": account_id}
            
            response = self.session.get(balance_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                balance = response.json()
                logger.info(f"Balance obtenido para cuenta {account_id}")
                return balance
            else:
                logger.error(f"Error obteniendo balance: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo balance: {e}")
            return None
    
    def get_margin_snapshot(self, account_id: int) -> Optional[Dict]:
        """
        Obtener snapshot del margen
        Endpoint: /marginSnapshot/list
        """
        try:
            if not self.check_token_validity():
                return None
            
            margin_url = self.get_api_url("marginSnapshot/list")
            params = {"accountId": account_id}
            
            response = self.session.get(margin_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                margin = response.json()
                logger.info(f"Margen obtenido para cuenta {account_id}")
                return margin
            else:
                logger.error(f"Error obteniendo margen: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo margen: {e}")
            return None
    
    def get_positions(self, account_id: int) -> List[Dict]:
        """
        Obtener posiciones actuales
        Endpoint: /position/list
        """
        try:
            if not self.check_token_validity():
                return []
            
            positions_url = self.get_api_url("position/list")
            params = {"accountId": account_id}
            
            response = self.session.get(positions_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                positions = response.json()
                logger.info(f"Obtenidas {len(positions)} posiciones")
                return positions
            else:
                logger.error(f"Error obteniendo posiciones: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []
    
    def find_contract(self, contract_name: str) -> Optional[Dict]:
        """
        Buscar contrato por nombre
        Endpoint: /contract/find
        """
        try:
            if not self.check_token_validity():
                return None
            
            contract_url = self.get_api_url("contract/find")
            params = {"name": contract_name}
            
            response = self.session.get(contract_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                contract = response.json()
                if contract:
                    self.contracts_cache[contract['id']] = contract
                    logger.info(f"Contrato encontrado: {contract_name}")
                    return contract
                else:
                    logger.warning(f"Contrato no encontrado: {contract_name}")
                    return None
            else:
                logger.error(f"Error buscando contrato: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error buscando contrato: {e}")
            return None
    
    def place_order(self, order_data: Dict) -> Optional[Dict]:
        """
        Colocar orden de trading
        Endpoint: /order/placeorder
        IMPORTANTE: Incluir isAutomated: true para órdenes del bot
        """
        try:
            if not self.check_token_validity():
                return None
            
            # Asegurar que la orden esté marcada como automatizada
            order_data['isAutomated'] = True
            
            order_url = self.get_api_url("order/placeorder")
            
            logger.info(f"Placing: Colocando orden: {order_data}")
            
            response = self.session.post(
                order_url,
                json=order_data,
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                order_response = response.json()
                logger.info(f"Orden colocada exitosamente: {order_response}")
                return order_response
            else:
                logger.error(f"Error colocando orden: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error colocando orden: {e}")
            return None
    
    def cancel_order(self, order_id: int) -> bool:
        """
        Cancelar orden
        Endpoint: /order/cancelorder
        """
        try:
            if not self.check_token_validity():
                return False
            
            cancel_url = self.get_api_url("order/cancelorder")
            cancel_data = {"orderId": order_id}
            
            response = self.session.post(
                cancel_url,
                json=cancel_data,
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Orden {order_id} cancelada")
                return True
            else:
                logger.error(f"Error cancelando orden: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False
    
    def modify_order(self, order_id: int, modifications: Dict) -> bool:
        """
        Modificar orden existente
        Endpoint: /order/modifyorder
        """
        try:
            if not self.check_token_validity():
                return False
            
            modify_url = self.get_api_url("order/modifyorder")
            modify_data = {
                "orderId": order_id,
                **modifications
            }
            
            response = self.session.post(
                modify_url,
                json=modify_data,
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Orden {order_id} modificada")
                return True
            else:
                logger.error(f"Error modificando orden: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error modificando orden: {e}")
            return False
    
    def liquidate_position(self, position_id: int) -> bool:
        """
        Liquidar posición
        Endpoint: /order/liquidateposition
        """
        try:
            if not self.check_token_validity():
                return False
            
            liquidate_url = self.get_api_url("order/liquidateposition")
            liquidate_data = {"positionId": position_id}
            
            response = self.session.post(
                liquidate_url,
                json=liquidate_data,
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Posición {position_id} liquidada")
                return True
            else:
                logger.error(f"Error liquidando posición: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error liquidando posición: {e}")
            return False
    
    def get_orders(self, account_id: int) -> List[Dict]:
        """
        Obtener lista de órdenes
        Endpoint: /order/list
        """
        try:
            if not self.check_token_validity():
                return []
            
            orders_url = self.get_api_url("order/list")
            params = {"accountId": account_id}
            
            response = self.session.get(orders_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                orders = response.json()
                logger.info(f"Obtenidas {len(orders)} órdenes")
                return orders
            else:
                logger.error(f"Error obteniendo órdenes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo órdenes: {e}")
            return []
    
    def get_execution_reports(self, account_id: int) -> List[Dict]:
        """
        Obtener reportes de ejecución
        Endpoint: /executionReport/list
        """
        try:
            if not self.check_token_validity():
                return []
            
            reports_url = self.get_api_url("executionReport/list")
            params = {"accountId": account_id}
            
            response = self.session.get(reports_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                reports = response.json()
                logger.info(f"Obtenidos {len(reports)} reportes de ejecución")
                return reports
            else:
                logger.error(f"Error obteniendo reportes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo reportes: {e}")
            return []
    
    def get_fills(self, account_id: int) -> List[Dict]:
        """
        Obtener fills (ejecuciones)
        Endpoint: /fill/list
        """
        try:
            if not self.check_token_validity():
                return []
            
            fills_url = self.get_api_url("fill/list")
            params = {"accountId": account_id}
            
            response = self.session.get(fills_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                fills = response.json()
                logger.info(f"Obtenidos {len(fills)} fills")
                return fills
            else:
                logger.error(f"Error obteniendo fills: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo fills: {e}")
            return []
    
    def get_account_risk_status(self, account_id: int) -> Optional[Dict]:
        """
        Obtener estado de riesgo de la cuenta
        Endpoint: /accountRiskStatus/list
        """
        try:
            if not self.check_token_validity():
                return None
            
            risk_url = self.get_api_url("accountRiskStatus/list")
            params = {"accountId": account_id}
            
            response = self.session.get(risk_url, params=params, timeout=self.api_config.timeout)
            
            if response.status_code == 200:
                risk_status = response.json()
                if risk_status:
                    logger.info(f"Estado de riesgo obtenido para cuenta {account_id}")
                    return risk_status[0]  # Retornar el primero
                else:
                    logger.warning(f"No hay estado de riesgo para cuenta {account_id}")
                    return None
            else:
                logger.error(f"Error obteniendo estado de riesgo: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de riesgo: {e}")
            return None
    
    def get_chart_data(self, contract_id: int, chart_type: str = "Tick", 
                       start_time: str = None, end_time: str = None) -> Optional[Dict]:
        """
        Obtener datos de chart
        Endpoint: /md/getChart
        """
        try:
            if not self.check_token_validity():
                return None
            
            chart_url = self.get_api_url("md/getChart")
            chart_data = {
                "symbol": str(contract_id),
                "underlyingType": chart_type,
                "startTime": start_time or (datetime.now() - timedelta(days=1)).isoformat(),
                "endTime": end_time or datetime.now().isoformat()
            }
            
            response = self.session.post(
                chart_url,
                json=chart_data,
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                chart_data = response.json()
                logger.info(f"Datos de chart obtenidos para contrato {contract_id}")
                return chart_data
            else:
                logger.error(f"Error obteniendo chart: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo chart: {e}")
            return None
    
    def connect_websocket(self) -> bool:
        """Conectar al WebSocket de Tradovate para datos en tiempo real"""
        try:
            if self.websocket_connected:
                logger.info("WebSocket ya conectado")
                return True
            
            # Crear conexión WebSocket
            self.websocket = websocket.WebSocketApp(
                self.api_config.websocket_url,
                on_open=self.on_websocket_open,
                on_message=self.on_websocket_message,
                on_error=self.on_websocket_error,
                on_close=self.on_websocket_close
            )
            
            # Iniciar WebSocket en thread separado
            self.websocket_thread = threading.Thread(target=self.websocket.run_forever)
            self.websocket_thread.daemon = True
            self.websocket_thread.start()
            
            # Esperar conexión
            timeout = 10
            start_time = time.time()
            while not self.websocket_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.websocket_connected:
                logger.info("WebSocket conectado exitosamente")
                return True
            else:
                logger.error("Timeout conectando WebSocket")
                return False
                
        except Exception as e:
            logger.error(f"Error conectando WebSocket: {e}")
            return False
    
    def on_websocket_open(self, ws):
        """Callback cuando se abre la conexión WebSocket"""
        logger.info("Conexión WebSocket abierta")
        self.websocket_connected = True
        
        # Enviar heartbeat inicial
        self.send_websocket_heartbeat()
    
    def on_websocket_message(self, ws, message):
        """Callback cuando se recibe mensaje del WebSocket"""
        try:
            data = json.loads(message)
            self.process_websocket_message(data)
        except json.JSONDecodeError:
            logger.warning(f"Mensaje WebSocket no válido: {message}")
        except Exception as e:
            logger.error(f"Error procesando mensaje WebSocket: {e}")
    
    def on_websocket_error(self, ws, error):
        """Callback cuando hay error en WebSocket"""
        logger.error(f"Error en WebSocket: {error}")
        self.websocket_connected = False
    
    def on_websocket_close(self, ws, close_status_code, close_msg):
        """Callback cuando se cierra la conexión WebSocket"""
        logger.info("Conexión WebSocket cerrada")
        self.websocket_connected = False
    
    def send_websocket_heartbeat(self):
        """Enviar heartbeat al WebSocket"""
        if self.websocket and self.websocket_connected:
            try:
                self.websocket.send("[]")
            except Exception as e:
                logger.error(f"Error enviando heartbeat: {e}")
    
    def process_websocket_message(self, message: Dict):
        """Procesar mensaje recibido del WebSocket"""
        try:
            # Procesar diferentes tipos de mensajes
            if 'md' in message:
                self.process_market_data(message['md'])
            elif 'chart' in message:
                self.process_chart_data(message['chart'])
            elif 'clock' in message:
                self.process_clock_message(message['clock'])
            elif 'props' in message:
                self.process_props_message(message['props'])
            else:
                logger.debug(f"Message: Mensaje WebSocket no procesado: {message}")
                
        except Exception as e:
            logger.error(f"Error procesando mensaje WebSocket: {e}")
    
    def process_market_data(self, market_data: Dict):
        """Procesar datos de mercado del WebSocket"""
        try:
            # Procesar quotes
            if 'quotes' in market_data:
                for quote in market_data['quotes']:
                    for callback in self.quote_callbacks:
                        callback(quote)
            
            # Procesar DOM
            if 'dom' in market_data:
                for dom in market_data['dom']:
                    for callback in self.quote_callbacks:
                        callback(dom)
                        
        except Exception as e:
            logger.error(f"Error procesando datos de mercado: {e}")
    
    def process_chart_data(self, chart_data: Dict):
        """Procesar datos de chart del WebSocket"""
        try:
            for callback in self.chart_callbacks:
                callback(chart_data)
        except Exception as e:
            logger.error(f"Error procesando datos de chart: {e}")
    
    def process_clock_message(self, clock_data: Dict):
        """Procesar mensaje de reloj del WebSocket"""
        try:
            logger.debug(f"🕐 Mensaje de reloj: {clock_data}")
        except Exception as e:
            logger.error(f"Error procesando mensaje de reloj: {e}")
    
    def process_props_message(self, props_data: Dict):
        """Procesar mensaje de propiedades del WebSocket"""
        try:
            logger.debug(f"Config: Mensaje de propiedades: {props_data}")
        except Exception as e:
            logger.error(f"Error procesando mensaje de propiedades: {e}")
    
    def subscribe_quote(self, symbol: str, callback: callable):
        """Suscribirse a quotes en tiempo real"""
        try:
            if not self.websocket_connected:
                if not self.connect_websocket():
                    return False
            
            # Agregar callback
            self.quote_callbacks.append(callback)
            
            # Enviar suscripción
            subscription_request = f"md/subscribeQuote\n0\n{{\"symbol\":\"{symbol}\"}}\n"
            self.websocket.send(subscription_request)
            
            logger.info(f"Suscrito a quotes para {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a quotes: {e}")
            return False
    
    def subscribe_dom(self, symbol: str, callback: callable):
        """Suscribirse a Depth of Market en tiempo real"""
        try:
            if not self.websocket_connected:
                if not self.connect_websocket():
                    return False
            
            # Agregar callback
            self.dom_callbacks.append(callback)
            
            # Enviar suscripción
            subscription_request = f"md/subscribeDOM\n0\n{{\"symbol\":\"{symbol}\"}}\n"
            self.websocket.send(subscription_request)
            
            logger.info(f"Suscrito a DOM para {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a DOM: {e}")
            return False
    
    def subscribe_chart(self, symbol: str, callback: callable):
        """Suscribirse a datos de chart en tiempo real"""
        try:
            if not self.websocket_connected:
                if not self.connect_websocket():
                    return False
            
            # Agregar callback
            self.chart_callbacks.append(callback)
            
            # Enviar suscripción
            subscription_request = f"md/subscribeChart\n0\n{{\"symbol\":\"{symbol}\"}}\n"
            self.websocket.send(subscription_request)
            
            logger.info(f"Suscrito a chart para {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a chart: {e}")
            return False
    
    def disconnect_websocket(self):
        """Desconectar WebSocket"""
        try:
            if self.websocket:
                self.websocket.close()
                self.websocket_connected = False
                logger.info("WebSocket desconectado")
        except Exception as e:
            logger.error(f"Error desconectando WebSocket: {e}")
    
    def get_account_summary(self, account_id: int) -> Dict:
        """Obtener resumen completo de la cuenta"""
        try:
            summary = {
                'account_info': None,
                'cash_balance': None,
                'margin_snapshot': None,
                'positions': [],
                'orders': [],
                'risk_status': None
            }
            
            # Obtener información de la cuenta
            accounts = self.get_accounts()
            if accounts:
                summary['account_info'] = next((acc for acc in accounts if acc['id'] == account_id), None)
            
            # Obtener balance de efectivo
            summary['cash_balance'] = self.get_cash_balance_snapshot(account_id)
            
            # Obtener snapshot de margen
            summary['margin_snapshot'] = self.get_margin_snapshot(account_id)
            
            # Obtener posiciones
            summary['positions'] = self.get_positions(account_id)
            
            # Obtener órdenes
            summary['orders'] = self.get_orders(account_id)
            
            # Obtener estado de riesgo
            summary['risk_status'] = self.get_account_risk_status(account_id)
            
            logger.info(f"Resumen de cuenta {account_id} obtenido")
            return summary
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de cuenta: {e}")
            return {}
    
    def create_mnq_order(self, side: str, quantity: int, price: float = None, 
                         order_type: str = "Market") -> Optional[Dict]:
        """
        Crear orden específica para MNQ (Micro E-mini NASDAQ-100)
        
        Args:
            side: "Buy" o "Sell"
            quantity: Cantidad de contratos
            price: Precio (opcional para órdenes de mercado)
            order_type: Tipo de orden ("Market", "Limit", "Stop", etc.)
        """
        try:
            # Buscar contrato MNQ
            contract = self.find_contract("MNQ")
            if not contract:
                logger.error("Contrato MNQ no encontrado")
                return None
            
            # Obtener primera cuenta
            accounts = self.get_accounts()
            if not accounts:
                logger.error("No hay cuentas disponibles")
                return None
            
            account_id = accounts[0]['id']
            
            # Crear datos de la orden
            order_data = {
                "accountId": account_id,
                "symbol": contract['name'],
                "price": price,
                "quantity": quantity,
                "side": side,
                "orderType": order_type,
                "isAutomated": True,  # CRÍTICO: Marcar como automatizada
                "timeInForce": "Day"
            }
            
            # Colocar orden
            return self.place_order(order_data)
            
        except Exception as e:
            logger.error(f"Error creando orden MNQ: {e}")
            return None
    
    def get_trading_status(self) -> Dict:
        """Obtener estado general del trading"""
        try:
            status = {
                'authenticated': bool(self.access_token),
                'token_valid': self.check_token_validity(),
                'websocket_connected': self.websocket_connected,
                'accounts_available': len(self.accounts_cache) > 0,
                'last_update': datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de trading: {e}")
            return {}
    
    def cleanup(self):
        """Limpiar recursos del conector"""
        try:
            # Desconectar WebSocket
            self.disconnect_websocket()
            
            # Cerrar sesión HTTP
            if self.session:
                self.session.close()
            
            logger.info("Recursos del conector limpiados")
            
        except Exception as e:
            logger.error(f"Error limpiando recursos: {e}")
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        self.cleanup()


# Funciones de demostración para testing
def demo_authentication():
    """Demostrar autenticación"""
    try:
        connector = TradovateConnector()
        if connector.authenticate():
            print("Autenticación exitosa")
            print(f"Token: {connector.access_token[:20]}...")
        else:
            print("Autenticación fallida")
    except Exception as e:
        print(f"Error en demo: {e}")

def demo_account_info():
    """Demostrar obtención de información de cuenta"""
    try:
        connector = TradovateConnector()
        if connector.authenticate():
            accounts = connector.get_accounts()
            if accounts:
                account_id = accounts[0]['id']
                summary = connector.get_account_summary(account_id)
                print(f"Resumen de cuenta obtenido: {len(summary)} elementos")
                print(f"Posiciones: {len(summary['positions'])}")
                print(f"Órdenes: {len(summary['orders'])}")
            else:
                print("No se pudieron obtener cuentas")
        else:
            print("Autenticación fallida")
    except Exception as e:
        print(f"Error en demo: {e}")

def demo_contract_search():
    """Demostrar búsqueda de contratos"""
    try:
        connector = TradovateConnector()
        if connector.authenticate():
            contract = connector.find_contract("MNQ")
            if contract:
                print(f"Contrato encontrado: {contract}")
            else:
                print("Contrato no encontrado")
        else:
            print("Autenticación fallida")
    except Exception as e:
        print(f"Error en demo: {e}")

if __name__ == "__main__":
    # Ejecutar demos
    print("DEMO TRADOVATE CONNECTOR")
    print("=" * 50)
    
    demo_authentication()
    print()
    
    demo_account_info()
    print()
    
    demo_contract_search()
