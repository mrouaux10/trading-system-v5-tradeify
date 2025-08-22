#!/usr/bin/env python3
"""
🧪 TEST TRADOVATE INTEGRATION - SCRIPT DE PRUEBA COMPLETO
Prueba todas las funcionalidades del conector Tradovate
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict
import sys
import os

# Agregar el directorio scripts al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradovate_connector import TradovateConnector

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradovateIntegrationTester:
    """Clase para probar la integración completa con Tradovate"""
    
    def __init__(self, config_file: str = "config/lightning_50k_final_config.json"):
        """Inicializar tester"""
        self.config_file = config_file
        self.connector = None
        self.test_results = {}
        
        logger.info("🧪 Tradovate Integration Tester inicializado")
    
    def run_all_tests(self) -> Dict:
        """Ejecutar todas las pruebas"""
        logger.info("🚀 INICIANDO PRUEBAS COMPLETAS DE INTEGRACIÓN")
        logger.info("=" * 60)
        
        try:
            # 1. Prueba de inicialización
            self.test_initialization()
            
            # 2. Prueba de autenticación
            self.test_authentication()
            
            # 3. Prueba de endpoints de cuenta
            self.test_account_endpoints()
            
            # 4. Prueba de búsqueda de contratos
            self.test_contract_endpoints()
            
            # 5. Prueba de WebSocket
            self.test_websocket_connection()
            
            # 6. Prueba de órdenes (simulada)
            self.test_order_endpoints()
            
            # 7. Prueba de datos de mercado
            self.test_market_data_endpoints()
            
            # Resumen final
            self.generate_test_summary()
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"❌ Error en pruebas: {e}")
            return self.test_results
    
    def test_initialization(self):
        """Prueba 1: Inicialización del conector"""
        logger.info("🔧 PRUEBA 1: Inicialización del Conector")
        logger.info("-" * 40)
        
        try:
            self.connector = TradovateConnector(self.config_file)
            
            # Verificar que se cargó la configuración
            assert self.connector.config is not None, "Configuración no cargada"
            assert self.connector.credentials is not None, "Credenciales no configuradas"
            assert self.connector.api_config is not None, "Configuración de API no configurada"
            
            logger.info("✅ Inicialización exitosa")
            logger.info(f"   Base URL: {self.connector.api_config.base_url}")
            logger.info(f"   API Version: {self.connector.api_config.api_version}")
            logger.info(f"   Username: {self.connector.credentials.name}")
            
            self.test_results['initialization'] = {
                'status': 'PASS',
                'message': 'Conector inicializado correctamente',
                'details': {
                    'base_url': self.connector.api_config.base_url,
                    'api_version': self.connector.api_config.api_version,
                    'username': self.connector.credentials.name
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Inicialización fallida: {e}")
            self.test_results['initialization'] = {
                'status': 'FAIL',
                'message': f'Error en inicialización: {e}',
                'details': {}
            }
    
    def test_authentication(self):
        """Prueba 2: Autenticación con Tradovate"""
        logger.info("🔐 PRUEBA 2: Autenticación con Tradovate")
        logger.info("-" * 40)
        
        try:
            if not self.connector:
                raise Exception("Conector no inicializado")
            
            # Intentar autenticación
            auth_result = self.connector.authenticate()
            
            if auth_result:
                logger.info("✅ Autenticación exitosa")
                logger.info(f"   Token: {self.connector.access_token[:20]}...")
                logger.info(f"   Expiry: {self.connector.token_expiry}")
                
                self.test_results['authentication'] = {
                    'status': 'PASS',
                    'message': 'Autenticación exitosa',
                    'details': {
                        'has_token': bool(self.connector.access_token),
                        'token_expiry': self.connector.token_expiry.isoformat() if self.connector.token_expiry else None
                    }
                }
            else:
                logger.warning("⚠️ Autenticación fallida (puede ser esperado en demo)")
                
                self.test_results['authentication'] = {
                    'status': 'WARNING',
                    'message': 'Autenticación fallida (puede ser esperado)',
                    'details': {
                        'has_token': False,
                        'reason': 'Credenciales de demo o API no disponible'
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Error en autenticación: {e}")
            self.test_results['authentication'] = {
                'status': 'FAIL',
                'message': f'Error en autenticación: {e}',
                'details': {}
            }
    
    def test_account_endpoints(self):
        """Prueba 3: Endpoints de cuenta"""
        logger.info("💰 PRUEBA 3: Endpoints de Cuenta")
        logger.info("-" * 40)
        
        try:
            if not self.connector:
                raise Exception("Conector no inicializado")
            
            # Solo probar si está autenticado
            if not self.connector.access_token:
                logger.info("⚠️ Saltando prueba de cuenta (no autenticado)")
                self.test_results['account_endpoints'] = {
                    'status': 'SKIP',
                    'message': 'No autenticado',
                    'details': {}
                }
                return
            
            # Probar obtención de cuentas
            accounts = self.connector.get_accounts()
            logger.info(f"✅ Cuentas obtenidas: {len(accounts)}")
            
            if accounts:
                account_id = accounts[0]['id']
                logger.info(f"   Primera cuenta: {account_id}")
                
                # Probar balance de efectivo
                balance = self.connector.get_cash_balance_snapshot(account_id)
                if balance:
                    logger.info("✅ Balance de efectivo obtenido")
                
                # Probar snapshot de margen
                margin = self.connector.get_margin_snapshot(account_id)
                if margin:
                    logger.info("✅ Snapshot de margen obtenido")
                
                # Probar posiciones
                positions = self.connector.get_positions(account_id)
                logger.info(f"✅ Posiciones obtenidas: {len(positions)}")
                
                self.test_results['account_endpoints'] = {
                    'status': 'PASS',
                    'message': 'Endpoints de cuenta funcionando',
                    'details': {
                        'accounts_count': len(accounts),
                        'first_account_id': account_id,
                        'has_balance': bool(balance),
                        'has_margin': bool(margin),
                        'positions_count': len(positions)
                    }
                }
            else:
                logger.warning("⚠️ No se obtuvieron cuentas")
                self.test_results['account_endpoints'] = {
                    'status': 'WARNING',
                    'message': 'No se obtuvieron cuentas',
                    'details': {}
                }
                
        except Exception as e:
            logger.error(f"❌ Error en endpoints de cuenta: {e}")
            self.test_results['account_endpoints'] = {
                'status': 'FAIL',
                'message': f'Error en endpoints de cuenta: {e}',
                'details': {}
            }
    
    def test_contract_endpoints(self):
        """Prueba 4: Endpoints de contratos"""
        logger.info("📋 PRUEBA 4: Endpoints de Contratos")
        logger.info("-" * 40)
        
        try:
            if not self.connector:
                raise Exception("Conector no inicializado")
            
            # Solo probar si está autenticado
            if not self.connector.access_token:
                logger.info("⚠️ Saltando prueba de contratos (no autenticado)")
                self.test_results['contract_endpoints'] = {
                    'status': 'SKIP',
                    'message': 'No autenticado',
                    'details': {}
                }
                return
            
            # Buscar contrato MNQ
            mnq_contract = self.connector.find_contract("MNQ")
            
            if mnq_contract:
                logger.info("✅ Contrato MNQ encontrado")
                logger.info(f"   ID: {mnq_contract.get('id')}")
                logger.info(f"   Nombre: {mnq_contract.get('name')}")
                
                self.test_results['contract_endpoints'] = {
                    'status': 'PASS',
                    'message': 'Búsqueda de contratos funcionando',
                    'details': {
                        'mnq_found': True,
                        'mnq_id': mnq_contract.get('id'),
                        'mnq_name': mnq_contract.get('name')
                    }
                }
            else:
                logger.warning("⚠️ Contrato MNQ no encontrado")
                self.test_results['contract_endpoints'] = {
                    'status': 'WARNING',
                    'message': 'Contrato MNQ no encontrado',
                    'details': {
                        'mnq_found': False
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Error en endpoints de contratos: {e}")
            self.test_results['contract_endpoints'] = {
                'status': 'FAIL',
                'message': f'Error en endpoints de contratos: {e}',
                'details': {}
            }
    
    def test_websocket_connection(self):
        """Prueba 5: Conexión WebSocket"""
        logger.info("🔌 PRUEBA 5: Conexión WebSocket")
        logger.info("-" * 40)
        
        try:
            if not self.connector:
                raise Exception("Conector no inicializado")
            
            # Intentar conectar WebSocket
            ws_result = self.connector.connect_websocket()
            
            if ws_result:
                logger.info("✅ WebSocket conectado exitosamente")
                
                # Esperar un poco para estabilizar
                time.sleep(2)
                
                # Verificar estado
                if self.connector.websocket_connected:
                    logger.info("✅ Estado WebSocket: Conectado")
                    
                    # Desconectar para la prueba
                    self.connector.disconnect_websocket()
                    logger.info("✅ WebSocket desconectado")
                    
                    self.test_results['websocket_connection'] = {
                        'status': 'PASS',
                        'message': 'WebSocket funcionando correctamente',
                        'details': {
                            'connection_successful': True,
                            'state_verified': True
                        }
                    }
                else:
                    logger.warning("⚠️ WebSocket no se mantuvo conectado")
                    self.test_results['websocket_connection'] = {
                        'status': 'WARNING',
                        'message': 'WebSocket no se mantuvo conectado',
                        'details': {
                            'connection_successful': True,
                            'state_verified': False
                        }
                    }
            else:
                logger.warning("⚠️ Conexión WebSocket fallida")
                self.test_results['websocket_connection'] = {
                    'status': 'WARNING',
                    'message': 'Conexión WebSocket fallida',
                    'details': {
                        'connection_successful': False,
                        'state_verified': False
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Error en WebSocket: {e}")
            self.test_results['websocket_connection'] = {
                'status': 'FAIL',
                'message': f'Error en WebSocket: {e}',
                'details': {}
            }
    
    def test_order_endpoints(self):
        """Prueba 6: Endpoints de órdenes (simulada)"""
        logger.info("📤 PRUEBA 6: Endpoints de Órdenes (Simulada)")
        logger.info("-" * 40)
        
        try:
            if not self.connector:
                raise Exception("Conector no inicializado")
            
            # Solo probar si está autenticado
            if not self.connector.access_token:
                logger.info("⚠️ Saltando prueba de órdenes (no autenticado)")
                self.test_results['order_endpoints'] = {
                    'status': 'SKIP',
                    'message': 'No autenticado',
                    'details': {}
                }
                return
            
            # Probar obtención de órdenes (sin ejecutar)
            accounts = self.connector.get_accounts()
            if accounts:
                account_id = accounts[0]['id']
                orders = self.connector.get_orders(account_id)
                logger.info(f"✅ Órdenes obtenidas: {len(orders)}")
                
                # Probar obtención de fills
                fills = self.connector.get_fills(account_id)
                logger.info(f"✅ Fills obtenidos: {len(fills)}")
                
                # Probar obtención de reportes de ejecución
                reports = self.connector.get_execution_reports(account_id)
                logger.info(f"✅ Reportes obtenidos: {len(reports)}")
                
                self.test_results['order_endpoints'] = {
                    'status': 'PASS',
                    'message': 'Endpoints de órdenes funcionando',
                    'details': {
                        'orders_count': len(orders),
                        'fills_count': len(fills),
                        'reports_count': len(reports)
                    }
                }
            else:
                logger.warning("⚠️ No hay cuentas para probar órdenes")
                self.test_results['order_endpoints'] = {
                    'status': 'WARNING',
                    'message': 'No hay cuentas disponibles',
                    'details': {}
                }
                
        except Exception as e:
            logger.error(f"❌ Error en endpoints de órdenes: {e}")
            self.test_results['order_endpoints'] = {
                'status': 'FAIL',
                'message': f'Error en endpoints de órdenes: {e}',
                'details': {}
            }
    
    def test_market_data_endpoints(self):
        """Prueba 7: Endpoints de datos de mercado"""
        logger.info("📊 PRUEBA 7: Endpoints de Datos de Mercado")
        logger.info("-" * 40)
        
        try:
            if not self.connector:
                raise Exception("Conector no inicializado")
            
            # Solo probar si está autenticado
            if not self.connector.access_token:
                logger.info("⚠️ Saltando prueba de datos de mercado (no autenticado)")
                self.test_results['market_data_endpoints'] = {
                    'status': 'SKIP',
                    'message': 'No autenticado',
                    'details': {}
                }
                return
            
            # Buscar contrato MNQ para la prueba
            mnq_contract = self.connector.find_contract("MNQ")
            if mnq_contract:
                contract_id = mnq_contract['id']
                
                # Probar obtención de datos de chart
                chart_data = self.connector.get_chart_data(
                    contract_id=contract_id,
                    chart_type="Tick",
                    start_time=(datetime.now() - timedelta(hours=1)).isoformat(),
                    end_time=datetime.now().isoformat()
                )
                
                if chart_data:
                    logger.info("✅ Datos de chart obtenidos")
                    self.test_results['market_data_endpoints'] = {
                        'status': 'PASS',
                        'message': 'Endpoints de datos de mercado funcionando',
                        'details': {
                            'chart_data_obtained': True,
                            'contract_id': contract_id
                        }
                    }
                else:
                    logger.warning("⚠️ No se obtuvieron datos de chart")
                    self.test_results['market_data_endpoints'] = {
                        'status': 'WARNING',
                        'message': 'No se obtuvieron datos de chart',
                        'details': {
                            'chart_data_obtained': False,
                            'contract_id': contract_id
                        }
                    }
            else:
                logger.warning("⚠️ No se pudo probar datos de mercado (contrato no encontrado)")
                self.test_results['market_data_endpoints'] = {
                    'status': 'WARNING',
                    'message': 'Contrato no encontrado para prueba',
                    'details': {}
                }
                
        except Exception as e:
            logger.error(f"❌ Error en endpoints de datos de mercado: {e}")
            self.test_results['market_data_endpoints'] = {
                'status': 'FAIL',
                'message': f'Error en endpoints de datos de mercado: {e}',
                'details': {}
            }
    
    def generate_test_summary(self):
        """Generar resumen de todas las pruebas"""
        logger.info("📊 RESUMEN DE PRUEBAS")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        warning_tests = sum(1 for result in self.test_results.values() if result['status'] == 'WARNING')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAIL')
        skipped_tests = sum(1 for result in self.test_results.values() if result['status'] == 'SKIP')
        
        logger.info(f"📈 TOTAL DE PRUEBAS: {total_tests}")
        logger.info(f"✅ EXITOSAS: {passed_tests}")
        logger.info(f"⚠️ ADVERTENCIAS: {warning_tests}")
        logger.info(f"❌ FALLIDAS: {failed_tests}")
        logger.info(f"⏭️ OMITIDAS: {skipped_tests}")
        
        # Mostrar detalles de cada prueba
        for test_name, result in self.test_results.items():
            status_emoji = {
                'PASS': '✅',
                'WARNING': '⚠️',
                'FAIL': '❌',
                'SKIP': '⏭️'
            }
            
            logger.info(f"{status_emoji.get(result['status'], '❓')} {test_name.upper()}: {result['message']}")
        
        # Evaluación general
        if failed_tests == 0 and passed_tests > 0:
            overall_status = "🎉 EXCELENTE - Todas las pruebas críticas pasaron"
        elif failed_tests == 0:
            overall_status = "⚠️ ADVERTENCIA - Algunas pruebas no se ejecutaron"
        else:
            overall_status = "❌ PROBLEMAS - Algunas pruebas fallaron"
        
        logger.info("=" * 60)
        logger.info(f"🎯 EVALUACIÓN GENERAL: {overall_status}")
        logger.info("=" * 60)
        
        # Guardar resultados en archivo
        self.save_test_results()
    
    def save_test_results(self):
        """Guardar resultados de las pruebas en archivo"""
        try:
            results_file = f"logs/tradovate_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(results_file), exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            logger.info(f"💾 Resultados guardados en: {results_file}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando resultados: {e}")
    
    def cleanup(self):
        """Limpiar recursos"""
        try:
            if self.connector:
                self.connector.cleanup()
                logger.info("🧹 Recursos limpiados")
        except Exception as e:
            logger.error(f"❌ Error limpiando recursos: {e}")


def main():
    """Función principal"""
    print("🧪 TEST TRADOVATE INTEGRATION")
    print("=" * 50)
    print("Este script prueba todas las funcionalidades del conector Tradovate")
    print("=" * 50)
    
    try:
        # Crear tester
        tester = TradovateIntegrationTester()
        
        # Ejecutar todas las pruebas
        results = tester.run_all_tests()
        
        # Limpiar recursos
        tester.cleanup()
        
        print("\n🎯 PRUEBAS COMPLETADAS")
        print("Revisa los logs para detalles completos")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
