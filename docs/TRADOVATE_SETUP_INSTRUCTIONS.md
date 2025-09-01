# INSTRUCCIONES TRADOVATE API - PASO A PASO

## 🎯 OBJETIVO
Descargar datos históricos MNQ directamente de Tradovate y re-ejecutar Lightning 50K COMPLIANCE

## 📋 PASOS DETALLADOS

### PASO 1: CUENTA TRADOVATE
1. Ir a: https://tradovate.com
2. Crear cuenta DEMO (gratis)
3. Anotar username y password
4. Activar API access en configuración

### PASO 2: CREDENCIALES API
1. Login en plataforma Tradovate
2. Ir a: Account Settings → API Access
3. Crear nueva aplicación:
   - Name: "TradeifyBot"
   - Description: "Lightning 50K Strategy"
4. Anotar App ID generado

### PASO 3: CONFIGURAR CÓDIGO
1. Abrir: tradovate_configs/tradovate_config.json
2. Llenar credenciales:
   ```json
   {
     "tradovate_credentials": {
       "username": "tu_username_real",
       "password": "tu_password_real",
       "app_id": "app_id_generado"
     }
   }
   ```

### PASO 4: DESCARGAR DATOS
```bash
cd "My trading system/scripts"
python3 tradovate_connector.py --download-historical
```

### PASO 5: CONVERTIR FORMATO
```bash
cd "My trading system/tradovate_data"
python3 convert_tradovate_data.py
```

### PASO 6: RE-BACKTEST
```bash
cd "My trading system/backtesting"
python3 lightning_50k_COMPLIANCE.py --data-source tradovate
```

## ⏰ TIEMPO ESTIMADO
- Paso 1-3: 15 minutos
- Paso 4: 30 minutos (descarga)
- Paso 5-6: 10 minutos

## 🎯 RESULTADO ESPERADO
- Archivo: MNQ_consolidated_2024-2025_TRADOVATE.csv
- Backtest con datos 100% compatibles
- ROI esperado: 45%-65% (similar a actual)
- Drawdown: <$2,000 (compliance)

## ⚠️ TROUBLESHOOTING
- Error autenticación → Verificar credenciales
- Error descarga → Verificar conexión internet
- Datos incompletos → Re-ejecutar descarga

## 📞 SOPORTE
Si hay problemas, proporcionar:
1. Logs de error completos
2. Archivo de configuración (sin passwords)
3. Descripción del paso donde falló
