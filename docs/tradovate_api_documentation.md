# **TRADOVATE API - DOCUMENTACIÓN COMPLETA**

**Estado:** **REQUIERE CORRECCIONES CRÍTICAS POR VALIDACIÓN TRADEIFY**  
**Versión:** API v1.0.0  
**Propósito:** Documentación completa para integración del bot de trading  
**Última actualización:** 21 de agosto de 2025  

## **VALIDACIÓN CRÍTICA POR IA TRADEIFY - AGOSTO 2025**

**IMPORTANTE:** Esta documentación fue validada por IA oficial de Tradeify y se encontraron **ERRORES CRÍTICOS**:

### **CONFIRMACIONES CORRECTAS:**
- Autenticación y tokens
- Estructura de la API  
- WebSockets
- Requisitos API Access ($25/mes + $1,000 mínimo)
- Bot trading permitido con propiedad exclusiva

### **ERRORES CRÍTICOS IDENTIFICADOS:**
1. **🔴 Plataformas soportadas:** Tradeify soporta **Tradovate, TradingView Y NinjaTrader** (no solo Tradovate)
2. **🔴 Instrumentos disponibles:** Hay muchos más: **ES, NQ, YM, RTY, productos agrícolas, divisas, contratos EUREX**
3. **🔴 Verificación de propiedad:** Debes **probar propiedad exclusiva + proporcionar video en vivo** del bot funcionando
4. **🔴 Restricciones HFT:** **Bots HFT prohibidos**, trades de **menos de 5 segundos son monitoreados**

### **INFORMACIÓN NO VERIFICABLE:**
- **Detalles técnicos específicos** de endpoints requieren verificación para cuentas Tradeify
- Muchos detalles parecen ser de **documentación general Tradovate**, no específicos para Tradeify

**ACCIÓN REQUERIDA:** Verificar todos los endpoints y parámetros específicamente para cuentas Tradeify antes de implementar

---

## **ÍNDICE DE CONTENIDO**

### **AUTENTICACIÓN Y SESIÓN**
- [x] Endpoints de autenticación
- [x] Gestión de tokens
- [x] Renovación de sesiones
- [x] Two-Factor Authentication
- [x] OAuth flow
- [x] Gestión de sesiones concurrentes

### **GESTIÓN DE CUENTA**
- [x] Información de cuenta
- [x] Saldos y balances
- [x] Margen disponible
- [x] P&L en tiempo real
- [x] Datos de usuario

### **DATOS DE MERCADO**
- [x] Precios en tiempo real
- [x] Histórico de precios
- [x] Volumen y liquidez
- [x] Indicadores técnicos
- [x] Market Data API
- [x] Quotes y DOM
- [x] Histogramas
- [x] Charts y Tick Charts

### **GESTIÓN DE ÓRDENES**
- [x] Colocar órdenes
- [x] Modificar órdenes
- [x] Cancelar órdenes
- [x] Tipos de órdenes

### **GESTIÓN DE POSICIONES**
- [x] Estado de posiciones
- [x] Abrir posiciones
- [x] Cerrar posiciones
- [x] Modificar posiciones

### **WEBSOCKETS Y STREAMING**
- [x] Conexiones en tiempo real
- [x] Suscripciones a datos
- [x] Manejo de eventos
- [x] Protocolo WebSocket
- [x] Server Frames
- [x] Client Requests
- [x] Heartbeats

### **MANEJO DE ERRORES**
- [x] Códigos de error
- [x] Mensajes de error
- [x] Estrategias de retry
- [x] Rate limits

### **🏗️ ESTRUCTURA DE LA API**
- [x] Operaciones de consulta (GET)
- [x] Operaciones de envío (POST)
- [x] Convenciones de nomenclatura
- [x] Batch loading
- [x] Dependencias master-detail

### **🎮 MARKET REPLAY**
- [x] Servicio de replay
- [x] Inicialización de sesión
- [x] Control de velocidad
- [x] Sincronización de reloj

### **CONTRACT LIBRARY**
- [x] Contratos y vencimientos
- [x] Búsqueda por nombre
- [x] Dependencias de contratos
- [x] Roll contracts
- [x] Contract groups
- [x] Product sessions
- [x] Spread definitions

### **ORDERS Y FILL MANAGEMENT**
- [x] Command endpoints
- [x] Execution reports
- [x] Fill management
- [x] Order strategies
- [x] Position management

### **ACCOUNTING Y GESTIÓN DE CUENTA**
- [x] Account management
- [x] Cash balance
- [x] Margin snapshots
- [x] Trading permissions

### **GESTIÓN DE RIESGO**
- [x] Account risk status
- [x] Position limits
- [x] Auto-liquidation
- [x] Risk parameters

### **💳 FEES Y SUBSCRIPTIONS**
- [x] Market data subscriptions
- [x] Subscription plans
- [x] Exchange scopes

### **🔔 ALERTS Y CONFIGURACIÓN**
- [x] Alert management
- [x] Configuration endpoints
- [x] Clearing house
- [x] Entitlements

### **👤 GESTIÓN DE USUARIOS**
- [x] User management
- [x] Contact info
- [x] Organizations
- [x] Sessions

### **💬 CHAT Y COMUNICACIÓN**
- [x] Chat management
- [x] Message handling

---

## **ENDPOINTS CRÍTICOS PARA EL BOT**

### **PRIORIDAD ALTA (Implementación inmediata):**
1. **Autenticación** - Login y tokens OK
2. **Saldos** - Ver balance de cuenta OK
3. **Órdenes** - Comprar/vender MNQ OK
4. **Posiciones** - Estado actual OK

### **PRIORIDAD MEDIA (Implementación posterior):**
1. **Datos en tiempo real** - Websockets OK
2. **Histórico** - Backtesting OK
3. **Gestión avanzada** - Órdenes complejas

---

## 📝 **NOTAS DE IMPLEMENTACIÓN**

### **Integración con código actual:**
- **Archivo:** `scripts/tradovate_connector.py`
- **Clase:** `TradovateConnector`
- **Métodos:** `authenticate()`, `get_balance()`, `place_order()`

### **Estrategia Lightning 50K:**
- **Instrumento:** MNQ (Micro E-mini NASDAQ) - **NOTA:** Tradeify soporta muchos más instrumentos
- **Instrumentos disponibles:** ES, NQ, YM, RTY, productos agrícolas, divisas, contratos EUREX
- **Contratos:** 1 (conservador)
- **Stop Loss:** $50
- **Take Profit:** $150

---

## **CONTENIDO DE LA API**

### **AUTENTICACIÓN Y ACCESO COMPLETO:**

#### **Requisitos Previos:**
- Cuenta LIVE con más de $1,000 en equity
- Suscripción a API Access
- API Key generada (cid y sec)
- 🔴 **CRÍTICO:** Probar propiedad exclusiva del código
- 🔴 **CRÍTICO:** Proporcionar video en vivo del bot funcionando en tu PC
- 🔴 **RESTRICCIÓN:** Bots HFT prohibidos (trades <5 segundos monitoreados)

#### **Endpoints de Autenticación:**

##### **1. Request Access Token:**
```
POST /v1/auth/accessTokenRequest
```

**Parámetros de Autenticación:**
```json
{
    "name": "username",
    "password": "password",
    "appId": "Sample App",
    "appVersion": "1.0",
    "cid": "client_id_from_tradovate",
    "sec": "secret_key_from_tradovate",
    "deviceId": "unique_device_identifier"
}
```

