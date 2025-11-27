# Guía de Uso del Webhook de WrenAI

Esta guía te explica cómo usar el webhook para integrar WrenAI con WhatsApp u otros servicios de mensajería.

## 📋 Requisitos

```bash
pip install flask requests
```

## 🚀 Inicio Rápido

### 1. Obtener el Project ID

Primero, necesitas obtener el `project_id` desde la UI de WrenAI:

1. Abre http://localhost:4000
2. Configura tu base de datos (si aún no lo has hecho)
3. Abre las DevTools del navegador (F12)
4. Ve a la pestaña "Network"
5. Haz una pregunta en la UI
6. Busca la petición a `/v1/asks`
7. En el payload verás el `project_id`

### 2. Configurar el Project ID

```bash
export WREN_PROJECT_ID="tu-project-id-aqui"
```

### 3. Iniciar el Servidor Webhook

```bash
cd examples/webhook
python webhook_server.py
```

El servidor estará disponible en:
- **Webhook**: http://localhost:5000/webhook
- **Health Check**: http://localhost:5000/health
- **Test**: http://localhost:5000/webhook/test

### 4. Probar el Webhook

En otra terminal:

```bash
cd examples/webhook
python test_webhook.py "¿Cuántos pedidos tenemos este mes?"
```

## 📡 API del Webhook

### POST /webhook

Envía un mensaje y recibe una respuesta procesada por WrenAI.

**Request:**
```json
{
  "message": "¿Cuál es el producto más vendido?",
  "user_id": "opcional-id-usuario",
  "project_id": "opcional-si-ya-lo-configuraste"
}
```

**Response (éxito):**
```json
{
  "status": "success",
  "query": "¿Cuál es el producto más vendido?",
  "sql": "SELECT producto, COUNT(*) as ventas FROM pedidos GROUP BY producto ORDER BY ventas DESC LIMIT 1",
  "answer": "He generado la siguiente consulta SQL:\n\n```sql\nSELECT...\n```",
  "wren_status": "finished",
  "raw_response": {...}
}
```

**Response (error):**
```json
{
  "status": "error",
  "query": "pregunta original",
  "message": "Descripción del error",
  "raw_response": {...}
}
```

## 🔗 Integración con WhatsApp

### Opción 1: Twilio

```python
from twilio.rest import Client
import requests

def handle_whatsapp_message(from_number, message_body):
    # Enviar al webhook
    response = requests.post(
        "http://localhost:5000/webhook",
        json={"message": message_body, "user_id": from_number}
    )
    
    result = response.json()
    
    # Enviar respuesta por WhatsApp
    client = Client(account_sid, auth_token)
    client.messages.create(
        from_='whatsapp:+14155238886',
        body=result.get('answer'),
        to=from_number
    )
```

### Opción 2: WhatsApp Business API

```python
import requests

def send_to_whatsapp(phone_number, message):
    # Tu lógica de WhatsApp Business API
    url = "https://graph.facebook.com/v17.0/YOUR_PHONE_ID/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

# En tu webhook de WhatsApp
@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    phone = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    
    # Procesar con WrenAI
    wren_response = requests.post(
        "http://localhost:5000/webhook",
        json={"message": message, "user_id": phone}
    ).json()
    
    # Responder por WhatsApp
    send_to_whatsapp(phone, wren_response.get('answer'))
    
    return jsonify({"status": "ok"})
```

## 🧪 Pruebas con cURL

```bash
# Prueba básica
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos pedidos tenemos?"}'

# Con project_id específico
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuál es el cliente con más compras?",
    "project_id": "tu-project-id",
    "user_id": "test_user"
  }'

# Health check
curl http://localhost:5000/health
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# URL del servicio de WrenAI
export WREN_AI_URL="http://localhost:5555"

# Project ID por defecto
export WREN_PROJECT_ID="tu-project-id"

# Puerto del webhook
export WEBHOOK_PORT=5000
```

### Ejecutar en Producción

Para producción, usa un servidor WSGI como Gunicorn:

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 webhook_server:app
```

## 📊 Flujo Completo

```
Usuario (WhatsApp)
    ↓
    📱 Envía mensaje
    ↓
Webhook de WhatsApp
    ↓
    🔗 POST /webhook
    ↓
Webhook Server (webhook_server.py)
    ↓
    🤖 Procesa con WrenAI
    ↓
WrenAI Service (localhost:5555)
    ↓
    📊 Genera SQL y respuesta
    ↓
Webhook Server
    ↓
    📤 Devuelve respuesta
    ↓
Webhook de WhatsApp
    ↓
    💬 Envía respuesta al usuario
    ↓
Usuario (WhatsApp)
```

## 🎯 Casos de Uso

1. **Bot de WhatsApp para consultas de negocio**
2. **Asistente de Telegram para análisis de datos**
3. **Integración con Slack para reportes**
4. **API pública para consultas de datos**
5. **Chatbot web personalizado**

## 🐛 Troubleshooting

### El webhook no responde
- Verifica que el servidor esté corriendo: `curl http://localhost:5000/health`
- Revisa los logs del servidor

### Error de conexión a WrenAI
- Verifica que WrenAI esté corriendo: `docker-compose ps`
- Verifica la URL: `echo $WREN_AI_URL`

### No se genera SQL
- Asegúrate de tener configurado el `project_id`
- Verifica que la base de datos esté conectada en la UI
- Revisa que la pregunta sea clara y relacionada con tus datos

## 📚 Recursos

- [Documentación de WrenAI](https://docs.getwren.ai)
- [API de WhatsApp Business](https://developers.facebook.com/docs/whatsapp)
- [Twilio WhatsApp](https://www.twilio.com/docs/whatsapp)
