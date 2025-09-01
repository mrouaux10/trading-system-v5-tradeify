# TRADOVATE API - DOCUMENTACIÓN COMPLETA OFICIAL (v1.0.0)

> **Fuente:** https://api.tradovate.com/
> **Fecha:** 31 de Enero, 2025
> **Estado:** Documentación oficial verificada y actualizada

## ÍNDICE

1. [INTRODUCCIÓN Y REQUISITOS](#introducción-y-requisitos)
2. [ACCESO Y AUTENTICACIÓN](#acceso-y-autenticación)
3. [ESTRUCTURA DE LA API](#estructura-de-la-api)
4. [WEBSOCKETS](#websockets)
5. [DATOS DE MERCADO](#datos-de-mercado)
6. [ÓRDENES](#órdenes)
7. [POSICIONES](#posiciones)
8. [CONTABILIDAD](#contabilidad)
9. [GESTIÓN DE RIESGOS](#gestión-de-riesgos)
10. [USUARIOS Y PERMISOS](#usuarios-y-permisos)
11. [CHAT Y COMUNICACIONES](#chat-y-comunicaciones)
12. [EJEMPLOS DE IMPLEMENTACIÓN](#ejemplos-de-implementación)

---

## INTRODUCCIÓN Y REQUISITOS

### Descripción General
La API de Tradovate es una interfaz web robusta que permite a los clientes integrar los servicios de trading de Tradovate en sus propias aplicaciones y extensiones. Cualquier funcionalidad disponible en la aplicación Tradovate Trader también está expuesta a través de la API.

### Requisitos de Acceso
Para utilizar la API de Tradovate necesitas:

1. **Cuenta LIVE con más de $1,000 en equity**
2. **Suscripción a API Access ($25/mes)**
3. **Clave API generada**

### Recursos Oficiales
- Tutorial JavaScript: https://github.com/tradovate/example-api-js
- Guía C# API y WebSocket: https://github.com/tradovate/example-api-csharp-trading
- Guía JavaScript OAuth: https://github.com/tradovate/example-api-oauth
- FAQ y ejemplos de código: https://github.com/tradovate/example-api-faq

---

## ACCESO Y AUTENTICACIÓN

### Servidores de la API

Los dominios de los servicios de API están divididos según el servicio que proporcionan:

- **`live.tradovateapi.com`** - Funcionalidad solo para cuentas Live
- **`demo.tradovateapi.com`** - Motor de simulación
- **`md.tradovateapi.com`** - Feed de datos de mercado

### Obtener Token de Acceso

#### Usando Credenciales del Cliente

**cURL:**
```bash
curl -X POST https://demo.tradovateapi.com/v1/auth/accesstokenrequest \
     -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     -d '{
          "name": "tu_usuario_aquí",
          "password": "tu_contraseña_aquí",
          "appId": "Sample App",
          "appVersion": "1.0",
          "cid": 8,
          "deviceId": "123e4567-e89b-12d3-a456-426614174000",
          "sec": "f03741b6-f634-48d6-9308-c8fb871150c2"
         }'
```

**JavaScript:**
```javascript
const body = {
    name: "tu_usuario_aquí",
    password: "tu_contraseña_aquí",
    appId: "Sample App",
    appVersion: "1.0",
    cid: 8,
    sec: "f03741b6-f634-48d6-9308-c8fb871150c2",
    deviceId: "123e4567-e89b-12d3-a456-426614174000"
}

const response = await fetch('https://live.tradovateapi.com/v1/auth/accesstokenrequest', {
    method: 'POST',
    mode: 'cors',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    body: JSON.stringify(body)
})

const json = await response.json()
```

**Respuesta:**
```json
{
    "accessToken": "tu_token_de_acceso_aquí",
    "mdAccessToken": "tu_token_md_aquí",
    "expirationTime": "2021-06-15T15:40:30.056Z",
    "userStatus": "Active",
    "userId": 15460,
    "name": "username",
    "hasLive": true,
    "outdatedTaC": false,
    "hasFunded": true,
    "hasMarketData": true
}
```

### Autenticación de Dos Factores

Para habilitar la autenticación de dos factores, debes proporcionar tres campos especiales:

- **`deviceId`**: String único de hasta 64 caracteres que identifica permanentemente el dispositivo físico
- **`cid`**: ID de aplicación cliente proporcionado por Tradovate
- **`sec`**: Clave secreta (API key) proporcionada por Tradovate

### Uso del Token de Acceso

Una vez obtenido el token, úsalo con el esquema de autenticación "Bearer":

```javascript
const response = await fetch('https://live.tradovateapi.com/v1/account/list', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})
```

### Renovación del Token

Los tokens tienen una vida útil de **90 minutos**. Puedes extender esa vida útil llamando al endpoint de renovación:

```javascript
const renewal = await fetch('https://live.tradovateapi.com/v1/auth/renewaccesstoken', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${currentToken}`
    }
});
```

### Límites de Sesión

- **Máximo 2 sesiones concurrentes** por usuario
- Una tercera sesión cierra automáticamente la más antigua
- Cada llamada exitosa a `accessTokenRequest` inicia una nueva sesión

---

## ESTRUCTURA DE LA API

### Convenciones de la API

La API de Tradovate es una API HTTP de bajo nivel dividida en dos partes:
1. **Endpoints para consultar datos** (típicamente método `GET`)
2. **Endpoints para modificar datos** (típicamente método `POST`)

Los paths de endpoints consisten en dos partes: nombre de entidad y tipo de operación.
Ejemplo: `/account/find` o `/order/cancelorder`

### Consulta de Datos

#### Por ID
```javascript
const response = await fetch(URL + '/position/item?id=1000', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

#### Todas las Entidades
```javascript
const response = await fetch(URL + '/fill/list', {
   headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

#### Dependencias Master-Details
```javascript
const response = await fetch(URL + '/position/deps?masterid=123', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

#### Carga en Lote
```javascript
const response = await fetch(URL + '/contract/items?ids=840972%2C840944', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

### Envío de Datos

Para enviar datos, usa el método HTTP POST con datos formateados como objeto JSON:

```javascript
const body = {
    accountSpec: yourUserName,
    accountId: yourAcctId,
    action: "Buy",
    symbol: "MYMM1",
    orderQty: 1,
    orderType: "Market",
    isAutomated: true // debe ser true si no es una orden hecha directamente por un humano
}

const response = await fetch(URL + '/order/placeorder', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${myAccessToken}`,
    },
    body: JSON.stringify(body)
})
```

### Manejo de Errores

La API tiene dos caminos para pasar errores al cliente:

1. **Códigos de estado HTTP**: 404 (no disponible), 401/403 (inaccesible), 429/423 (demasiadas solicitudes)
2. **Campo `errorText`**: Violaciones de lógica de negocio en formato de texto

---

## WEBSOCKETS

### Conexión al Servidor WebSocket

La versión actual del protocolo WebSocket está heredada del protocolo SockJS. 

**URL de conexión:**
```
wss://demo.tradovateapi.com/v1/websocket
```

**Ejemplo de conexión:**
```javascript
const URL = 'wss://demo.tradovateapi.com/v1/websocket'
const myWebSocket = new WebSocket(URL)

myWebSocket.onopen = function() {
    myWebSocket.send(`authorize\n0\n\n${accessToken}`)
}
```

### Marcos del Servidor

El servidor WebSocket comunica en marcos que consisten en:
- **Carácter de prefijo de tipo**
- **Array de datos JSON**

**Tipos de marcos:**
- **`'o'`**: Marco de apertura (enviado al establecer sesión)
- **`'h'`**: Marco de heartbeat (enviado cada 2.5 segundos)
- **`'a'`**: Marco de aplicación (contiene datos de aplicación reales)
- **`'c'`**: Marco de cierre (enviado cuando se cierra la conexión)

### Decodificación de Marcos del Servidor

```javascript
function prepareMsg(raw) {
    const T = raw.slice(0, 1)
    let payload = null
    
    if (T === 'a') {
        payload = JSON.parse(raw.slice(1))
    }
    
    return [T, payload]
}
```

### Mensajes Específicos de Tradovate

#### Mensaje de Evento del Servidor
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
      "ordStatus": "PendingNew"
    }
  }
}
```

#### Mensaje de Respuesta
```json
{
  "s": 200,
  "i": 23,
  "d": {
    "id": 65543,
    "name": "CLZ6",
    "contractMaturityId": 6727
  }
}
```

### Autorización WebSocket

```javascript
myWebSocket.send(`authorize\n2\n\n${accessToken}`)

// Respuesta exitosa:
// a[{"s":200,"i":2}]
```

### Sincronización de Usuario

Para obtener datos de usuario en tiempo real:

```javascript
const requestBody = {
    users: [12345]
}

myWebSocket.send(`user/syncrequest\n1\n\n${JSON.stringify(requestBody)}`)
```

### Heartbeats del Cliente

Los clientes deben enviar heartbeats cada 2.5 segundos:

```javascript
setInterval(() => {
    if (myWebSocket.readyState === WebSocket.OPEN) {
        myWebSocket.send('[]')
    }
}, 2500)
```

---

## DATOS DE MERCADO

### Acceso a Datos de Mercado

El proceso típico para usar la API de datos de mercado:

1. **Adquirir token de acceso usando credenciales**
2. **Abrir WebSocket y autorizarse**
3. **Construir solicitud**
4. **Suscribirse a datos en tiempo real**

### Suscripción a Cotizaciones

**Endpoint:** `md/subscribeQuote`

**Parámetros:**
```json
{ "symbol": "ESM7" }
```

**Mensaje de datos:**
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

### Suscripción a DOM (Depth of Market)

**Endpoint:** `md/subscribeDOM`

**Parámetros:**
```json
{ "symbol": "ESM7" }
```

**Mensaje de datos:**
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

### Obtener Gráficos

**Endpoint:** `md/getChart`

**Parámetros:**
```json
{
  "symbol": "ESM7",
  "chartDescription": {
    "underlyingType": "MinuteBar",
    "elementSize": 15,
    "elementSizeUnit": "UnderlyingUnits",
    "withHistogram": true
  },
  "timeRange": {
    "closestTimestamp": "2017-04-13T11:33Z",
    "asMuchAsElements": 66
  }
}
```

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

### Desuscribirse de Datos de Mercado

**Endpoints de desuscripción:**
- `md/unsubscribeQuote`
- `md/unsubscribeDOM`
- `md/cancelChart`

---

## ÓRDENES

### Colocar Orden de Mercado

```javascript
const body = {
    accountSpec: yourUserName,
    accountId: yourAcctId,
    action: "Buy",
    symbol: "MYMM1",
    orderQty: 1,
    orderType: "Market",
    isAutomated: true
}

const response = await fetch(URL + '/order/placeorder', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${myAccessToken}`,
    },
    body: JSON.stringify(body)
})
```

### Colocar Orden Límite

```javascript
const body = {
    accountSpec: yourUserName,
    accountId: yourAcctId,
    action: "Sell",
    symbol: "MYMM1",
    orderQty: 1,
    orderType: "Limit",
    price: 35000,
    isAutomated: true
}
```

### Órdenes OCO (Order Cancels Order)

```javascript
const limit = {
    action: 'Sell',
    orderType: 'Limit',
    price: 4200.00
}

const oco = {
    accountSpec: yourUserName,
    accountId: yourAcctId,
    action: "Buy",
    symbol: "MESM1",
    orderQty: 1,
    orderType: "Stop",
    price: 4100.00,
    isAutomated: true,
    other: limit
}

const response = await fetch(URL + '/order/placeoco', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${myAccessToken}`,
    },
    body: JSON.stringify(oco)
})
```

### Modificar Orden

**Endpoint:** `POST /order/modifyorder`

### Cancelar Orden

**Endpoint:** `POST /order/cancelorder`

### Liquidar Posición

**Endpoint:** `POST /order/liquidateposition`

```javascript
const body = {
    accountId: myAccountId,
    contractId: contractId,
    admin: false,
    customTag50: "liquidation_tag"
}
```

---

## POSICIONES

### Obtener Posiciones por Cuenta

```javascript
const response = await fetch(URL + '/position/deps?masterid=' + accountId, {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

### Estructura de Datos de Posición

```json
{
  "id": 0,
  "accountId": 0,
  "contractId": 0,
  "timestamp": "2019-08-24T14:15:22Z",
  "tradeDate": { "year": 2019, "month": 8, "day": 24 },
  "netPos": 0,
  "netPrice": 0.1,
  "bought": 0,
  "boughtValue": 0.1,
  "sold": 0,
  "soldValue": 0.1,
  "prevPos": 0,
  "prevPrice": 0.1
}
```

---

## CONTABILIDAD

### Obtener Instantánea del Saldo de Efectivo

**Endpoint:** `POST /cashBalance/getcashbalancesnapshot`

```javascript
const body = { accountId: myAccountId }

const response = await fetch(URL + '/cashBalance/getcashbalancesnapshot', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${myAccessToken}`,
    },
    body: JSON.stringify(body)
})
```

### Restablecer Estado de Cuenta Demo

**Endpoint:** `POST /account/resetdemoaccountstate`

```javascript
const body = {
    accountIds: [accountId],
    resetTradeDate: {
        year: 2024,
        month: 1,
        day: 15
    }
}
```

### Listar Cuentas

```javascript
const response = await fetch(URL + '/account/list', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

---

## GESTIÓN DE RIESGOS

### Estado de Riesgo de la Cuenta

Tradovate auto-liquida cuentas que caen por debajo de criterios de salud establecidos. Puedes ver la política completa de liquidación en: https://tradovate.com/liquidation-policy/

**Endpoint:** `GET /accountRiskStatus/list`

### Límites de Riesgo Disponibles

- **Límites de posición** (limita cuánto puedes operar)
- **Limitaciones de producto** (limita qué puedes operar)
- **Límites de pérdida diaria/semanal**
- **Trailing max drawdown**

### Crear Límite de Posición

```javascript
const posLimitBody = {
    accountId: myAccountId,
    active: true,
    totalBy: 'Overall',
    exposedLimit: 30, // máximo contratos abiertos
    description: 'Max Position Size'
}

const posLimitRes = await fetch(URL + '/userAccountPositionLimit/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${myAccessToken}`
    },
    body: JSON.stringify(posLimitBody)
})
```

### Crear Parámetro de Riesgo

```javascript
const riskParamBody = {
    hardLimit: true,
    userAccountPositionLimitId: positionLimitId
}

const riskParamRes = await fetch(URL + '/userAccountRiskParameter/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${myAccessToken}`
    },
    body: JSON.stringify(riskParamBody)
})
```

---

## USUARIOS Y PERMISOS

### Obtener Información de Usuario

```javascript
const response = await fetch(URL + '/user/list', {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

### Crear Permiso de Trading

**Endpoint:** `POST /user/createtradingpermission`

```javascript
const body = {
    accountId: accountId,
    userId: userId
}
```

### Abrir Cuenta Demo

**Endpoint:** `POST /user/opendemoaccount`

```javascript
const body = {
    templateAccountId: 0,
    name: "Demo Account",
    initialBalance: 50000.0,
    defaultAutoLiq: {
        marginPercentageAlert: 0.8,
        dailyLossPercentageAlert: 0.05,
        dailyLossAlert: 2500.0,
        marginPercentageLiqOnly: 0.9,
        dailyLossPercentageLiqOnly: 0.1,
        dailyLossLiqOnly: 5000.0
    }
}
```

---

## CHAT Y COMUNICACIONES

### Obtener Mensajes de Chat

```javascript
const response = await fetch(URL + '/chatMessage/ldeps?masterids=' + chatId, {
    headers: {
        Authorization: `Bearer ${myAccessToken}`,
        'Content-Type': 'application/json'
    }
})
```

### Estructura de Mensaje de Chat

```json
{
  "id": 0,
  "timestamp": "2019-08-24T14:15:22Z",
  "chatId": 0,
  "senderId": 0,
  "senderName": "string",
  "text": "string",
  "readStatus": true
}
```

---

## EJEMPLOS DE IMPLEMENTACIÓN

### Ejemplo Completo: Bot de Trading Básico

```javascript
class TradovateBot {
    constructor(credentials) {
        this.credentials = credentials;
        this.accessToken = null;
        this.accountId = null;
        this.ws = null;
    }
    
    async initialize() {
        // 1. Obtener token de acceso
        await this.getAccessToken();
        
        // 2. Obtener información de cuenta
        await this.getAccountInfo();
        
        // 3. Conectar WebSocket
        await this.connectWebSocket();
        
        // 4. Sincronizar datos de usuario
        await this.syncUserData();
    }
    
    async getAccessToken() {
        const response = await fetch('https://live.tradovateapi.com/v1/auth/accesstokenrequest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(this.credentials)
        });
        
        const data = await response.json();
        this.accessToken = data.accessToken;
    }
    
    async getAccountInfo() {
        const response = await fetch('https://live.tradovateapi.com/v1/account/list', {
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        const accounts = await response.json();
        this.accountId = accounts[0].id;
    }
    
    async connectWebSocket() {
        this.ws = new WebSocket('wss://live.tradovateapi.com/v1/websocket');
        
        this.ws.onopen = () => {
            this.ws.send(`authorize\n0\n\n${this.accessToken}`);
        };
        
        this.ws.onmessage = (event) => {
            this.handleWebSocketMessage(event.data);
        };
    }
    
    async syncUserData() {
        const requestBody = {
            users: [this.userId]
        };
        
        this.ws.send(`user/syncrequest\n1\n\n${JSON.stringify(requestBody)}`);
    }
    
    async placeMarketOrder(symbol, action, quantity) {
        const body = {
            accountSpec: this.username,
            accountId: this.accountId,
            action: action,
            symbol: symbol,
            orderQty: quantity,
            orderType: "Market",
            isAutomated: true
        };
        
        const response = await fetch('https://live.tradovateapi.com/v1/order/placeorder', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Authorization': `Bearer ${this.accessToken}`,
            },
            body: JSON.stringify(body)
        });
        
        return await response.json();
    }
    
    handleWebSocketMessage(data) {
        const [frameType, payload] = this.prepareMessage(data);
        
        if (frameType === 'a' && payload) {
            payload.forEach(message => {
                if (message.e === 'props') {
                    this.handleEntityEvent(message.d);
                } else if (message.e === 'md') {
                    this.handleMarketData(message.d);
                }
            });
        }
    }
    
    prepareMessage(raw) {
        const frameType = raw.slice(0, 1);
        let payload = null;
        
        if (frameType === 'a') {
            payload = JSON.parse(raw.slice(1));
        }
        
        return [frameType, payload];
    }
}

// Uso del bot
const credentials = {
    name: "tu_usuario",
    password: "tu_contraseña",
    appId: "My Trading Bot",
    appVersion: "1.0",
    cid: 8,
    sec: "tu_api_key_aquí",
    deviceId: "unique-device-id"
};

const bot = new TradovateBot(credentials);
await bot.initialize();

// Colocar orden de compra de mercado
const result = await bot.placeMarketOrder("MESM1", "Buy", 1);
console.log("Orden colocada:", result);
```

### Configuración para Lightning 50K

```javascript
const lightningConfig = {
    // Configuración específica para estrategia Lightning 50K
    symbol: "MNQ",
    maxContracts: 3,
    riskManagement: {
        maxDailyLoss: 2500,
        maxPosition: 30,
        trailingStop: true
    },
    
    // Límites de riesgo
    positionLimits: {
        exposedLimit: 30,
        totalBy: 'Overall'
    },
    
    // Auto-liquidación
    autoLiquidation: {
        marginPercentageAlert: 80,
        dailyLossPercentageAlert: 5,
        dailyLossAlert: 2500
    }
};
```

---

## NOTAS IMPORTANTES

### Límites y Restricciones

1. **Sesiones Concurrentes**: Máximo 2 sesiones activas por usuario
2. **Vida Útil del Token**: 90 minutos (renovable)
3. **Rate Limits**: Aplicables según el tipo de endpoint
4. **Heartbeats**: Requeridos cada 2.5 segundos en WebSocket

### Mejores Prácticas

1. **Usar `user/syncrequest`** para datos de usuario en tiempo real
2. **Limpiar suscripciones** de datos de mercado cuando no las necesites
3. **Renovar tokens** antes de que expiren
4. **Manejar reconexiones** WebSocket automáticamente
5. **Implementar logging** robusto para debugging

### Seguridad

1. **Mantener API keys secretas** - no las incluyas en repositorios públicos
2. **Usar autenticación de dos factores** siempre
3. **Implementar `deviceId` único** para cada instalación
4. **Validar todas las respuestas** de la API

---

**Fin de la Documentación Completa**

> Esta documentación está basada en la fuente oficial de Tradovate API (v1.0.0) obtenida de https://api.tradovate.com/ el 31 de enero de 2025. Para actualizaciones y información adicional, consulta la documentación oficial y los repositorios de ejemplo en GitHub.