**Esquema de Request Body:**
```json
{
    "name": "string <= 64 characters (required)",
    "password": "string <= 64 characters (required)",
    "appId": "string <= 64 characters",
    "appVersion": "string <= 64 characters",
    "deviceId": "string <= 64 characters",
    "cid": "string <= 64 characters",
    "sec": "string <= 8192 characters"
}
```

**Respuesta de Autenticación:**
```json
{
    "accessToken": "token_value",
    "mdAccessToken": "market_data_token",
    "expirationTime": "2021-06-15T15:40:30.056Z",
    "userStatus": "Active",
    "userId": 15460,
    "name": "username",
    "hasLive": true,
    "outdatedTaC": false,
    "hasFunded": true,
    "hasMarketData": true,
    "outdatedLiquidationPolicy": false
}
```

##### **2. Renovar Access Token:**
```
GET /v1/auth/renewAccessToken
```

**Headers requeridos:**
```bash
Authorization: Bearer <existing_token>
Content-Type: application/json
Accept: application/json
```

**Respuesta de Renovación:**
```json
{
    "errorText": "string",
    "accessToken": "new_token_value",
    "expirationTime": "2019-08-24T14:15:22Z",
    "passwordExpirationTime": "2019-08-24T14:15:22Z",
    "userStatus": "Active",
    "userId": 0,
    "name": "string",
    "hasLive": true
}
```

##### **3. Obtener Datos de Usuario:**
```
GET /v1/auth/me
```

**Headers requeridos:**
```bash
Authorization: Bearer <access_token>
```

**Respuesta de Usuario:**
```json
{
    "errorText": "string",
    "userId": 0,
    "name": "string",
    "fullName": "string",
    "email": "string",
    "emailVerified": true,
    "isTrial": true,
    "organizationName": "string"
}
```

##### **4. OAuth Token Exchange:**
```
POST /v1/auth/oauthtoken
```

**Request Body:**
```json
{
    "grant_type": "string <= 64 characters (required)",
    "code": "string <= 8192 characters (required)",
    "redirect_uri": "string <= 8192 characters (required)",
    "client_id": "string <= 8192 characters",
    "client_secret": "string <= 8192 characters",
    "httpAuth": "string <= 8192 characters"
}
```

**Respuesta OAuth:**
```json
{
    "access_token": "string",
    "token_type": "string",
    "expires_in": 0,
    "error": "string",
    "error_description": "string"
}
```

#### **Implementación JavaScript Completa:**

##### **Adquirir Access Token:**
```javascript
const URL = 'https://live.tradovateapi.com/v1'

const credentials = {
    name: "Your credentials here",
    password: "Your credentials here",
    appId: "Sample App",
    appVersion: "1.0",
    cid: 0,
    sec: "Your API secret here"
}

async function getAccessToken() {
    let response = await fetch(URL + '/auth/accessTokenRequest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
    })
    let result = await response.json()
    return result // { accessToken, mdAccessToken, userId, ... }
}

async function main() {
    const { accessToken, mdAccessToken, userId } = await getAccessToken()
    // Usar access token
}
```

##### **Usar Access Token:**
```javascript
async function getAccounts() {
    let response = await fetch(URL + '/account/list', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}` // Access Token en HTTP requests
        }
    })
    let result = await response.json()
    return result
}
```

##### **Renovación Automática de Token:**
```javascript
// Renovar token cada 2 minutos
setInterval(async () => {
    const expiration = sessionStorage.getItem(TOKEN_EXPIRATION_KEY);
    const now = new Date().getTime();
    const exp = new Date(expiration).getTime();
    
    // Si expira en menos de 15 minutos, renovar
    if(exp - now < 15 * 60000) {
        const currentToken = sessionStorage.getItem(CURRENT_TOKEN_KEY);
        const renewal = await fetch(TRADOVATELIVE+'/auth/renewAccessToken', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': `Bearer ${currentToken}` // Token existente no expirado
            }
        });
        
        // Establecer nuevo token y expiración
        sessionStorage.setItem(CURRENT_TOKEN_KEY, renewal.accessToken);
        sessionStorage.setItem(TOKEN_EXPIRATION_KEY, renewal.expirationTime);
    }
}, 120 * 60000) // Cada 2 minutos
```

#### **IMPORTANTE - Gestión de Sesiones:**

##### **Límites de Sesión:**
- **Máximo 2 sesiones concurrentes** por usuario
- **Sesiones adicionales** cierran las más antiguas
- **Tokens expirados** causan errores 408, 429, o 500

##### **Problemas Comunes y Soluciones:**

| Situación | Problema | Solución |
|-----------|----------|----------|
| Múltiples servicios sin punto central | Sesiones antiguas se cierran | Crear servicio central para gestionar token |
| Login en .tradovate.com + API apps | API apps pueden ser expulsadas | Usar usuario dedicado para API |
| Llamadas frecuentes a accessTokenRequest | Sesiones innecesarias | Usar renewAccessToken cuando sea posible |

##### **Mejores Prácticas:**
- **1 token por instancia** de aplicación API
- **Mantener token vivo** el mayor tiempo posible
- **Renovar 15 minutos antes** de expiración
- **Compartir token válido** entre servicios dependientes

#### **Two-Factor Authentication:**
- **deviceId**: Identificador único del dispositivo (hasta 64 caracteres)
- **cid**: Client app ID proporcionado por Tradovate
- **sec**: Secret/API key proporcionado por Tradovate

### **🌐 DOMINIOS DE LA API:**

#### **Servicios Disponibles:**
- **live.tradovateapi.com** - Funcionalidad LIVE únicamente
- **demo.tradovateapi.com** - Motor de simulación
- **md.tradovateapi.com** - Feed de datos de mercado
- **replay.tradovateapi.com** - Servicio de Market Replay

#### **Uso de Tokens:**
```bash
Authorization: Bearer <access_token>
```

### **🏗️ ESTRUCTURA DE LA API:**

#### **Arquitectura General:**
- **API de bajo nivel** basada en HTTP
- **Granularidad fina** de datos para máxima flexibilidad
- **Responsabilidad del cliente** de unir dependencias
- **Dos tipos principales** de endpoints:
  - **Consulta (GET)**: Obtener datos
  - **Modificación (POST)**: Enviar/modificar datos

#### **Convenciones de Nomenclatura:**
- **Formato:** `/entidad/operacion`
- **Ejemplos:**
  - `/account/find` - Buscar cuenta
  - `/order/cancelorder` - Cancelar orden
  - `/position/deps` - Posiciones dependientes

### **OPERACIONES DE CONSULTA (GET):**

#### **1. Consulta por ID:**
```
GET /v1/entidad/item?id=ID
```

**Ejemplo - Orden por ID:**
```bash
curl -X GET --header 'Accept: application/json' \
  'https://demo.tradovateapi.com/v1/order/item?id=1000'
```

**JavaScript:**
```javascript
const response = await fetch(URL + '/order/item?id=1000', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
const order = await response.json()
```

#### **2. Listar Todas las Entidades:**
```
GET /v1/entidad/list
```

**Ejemplo - Listar Fills:**
```bash
curl -X GET --header 'Accept: application/json' \
  'https://demo.tradovateapi.com/v1/fill/list'
```

**JavaScript:**
```javascript
const response = await fetch(URL + '/fill/list', {
   headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
const fills = await response.json()
```

#### **3. Consulta por Dependencias (Master-Detail):**
```
GET /v1/entidad/deps?masterid=ID_MAESTRO
```

**Ejemplo - Posiciones de una Cuenta:**
```bash
curl -X GET --header 'Accept: application/json' \
  'https://demo.tradovateapi.com/v1/position/deps?masterid=123'
```

**JavaScript:**
```javascript
const response = await fetch(URL + '/position/deps?masterid=123', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
const positions = await response.json()
```

#### **4. Búsqueda por Nombre:**
```
GET /v1/entidad/find?name=NOMBRE
```

**Ejemplo - Buscar Producto ES:**
```bash
curl -X GET --header 'Accept: application/json' \
  'https://demo.tradovateapi.com/v1/product/find?name=ES'
```

**JavaScript:**
```javascript
const response = await fetch(URL + '/product/find?name=ES', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
const es = await response.json()
```

#### **5. Carga en Lote (Batch Loading):**
```
GET /v1/entidad/items?ids=ID1,ID2,ID3
```

**Ejemplo - Múltiples Contratos:**
```bash
curl -X GET --header 'Accept: application/json' \
  'https://demo.tradovateapi.com/v1/contract/items?ids=840972,840944'
```

**JavaScript:**
```javascript
const response = await fetch(URL + '/contract/items?ids=840972,840944', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
const contracts = await response.json()
```

### **📤 OPERACIONES DE ENVÍO (POST):**

#### **Características:**
- **Método HTTP:** POST obligatorio
- **Formato:** JSON válido en el body
- **Nomenclatura:** Sin reglas generales, refleja la semántica

#### **Ejemplo - Colocar Orden:**
```javascript
const body = {
    accountSpec: yourUserName,
    accountId: yourAcctId,
    action: "Buy",
    symbol: "MYMM1",
    orderQty: 1,
    orderType: "Market",
    isAutomated: true // OBLIGATORIO para bots
}

const response = await fetch(URL + '/order/placeorder', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${myAccessToken}`,
    },
    body: JSON.stringify(body)
})

const json = await response.json() // { orderId: 0000000 }
```

#### **IMPORTANTE - Órdenes Automatizadas:**
- **`isAutomated: true`** es OBLIGATORIO para bots
- **Por defecto es `false`** (órdenes humanas)
- **El exchange es muy estricto** con este requisito
- **Faltar puede violar** políticas del exchange

### **MANEJO DE ERRORES:**

#### **Dos Caminos de Error:**

1. **HTTP Status Codes:**
   - **404**: Datos/operación no disponible
   - **401/403**: No autorizado/acceso denegado
   - **429**: Demasiadas solicitudes
   - **423**: Demasiadas solicitudes (con penalización)

2. **Campo `errorText`:**
   - **Errores de nivel de negocio**
   - **Request exitoso en HTTP pero rechazado por lógica**
   - **Descripción textual** del problema

### **WEBSOCKETS COMPLETOS:**

#### **URL de Conexión:**
```
wss://demo.tradovateapi.com/v1/websocket
```

#### **Protocolo:**
- **Heredado de SockJS** (versiones anteriores)
- **Prefijo `wss://`** en lugar de `https://`

#### **Server Frames:**

##### **Tipos de Frames:**
1. **`'o'` - Open frame:**
   - Enviado al establecer nueva sesión
   - Requerido para confirmar conexión válida

2. **`'h'` - Heartbeat frame:**
   - Enviado cada ~2.5 segundos por el servidor
   - Cliente debe responder con `'[]'` (array vacío)

3. **`'a'` - Array frame:**
   - Contiene array de mensajes JSON codificados
   - Backbone del protocolo de mensajes de Tradovate

4. **`'c'` - Close frame:**
   - Contiene código y razón de cierre
   - Ejemplo: `c[3000, "Go away!"]`

##### **Decodificación de Frames:**
```javascript
function prepareMsg(raw) {
    const T = raw.slice(0, 1)
    let payload = null
    const data = raw.slice(1)
    if(data) {
        payload = JSON.parse(data)
    }
    return [T, payload]
}

// Uso:
mySocket.onmessage = msg => {
    const [T, data] = prepareMsg(msg.data)
    switch(T) {
        case 'a': {
            // Reaccionar a datos
            break
        }
    }
}
```

#### **Tipos de Mensajes:**

##### **Server Event Messages:**
```json
{
  "e": "props",
  "d": {
    "entityType": "order",
    "eventType": "Created",
    "entity": {
      "id": 210518,
      "accountId": 25,
      "contractId": 560901,
      "timestamp": "2016-11-04T00:02:36.626Z",
      "action": "Sell",
      "ordStatus": "PendingNew",
      "admin": false
    }
  }
}
```

**Tipos de Eventos:**
- **`"props"`**: Notificación de creación/actualización/eliminación de entidad
- **`"shutdown"`**: Notificación antes de cierre graceful
- **`"md"` y `"chart"`**: Notificaciones de market data
- **`"clock"`**: Sincronización de reloj para Market Replay

##### **Response Messages:**
```json
{
  "i": 26,
  "s": 200,
  "d": {
    "id": 478866,
    "name": "6EZ6",
    "contractMaturityId": 23574
  }
}
```

**Campos:**
- **`i`**: ID de la request del cliente
- **`s`**: HTTP status code
- **`d`**: Contenido de la respuesta

#### **Client Requests:**

##### **Formato de Request:**
```
endpoint_name
request_id
query_parameters (opcional)
body_parameters (opcional)
```

**Separadores:** `\n` (new line) entre campos

##### **Ejemplos de Requests:**

**Sin parámetros:**
```
executionReport/list
4
```

**Con query parameter:**
```
tradingPermission/ldeps
8
masterids=1
```

**Con body:**
```
contract/rollcontract
33

{"name":"YMZ6","forward":true,"ifExpired":true}
```

##### **Autorización WebSocket:**
```
authorize
2

uST01MhJMF3cR3lCs-gdQ9W0AzomYLaqsWcZ_GYgAspPRf-ZS-Wb7q3sW3pUafTm90ba4
```

**Respuesta exitosa:**
```json
a[{"s":200,"i":2}]
```

##### **Sincronización de Usuario:**
```
user/syncrequest
```

- **WebSocket obligatorio** (no HTTP)
- **Actualizaciones automáticas** de datos de usuario
- **Core para datos en tiempo real** (P&L, márgenes)
- **Permisos de API Key** afectan campos disponibles

#### **Client Heartbeats:**
- **Enviar cada 2.5 segundos** para mantener conexión
- **Frame:** `"[]"` (array vacío)
- **No usar setInterval** (puede ser throttled por browser)
- **Verificar timestamp** de último mensaje recibido
- **Servidor no envía heartbeats** mientras streama datos activos

### **🎮 MARKET REPLAY:**

#### **Hostname:**
```
wss://replay.tradovateapi.com/v1/websocket
```

#### **Inicialización de Sesión:**
```
replay/initializeclock
3

{"startTimestamp":"2019-08-26T16:43:00.000Z","speed":20,"initialBalance":51000}
```

**Parámetros:**
- **`startTimestamp`**: Tiempo de inicio de la sesión
- **`speed`**: Velocidad de replay (0-400%)
- **`initialBalance`**: Balance inicial en dólares

**Respuesta:**
```json
a[{"s":200,"i":3,"d":{"ok":true}}]
```

#### **Características:**
- **1 sesión por usuario** (nueva sesión resetea la actual)
- **Múltiples conexiones** pueden unirse a la misma sesión
- **Sin inicialización** = unirse a sesión existente
- **Sesión descartada** automáticamente sin conexiones

#### **Sincronización de Reloj:**
```json
a[{"e":"clock","d":"{\"t\":\"2019-08-26T16:43:08.599Z\",\"s\":20}"}]
```

**Campos:**
- **`t`**: Timestamp actual del replay
- **`s`**: Velocidad actual del replay

#### **Control de Velocidad:**
```
replay/changespeed
49

{"speed":100}
```

- **Rango:** 0-400% (400% = 4x tiempo real)
- **Velocidad 0** = pausado
- **Servidor puede pausar** automáticamente

#### **Verificación de Disponibilidad:**
```
GET /v1/replay/checkReplaySession
```

- **Verificar** si fecha/hora está permitida
- **Depende de entitlements** del cliente

### **MARKET DATA API COMPLETO:**

#### **Flujo Típico:**

1. **Adquirir Access Token** usando credenciales
2. **Abrir WebSocket** y autorizar
3. **Construir Request** con parámetros JSON
4. **Suscribirse** a datos en tiempo real

#### **Parámetros de Request:**
```json
{
    "symbol": "ESM7"  // Por símbolo del contrato
}
// o
{
    "symbol": 123456  // Por ID del contrato
}
```

#### **1. Subscribe Quote:**
```
md/subscribeQuote
```

**Parámetros:**
```json
{ "symbol": "ESM7" | 123456 }
```

**Data Message:**
```json
{
  "e": "md",
  "d": {
    "quotes": [
      {
        "timestamp": "2021-04-13T04:59:06.588Z",
        "contractId": 123456,
        "entries": {
            "Bid": { "price": 18405.123, "size": 7.123 },
            "TotalTradeVolume": { "size": 4118.123 },
            "Offer": { "price": 18410.012, "size": 12.35 },
            "LowPrice": { "price": 18355.23 },
            "Trade": { "price": 18405.023, "size": 2.10 },
            "OpenInterest": { "size": 40702.024 },
            "OpeningPrice": { "price": 18515.123 },
            "HighPrice": { "price": 18520.125 },
            "SettlementPrice": { "price": 18520.257 }
        }
      }
    ]
  }
}
```

**Unsubscribe Quote:**
```
md/unsubscribeQuote
```

#### **2. Subscribe DOM (Depth of Market):**
```
md/subscribeDOM
```

**Parámetros:**
```json
{ "symbol": "ESM7" | 123456 }
```

**Data Message:**
```json
{
  "e": "md",
  "d": {
    "doms": [
      {
        "contractId": 123456,
        "timestamp": "2021-04-13T11:33:57.488Z",
        "bids": [
          {"price": 2335.25, "size": 33.54},
          {"price": 2333, "size": 758.21}
        ],
        "offers": [
          {"price": 2335.5, "size": 255.12},
          {"price": 2337.75, "size": 466.64}
        ]
      }
    ]
  }
}
```

**Unsubscribe DOM:**
```
md/unsubscribeDOM
```

#### **3. Subscribe Histogram:**
```
md/subscribeHistogram
```

**Parámetros:**
```json
{ "symbol": "ESM7" | 123456 }
```

**Data Message:**
```json
{
  "e": "md",
  "d": {
    "histograms": [
      {
        "contractId": 123456,
        "timestamp": "2017-04-13T11:33:57.412Z",
        "tradeDate": {
          "year": 2022,
          "month": 4,
          "day": 13
        },
        "base": 2338.75,
        "items": {
          "-14": 5906.67,
          "2": 1234.55
        },
        "refresh": false
      }
    ]
  }
}
```

**Unsubscribe Histogram:**
```
md/unsubscribeHistogram
```

#### **4. Get Chart:**
```
md/getChart
```

**Parámetros:**
```json
{
  "symbol": "ESM7" | 123456,
  "chartDescription": {
    "underlyingType": "MinuteBar",
    "elementSize": 15,
    "elementSizeUnit": "UnderlyingUnits",
    "withHistogram": true
  },
  "timeRange": {
    "closestTimestamp": "2017-04-13T11:33Z",
    "closestTickId": 123,
    "asFarAsTimestamp": "2017-04-13T11:33Z",
    "asMuchAsElements": 66
  }
}
```

**Tipos de Chart Disponibles:**
- **`Tick`**: Datos por tick
- **`DailyBar`**: Barras diarias
- **`MinuteBar`**: Barras por minuto
- **`Custom`**: Personalizado
- **`DOM`**: Depth of Market

**Unidades de Element Size:**
- **`Volume`**: Por volumen
- **`Range`**: Por rango
- **`UnderlyingUnits`**: Unidades subyacentes
- **`Renko`**: Renko
- **`MomentumRange`**: Rango de momentum
- **`PointAndFigure`**: Punto y figura
- **`OFARange`**: Rango OFA

**Respuesta:**
```json
{
  "s": 200,
  "i": 13,
  "d": {
    "historicalId": 32,
    "realtimeId": 31
  }
}
```

**Data Message:**
```json
{
  "e": "chart",
  "d": {
    "charts": [
      {
        "id": 9,
        "td": 20170413,
        "bars": [
          {
            "timestamp": "2017-04-13T11:00:00.000Z",
            "open": 2334.25,
            "high": 2334.5,
            "low": 2333,
            "close": 2333.75,
            "upVolume": 4712.234,
            "downVolume": 201.124,
            "upTicks": 1333.567,
            "downTicks": 82.890,
            "bidVolume": 2857.123,
            "offerVolume": 2056.224
          }
        ]
      }
    ]
  }
}
```

**Cancel Chart:**
```
md/cancelChart
```

**Parámetros:**
```json
{
  "subscriptionId": 123456
}
```

### **TICK CHARTS:**

#### **Requesting Tick Charts:**
```json
{
  "symbol": "ESU9",
  "chartDescription": {
    "underlyingType": "Tick",
    "elementSize": 1,
    "elementSizeUnit": "UnderlyingUnits"
  },
  "timeRange": {
    // Campos opcionales
  }
}
```

#### **Data Stream Message:**
```json
{
    "charts": [
        {
            "id": 16335,
            "s": "db",
            "td": 20210718,
            "bp": 11917,
            "bt": 1563421179735,
            "ts": 0.25,
            "tks": [
                {
                    "t": 0,
                    "p": 0,
                    "s": 3,
                    "b": -1,
                    "a": 0,
                    "bs": 122.21,
                    "as": 28.35,
                    "id": 11768401
                }
            ]
        },
        {
            "id": 16335,
            "eoh": true
        }
    ]
}
```

**Campos del Packet:**
- **`id`**: Subscription ID
- **`s`**: Fuente de datos del packet
- **`td`**: Fecha de trading (YYYYMMDD)
- **`bp`**: Precio base del packet
- **`bt`**: Timestamp base del packet
- **`ts`**: Tick size del contrato
- **`tks`**: Array de ticks
- **`eoh`**: End of history flag

**Campos del Tick:**
- **`t`**: Timestamp relativo del tick
- **`p`**: Precio relativo del tick
- **`s`**: Tamaño del tick (volumen)
- **`b`**: Precio bid relativo (opcional)
- **`a`**: Precio ask relativo (opcional)
- **`bs`**: Tamaño bid (opcional)
- **`as`**: Tamaño ask (opcional)
- **`id`**: ID del tick

#### **Procesamiento de Tick Stream:**
```javascript
function processTickChartMessage(msg) {
    const result = [];
    if (msg.charts && msg.charts.length) {
        for (let i = 0; i < msg.charts.length; ++i) {
            const packet = msg.charts[i];
            if (packet.eoh) {
                // Historical ticks are loaded.
            }
            else if (packet.tks && packet.tks.length) {
                for (let j = 0; j < packet.tks.length; ++j) {
                    const tick = packet.tks[j];

                    const timestamp = packet.bt + tick.t;   // Actual tick timestamp
                    const price = packet.bp + tick.p;       // Actual tick price

                    const bid = tick.bs && (packet.bp + tick.b);    // Actual bid price
                    const ask = tick.as && (packet.bp + tick.a);    // Actual ask price

                    result.push({
                        id: tick.id,
                        timestamp: new Date(timestamp),
                        price: price * packet.ts,           // Tick price as contract price
                        size: tick.s,                       // Tick size (tick volume)
                        bidPrice: bid && (bid * packet.ts), // Bid price as contract price
                        bidSize: tick.bs,
                        askPrice: ask && (ask * packet.ts), // Ask price as contract price
                        askSize: tick.as,
                    });
                }
            }
        }
    }
    return result;
}
```

### **CONTRACT LIBRARY:**

#### **Contract Dependents:**
```
GET /v1/contract/deps?masterid=ID
```

**Parámetros:**
- **`masterid`**: ID de la entidad ContractMaturity

**Respuesta:**
```json
[
  {
    "id": 0,
    "name": "string",
    "contractMaturityId": 0
  }
]
```

#### **Contract Find:**
```
GET /v1/contract/find?name=NOMBRE
```

**Parámetros:**
- **`name`**: Nombre del contrato

**Respuesta:**
```json
{
  "id": 0,
  "name": "string",
  "contractMaturityId": 0
}
```

#### **Contract Item:**
```
GET /v1/contract/item?contractid=ID
```

**Parámetros:**
- **`contractid`**: ID del contrato

**Respuesta:**
```json
{
  "id": 0,
  "name": "string",
  "contractMaturityId": 0
}
```

#### **Contract Items (Batch):**
```
GET /v1/contract/items?contractids=ID1,ID2,ID3
```

**Parámetros:**
- **`contractids`**: Lista de IDs separados por comas

#### **Contract List:**
```
GET /v1/contract/list
```

**Respuesta:**
```json
[
  {
    "id": 0,
    "name": "string",
    "contractMaturityId": 0
  }
]
```

#### **Contract Maturity Dependents:**
```
GET /v1/contract/ldeps?masterid=ID
```

**Parámetros:**
- **`masterid`**: ID de la entidad Product

#### **Roll Contract:**
```
POST /v1/contract/rollcontract
```

**Body:**
```json
{
  "fromContractId": 0,
  "toContractId": 0
}
```

#### **Roll Contracts:**
```
POST /v1/contract/rollcontracts
```

**Body:**
```json
{
  "fromContractId": 0,
  "toContractId": 0
}
```

#### **Contract Suggest:**
```
GET /v1/contractSuggest?query=QUERY
```

**Parámetros:**
- **`query`**: Texto de búsqueda

#### **Contract Group:**
```
GET /v1/contractGroup/item?contractgroupid=ID
GET /v1/contractGroup/items?contractgroupids=ID1,ID2
GET /v1/contractGroup/list
```

#### **Contract Maturity:**
```
GET /v1/contractMaturity/item?contractmaturityid=ID
GET /v1/contractMaturity/items?contractmaturityids=ID1,ID2
GET /v1/contractMaturity/list
```

#### **Currency:**
```
GET /v1/currency/item?currencyid=ID
GET /v1/currency/items?currencyids=ID1,ID2
GET /v1/currency/list
```

#### **Currency Rate:**
```
GET /v1/currencyRate/item?currencyrateid=ID
GET /v1/currencyRate/items?currencyrateids=ID1,ID2
GET /v1/currencyRate/list
```

#### **Exchange:**
```
GET /v1/exchange/item?exchangeid=ID
GET /v1/exchange/items?exchangeids=ID1,ID2
GET /v1/exchange/list
```

#### **Product:**
```
GET /v1/product/item?productid=ID
GET /v1/product/items?productids=ID1,ID2
GET /v1/product/list
```

#### **Product Session:**
```
GET /v1/productSession/item?productsessionid=ID
GET /v1/productSession/items?productsessionids=ID1,ID2
GET /v1/productSession/list
```

#### **Spread Definition:**
```
GET /v1/spreadDefinition/item?spreaddefinitionid=ID
GET /v1/spreadDefinition/items?spreaddefinitionids=ID1,ID2
GET /v1/spreadDefinition/list
```

---

### **ORDERS Y FILL MANAGEMENT:**

#### **Command Endpoints:**
```
GET /v1/command/deps?masterid=ID
GET /v1/command/item?commandid=ID
GET /v1/command/items?commandids=ID1,ID2
GET /v1/command/ldeps?masterid=ID
GET /v1/command/list
```

#### **Command Report:**
```
GET /v1/commandReport/deps?masterid=ID
GET /v1/commandReport/item?commandreportid=ID
GET /v1/commandReport/items?commandreportids=ID1,ID2
GET /v1/commandReport/ldeps?masterid=ID
GET /v1/commandReport/list
```

#### **Execution Report:**
```
GET /v1/executionReport/deps?masterid=ID
GET /v1/executionReport/item?executionreportid=ID
GET /v1/executionReport/items?executionreportids=ID1,ID2
GET /v1/executionReport/ldeps?masterid=ID
GET /v1/executionReport/list
```

#### **Fill Endpoints:**
```
GET /v1/fill/deps?masterid=ID
GET /v1/fill/item?fillid=ID
GET /v1/fill/items?fillids=ID1,ID2
GET /v1/fill/ldeps?masterid=ID
GET /v1/fill/list
```

#### **Fill Fee:**
```
GET /v1/fillFee/deps?masterid=ID
GET /v1/fillFee/item?fillfeeid=ID
GET /v1/fillFee/items?fillfeeids=ID1,ID2
GET /v1/fillFee/ldeps?masterid=ID
GET /v1/fillFee/list
```

#### **Order Management:**
```
GET /v1/order/deps?masterid=ID
GET /v1/order/item?orderid=ID
GET /v1/order/items?orderids=ID1,ID2
GET /v1/order/ldeps?masterid=ID
GET /v1/order/list
```

#### **Order Actions:**
```
POST /v1/order/cancelorder
POST /v1/order/liquidateposition
POST /v1/order/liquidatepositions
POST /v1/order/modifyorder
POST /v1/order/placeoco
POST /v1/order/placeorder
POST /v1/order/placeoso
```

#### **Order Strategy:**
```
POST /v1/orderStrategy/interruptorderstrategy
POST /v1/orderStrategy/startorderstrategy
POST /v1/orderStrategy/modifyorderstrategy
GET /v1/orderStrategy/deps?masterid=ID
GET /v1/orderStrategy/item?orderstrategyid=ID
GET /v1/orderStrategy/items?orderstrategyids=ID1,ID2
GET /v1/orderStrategy/ldeps?masterid=ID
GET /v1/orderStrategy/list
```

#### **Order Strategy Link:**
```
GET /v1/orderStrategyLink/deps?masterid=ID
GET /v1/orderStrategyLink/item?orderstrategylinkid=ID
GET /v1/orderStrategyLink/items?orderstrategylinkids=ID1,ID2
GET /v1/orderStrategyLink/ldeps?masterid=ID
GET /v1/orderStrategyLink/list
```

#### **Order Version:**
```
GET /v1/orderVersion/deps?masterid=ID
GET /v1/orderVersion/item?orderversionid=ID
GET /v1/orderVersion/items?orderversionids=ID1,ID2
GET /v1/orderVersion/ldeps?masterid=ID
GET /v1/orderVersion/list
```

#### **Position Management:**
```
GET /v1/position/deps?masterid=ID
GET /v1/position/find?query=QUERY
GET /v1/position/item?positionid=ID
GET /v1/position/items?positionids=ID1,ID2
GET /v1/position/ldeps?masterid=ID
GET /v1/position/list
```

#### **Fill Pair:**
```
GET /v1/fillPair/deps?masterid=ID
GET /v1/fillPair/item?fillpairid=ID
GET /v1/fillPair/items?fillpairids=ID1,ID2
GET /v1/fillPair/ldeps?masterid=ID
GET /v1/fillPair/list
```

---

### **ACCOUNTING Y GESTIÓN DE CUENTA:**

#### **Account Management:**
```
GET /v1/account/deps?masterid=ID
GET /v1/account/find?query=QUERY
GET /v1/account/item?accountid=ID
GET /v1/account/items?accountids=ID1,ID2
GET /v1/account/ldeps?masterid=ID
GET /v1/account/list
```

#### **Account Actions:**
```
POST /v1/account/resetdemoaccountstate
GET /v1/account/accountsuggest?query=QUERY
```

#### **Cash Balance:**
```
GET /v1/cashBalance/deps?masterid=ID
GET /v1/cashBalance/getcashbalancesnapshot
GET /v1/cashBalance/item?cashbalanceid=ID
GET /v1/cashBalance/items?cashbalanceids=ID1,ID2
GET /v1/cashBalance/ldeps?masterid=ID
GET /v1/cashBalance/list
```

#### **Cash Balance Log:**
```
GET /v1/cashBalanceLog/deps?masterid=ID
GET /v1/cashBalanceLog/item?cashbalancelogid=ID
GET /v1/cashBalanceLog/items?cashbalancelogids=ID1,ID2
GET /v1/cashBalanceLog/ldeps?masterid=ID
GET /v1/cashBalanceLog/list
```

#### **Margin Snapshot:**
```
GET /v1/marginSnapshot/deps?masterid=ID
GET /v1/marginSnapshot/item?marginsnapshotid=ID
GET /v1/marginSnapshot/items?marginsnapshotids=ID1,ID2
GET /v1/marginSnapshot/ldeps?masterid=ID
GET /v1/marginSnapshot/list
```

#### **Trading Permission:**
```
GET /v1/tradingPermission/deps?masterid=ID
GET /v1/tradingPermission/item?tradingpermissionid=ID
GET /v1/tradingPermission/items?tradingpermissionids=ID1,ID2
GET /v1/tradingPermission/ldeps?masterid=ID
GET /v1/tradingPermission/list
```

---

### **GESTIÓN DE RIESGO:**

#### **Account Risk Status:**
```
GET /v1/accountRiskStatus/deps?masterid=ID
GET /v1/accountRiskStatus/item?accountriskstatusid=ID
GET /v1/accountRiskStatus/items?accountriskstatusids=ID1,ID2
GET /v1/accountRiskStatus/ldeps?masterid=ID
GET /v1/accountRiskStatus/list
```

#### **Account Risk Actions:**
```
POST /v1/accountRiskStatus/resetautoliqstatus
POST /v1/accountRiskStatus/setaccountnotes
POST /v1/accountRiskStatus/setadminautoliqaction
POST /v1/accountRiskStatus/updatemaxnetliq
```

#### **Contract Margin:**
```
GET /v1/contractMargin/deps?masterid=ID
GET /v1/contractMargin/item?contractmarginid=ID
GET /v1/contractMargin/items?contractmarginids=ID1,ID2
GET /v1/contractMargin/ldeps?masterid=ID
GET /v1/contractMargin/list
```

#### **Permissioned Account Auto Liq:**
```
GET /v1/permissionedAccountAutoLiq/deps?masterid=ID
GET /v1/permissionedAccountAutoLiq/item?permissionedaccountautoliqid=ID
GET /v1/permissionedAccountAutoLiq/items?permissionedaccountautoliqids=ID1,ID2
GET /v1/permissionedAccountAutoLiq/ldeps?masterid=ID
GET /v1/permissionedAccountAutoLiq/list
```

#### **Product Margin:**
```
GET /v1/productMargin/deps?masterid=ID
GET /v1/productMargin/item?productmarginid=ID
GET /v1/productMargin/items?productmarginids=ID1,ID2
GET /v1/productMargin/ldeps?masterid=ID
GET /v1/productMargin/list
```

#### **User Account Auto Liq:**
```
POST /v1/userAccountAutoLiq/create
GET /v1/userAccountAutoLiq/deps?masterid=ID
GET /v1/userAccountAutoLiq/item?useraccountautoliqid=ID
GET /v1/userAccountAutoLiq/items?useraccountautoliqids=ID1,ID2
GET /v1/userAccountAutoLiq/ldeps?masterid=ID
GET /v1/userAccountAutoLiq/list
POST /v1/userAccountAutoLiq/update
POST /v1/userAccountAutoLiq/updateuserautoliq
```

#### **User Account Position Limit:**
```
POST /v1/userAccountPositionLimit/create
POST /v1/userAccountPositionLimit/deleteuseraccountpositionlimit
GET /v1/userAccountPositionLimit/deps?masterid=ID
GET /v1/userAccountPositionLimit/item?useraccountpositionlimitid=ID
GET /v1/userAccountPositionLimit/items?useraccountpositionlimitids=ID1,ID2
GET /v1/userAccountPositionLimit/ldeps?masterid=ID
POST /v1/userAccountPositionLimit/update
```

#### **User Account Risk Parameter:**
```
POST /v1/userAccountRiskParameter/create
POST /v1/userAccountRiskParameter/deleteuseraccountriskparameter
GET /v1/userAccountRiskParameter/deps?masterid=ID
GET /v1/userAccountRiskParameter/item?useraccountriskparameterid=ID
GET /v1/userAccountRiskParameter/items?useraccountriskparameterids=ID1,ID2
GET /v1/userAccountRiskParameter/ldeps?masterid=ID
POST /v1/userAccountRiskParameter/update
```

---

### **💳 FEES Y SUBSCRIPTIONS:**

#### **Market Data Subscription Exchange Scope:**
```
GET /v1/marketDataSubscriptionExchangeScope/deps?masterid=ID
GET /v1/marketDataSubscriptionExchangeScope/item?marketdatasubscriptionexchangescopeid=ID
GET /v1/marketDataSubscriptionExchangeScope/items?marketdatasubscriptionexchangescopeids=ID1,ID2
GET /v1/marketDataSubscriptionExchangeScope/ldeps?masterid=ID
GET /v1/marketDataSubscriptionExchangeScope/list
```

#### **Market Data Subscription Plan:**
```
GET /v1/marketDataSubscriptionPlan/deps?masterid=ID
GET /v1/marketDataSubscriptionPlan/item?marketdatasubscriptionplanid=ID
GET /v1/marketDataSubscriptionPlan/items?marketdatasubscriptionplanids=ID1,ID2
GET /v1/marketDataSubscriptionPlan/ldeps?masterid=ID
GET /v1/marketDataSubscriptionPlan/list
```

#### **Tradovate Subscription Plan:**
```
GET /v1/tradovateSubscriptionPlan/deps?masterid=ID
GET /v1/tradovateSubscriptionPlan/item?tradovatesubscriptionplanid=ID
GET /v1/tradovateSubscriptionPlan/items?tradovatesubscriptionplanids=ID1,ID2
GET /v1/tradovateSubscriptionPlan/ldeps?masterid=ID
GET /v1/tradovateSubscriptionPlan/list
```

---

### **🔔 ALERTS Y CONFIGURACIÓN:**

#### **Admin Alert Signal:**
```
POST /v1/adminAlertSignal/completealertsignal
POST /v1/adminAlertSignal/takealertsignalownership
```

#### **Alert Management:**
```
POST /v1/alert/createalert
POST /v1/alert/deletealert
GET /v1/alert/deps?masterid=ID
POST /v1/alert/dismissalertsignal
GET /v1/alert/item?alertid=ID
GET /v1/alert/items?alertids=ID1,ID2
GET /v1/alert/ldeps?masterid=ID
POST /v1/alert/markreadalertsignal
POST /v1/alert/modifyalert
POST /v1/alert/resetalert
```

#### **Alert Signal:**
```
GET /v1/alertSignal/deps?masterid=ID
GET /v1/alertSignal/item?alertsignalid=ID
GET /v1/alertSignal/items?alertsignalid=ID1,ID2
GET /v1/alertSignal/ldeps?masterid=ID
GET /v1/alertSignal/list
```

#### **Configuration Endpoints:**
```
GET /v1/adminAlert/deps?masterid=ID
GET /v1/adminAlert/item?adminalertid=ID
GET /v1/adminAlert/items?adminalertids=ID1,ID2
GET /v1/adminAlert/ldeps?masterid=ID
GET /v1/adminAlert/list
```

#### **Clearing House:**
```
GET /v1/clearingHouse/deps?masterid=ID
GET /v1/clearingHouse/item?clearinghouseid=ID
GET /v1/clearingHouse/items?clearinghouseids=ID1,ID2
GET /v1/clearingHouse/ldeps?masterid=ID
GET /v1/clearingHouse/list
```

#### **Entitlement:**
```
GET /v1/entitlement/deps?masterid=ID
GET /v1/entitlement/item?entitlementid=ID
GET /v1/entitlement/items?entitlementids=ID1,ID2
GET /v1/entitlement/ldeps?masterid=ID
GET /v1/entitlement/list
```

#### **Order Strategy Type:**
```
GET /v1/orderStrategyType/deps?masterid=ID
GET /v1/orderStrategyType/item?orderstrategytypeid=ID
GET /v1/orderStrategyType/items?orderstrategytypeids=ID1,ID2
GET /v1/orderStrategyType/ldeps?masterid=ID
GET /v1/orderStrategyType/list
```

#### **Property:**
```
GET /v1/property/deps?masterid=ID
GET /v1/property/item?propertyid=ID
GET /v1/property/items?propertyids=ID1,ID2
GET /v1/property/ldeps?masterid=ID
GET /v1/property/list
```

---

### **👤 GESTIÓN DE USUARIOS:**

#### **Contact Info:**
```
GET /v1/contactInfo/deps?masterid=ID
GET /v1/contactInfo/item?contactinfoid=ID
GET /v1/contactInfo/items?contactinfoids=ID1,ID2
GET /v1/contactInfo/ldeps?masterid=ID
GET /v1/contactInfo/list
```

#### **Market Data Subscription:**
```
POST /v1/marketDataSubscription/create
GET /v1/marketDataSubscription/deps?masterid=ID
GET /v1/marketDataSubscription/item?marketdatasubscriptionid=ID
GET /v1/marketDataSubscription/items?marketdatasubscriptionids=ID1,ID2
GET /v1/marketDataSubscription/ldeps?masterid=ID
GET /v1/marketDataSubscription/list
POST /v1/marketDataSubscription/update
```

#### **Organization:**
```
GET /v1/organization/deps?masterid=ID
GET /v1/organization/item?organizationid=ID
GET /v1/organization/items?organizationids=ID1,ID2
GET /v1/organization/ldeps?masterid=ID
GET /v1/organization/list
```

#### **Second Market Data Subscription:**
```
GET /v1/secondMarketDataSubscription/deps?masterid=ID
GET /v1/secondMarketDataSubscription/item?secondmarketdatasubscriptionid=ID
GET /v1/secondMarketDataSubscription/items?secondmarketdatasubscriptionids=ID1,ID2
GET /v1/secondMarketDataSubscription/ldeps?masterid=ID
GET /v1/secondMarketDataSubscription/list
```

#### **Tradovate Subscription:**
```
POST /v1/tradovateSubscription/create
GET /v1/tradovateSubscription/deps?masterid=ID
GET /v1/tradovateSubscription/item?tradovatesubscriptionid=ID
GET /v1/tradovateSubscription/items?tradovatesubscriptionids=ID1,ID2
GET /v1/tradovateSubscription/ldeps?masterid=ID
GET /v1/tradovateSubscription/list
POST /v1/tradovateSubscription/update
```

#### **User Management:**
```
POST /v1/user/accepttradingpermission
POST /v1/user/activatesecondmarketdatasubscriptionrenewal
POST /v1/user/addmarketdatasubscription
POST /v1/user/addsecondmarketdatasubscription
POST /v1/user/addtradovatesubscription
POST /v1/user/canceleverything
POST /v1/user/cancelsecondmarketdatasubscription
POST /v1/user/cancelsecondmarketdatasubscriptionrenewal
POST /v1/user/canceltradovatesubscription
POST /v1/user/createevaluationaccounts
POST /v1/user/createevaluationusers
POST /v1/user/createtradingpermission
GET /v1/user/find?query=QUERY
GET /v1/user/getaccounttradingpermissions
GET /v1/user/getsecondmarketdatasubscriptioncost
GET /v1/user/item?userid=ID
GET /v1/user/items?userids=ID1,ID2
GET /v1/user/list
POST /v1/user/modifycredentials
POST /v1/user/modifyemailaddress
POST /v1/user/modifypassword
POST /v1/user/opendemoaccount
POST /v1/user/requesttradingpermission
POST /v1/user/revoketradingpermission
POST /v1/user/revoketradingpermissions
POST /v1/user/signuporganizationmember
GET /v1/user/suggest?query=QUERY
POST /v1/user/syncrequest
```

#### **User Plugin:**
```
POST /v1/userPlugin/addentitlementsubscription
POST /v1/userPlugin/changedpluginpermission
POST /v1/userPlugin/create
GET /v1/userPlugin/deps?masterid=ID
GET /v1/userPlugin/item?userpluginid=ID
GET /v1/userPlugin/items?userpluginids=ID1,ID2
GET /v1/userPlugin/ldeps?masterid=ID
GET /v1/userPlugin/list
POST /v1/userPlugin/update
```

#### **User Property:**
```
GET /v1/userProperty/deps?masterid=ID
GET /v1/userProperty/item?userpropertyid=ID
GET /v1/userProperty/items?userpropertyids=ID1,ID2
GET /v1/userProperty/ldeps?masterid=ID
GET /v1/userProperty/list
```

#### **User Session:**
```
GET /v1/userSession/deps?masterid=ID
GET /v1/userSession/item?usersessionid=ID
GET /v1/userSession/items?usersessionids=ID1,ID2
GET /v1/userSession/ldeps?masterid=ID
GET /v1/userSession/list
```

#### **User Session Stats:**
```
GET /v1/userSessionStats/deps?masterid=ID
GET /v1/userSessionStats/item?usersessionstatsid=ID
GET /v1/userSessionStats/items?usersessionstatsids=ID1,ID2
GET /v1/userSessionStats/ldeps?masterid=ID
GET /v1/userSessionStats/list
```

---

### **💬 CHAT Y COMUNICACIÓN:**

#### **Chat Management:**
```
POST /v1/chat/closechat
GET /v1/chat/deps?masterid=ID
GET /v1/chat/item?chatid=ID
GET /v1/chat/items?chatids=ID1,ID2
GET /v1/chat/ldeps?masterid=ID
GET /v1/chat/list
```

#### **Chat Message:**
```
POST /v1/markasreadchatmessage
POST /v1/postchatmessage
GET /v1/chatMessage/deps?masterid=ID
GET /v1/chatMessage/item?chatmessageid=ID
GET /v1/chatMessage/items?chatmessageids=ID1,ID2
GET /v1/chatMessage/ldeps?masterid=ID
GET /v1/chatMessage/list
```

---

## **IMPLEMENTACIÓN EN EL BOT**

### **Archivos a Modificar:**
1. **`scripts/tradovate_connector.py`** - Conector principal
2. **`config/lightning_50k_final_config.json`** - Configuración de API
3. **`scripts/tradeify_bot_main.py`** - Integración principal

### **Próximos Pasos:**
1. Documentación completa de autenticación
2. Endpoints de cuenta y órdenes
3. Gestión de riesgo y posiciones
4. Estructura completa de la API
5. WebSockets y Market Data
6. Market Replay
7. Tick Charts y Contract Library
8. Orders y Fill Management
9. Accounting y Risk Management
10. Fees y Subscriptions
11. Alerts y Configuration
12. User Management y Chat
13. ⏳ Implementación en código
14. ⏳ Pruebas de integración

---

## **PROCESO DE SUSCRIPCIÓN Y CONFIGURACIÓN**

### **🔑 REQUISITOS PREVIOS COMPLETOS:**
- **Cuenta de Tradovate "en vivo" y fondeada**
- **Saldo mínimo de $1,000 USD**
- **Suscripción al add-on de API Access ($25/mes)**
- 🔴 **NUEVO:** **Verificación de propiedad exclusiva del código del bot**
- 🔴 **NUEVO:** **Video en vivo demostrando el bot funcionando en tu PC**
- 🔴 **RESTRICCIÓN:** **Bots HFT prohibidos - trades de menos de 5 segundos monitoreados**
- **PLATAFORMAS:** Tradeify soporta **Tradovate, TradingView Y NinjaTrader**

### **📱 PROCESO DE SUSCRIPCIÓN PASO A PASO:**

#### **1. Login en Tradovate Web Trader:**
- Acceder a tu cuenta en `tradovate.com`
- Usar credenciales: TDY030574

#### **2. Application Settings:**
- **Ubicación:** Esquina superior derecha - Gear icon visible
- **Acceso:** Click en el ícono de engranaje

#### **3. Pestaña API Access:**
- **Ubicación:** Entre otras pestañas (Accounts, Subscriptions, Your Profile, Preferences, Security & Privacy, Transfers & Payments, Add-Ons)
- **Estado:** Debe mostrar opciones de API Access

#### **4. Botón Subscribe:**
- **Precio:** $25 USD por mes
- **Formas de pago:** Saldo de cuenta o tarjeta
- **Restricción:** Si no tienes cuenta fondeada, el botón estará deshabilitado (gris)
- **Botón "API Docs":** Disponible en azul para consultar documentación

### **GENERACIÓN DE API KEY:**

#### **1. Volver a Application Settings > API Access:**
- Después de suscribirte, regresar a la pestaña

#### **2. Completar proceso de auto-atestación:**
- **Requisito:** Entender completamente los riesgos de futures trading
- **Proceso:** Leer y aceptar términos de riesgo

#### **3. Firmar acuerdo digital:**
- **Tipo:** Acuerdo de trading de futuros
- **Responsabilidad:** Aceptar riesgos del mercado

#### **4. Click en "Generate API Key":**
- **Ubicación:** Botón principal en la pestaña API Access

#### **5. Seleccionar permisos deseados:**
- **Opciones:** Trading, Market Data, Account Info
- **Recomendación:** Seleccionar todos los permisos necesarios

#### **6. Click en "Generate":**
- **Confirmación:** Proceso de generación de la API Key

#### **7. IMPORTANTE - API Key se muestra UNA SOLA VEZ:**
- **Copiar inmediatamente** la API Key generada
- **Guardar en lugar seguro** (no se puede recuperar después)
- **Configurar en el bot** antes de cerrar la ventana

### **🔒 CONSIDERACIONES DE SEGURIDAD:**

#### **Protección de la API Key:**
- **NUNCA compartir** la API Key con nadie
- **NO exponer** en repositorios públicos de código
- **Almacenar** en ubicación segura y encriptada
- **Entender completamente** los riesgos antes de usar la API

#### **Mejores Prácticas:**
- **Una API Key por aplicación** (no reutilizar)
- **Rotar claves** periódicamente
- **Monitorear uso** de la API Key
- **Revocar inmediatamente** si se sospecha compromiso

### **📞 SOPORTE TÉCNICO:**

#### **Recursos de Ayuda:**
- **API Support Center de Tradovate:** Centro de ayuda oficial
- **Email directo:** apisupport@ninjatrader.com
- **Documentación oficial:** Disponible en la plataforma
- **Chat en vivo:** Soporte técnico en tiempo real

#### **Problemas Comunes:**
- **API Key no funciona:** Verificar permisos y estado de cuenta
- **Rate limits:** Respetar límites de la API
- **Autenticación fallida:** Verificar credenciales y tokens
- **WebSocket desconectado:** Verificar conexión y heartbeats

### **INTEGRACIÓN CON SISTEMA DE TRADING:**

#### **Esta documentación será utilizada para:**
- **Configurar conexión** con API de Tradovate
- **Implementar autenticación** segura y robusta
- **Gestionar órdenes** y posiciones automáticamente
- **Obtener datos de mercado** en tiempo real
- **Automatizar estrategias** de trading (V5)
- **Cumplir reglas** de compliance de Tradeify

#### **Notas Importantes:**
- **La API requiere** comprensión completa de los riesgos de futures trading
- **Es necesario firmar** acuerdos digitales antes de usar
- **El costo mensual** es de $25 USD
- **Se requiere cuenta real** con fondos mínimos de $1,000

---

**📱 Desarrollador:** Matias Rouaux  
**Propósito:** Integración completa con bot de trading  
**Fecha:** 21 de agosto de 2025  
**Estado:** **DOCUMENTACIÓN CORREGIDA TRAS VALIDACIÓN TRADEIFY**

## **RESUMEN DE CORRECCIONES APLICADAS:**

### **CORRECCIONES IMPLEMENTADAS:**
1. **Plataformas:** Agregado soporte para TradingView y NinjaTrader
2. **Instrumentos:** Expandida lista incluyendo ES, NQ, YM, RTY, agrícolas, divisas, EUREX
3. **Verificación:** Agregados requisitos de propiedad exclusiva + video en vivo
4. **Restricciones HFT:** Agregada prohibición de trades <5 segundos

### **ACCIÓN PENDIENTE:**
- **Verificar todos los endpoints específicamente para cuentas Tradeify**
- **Confirmar parámetros con soporte antes de implementación**
