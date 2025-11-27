# 🧵 Cómo Obtener y Usar Thread ID en WrenAI

## ¿QUÉ ES UN THREAD_ID?

Un **Thread ID** es:
- ✅ Identificador de una **CONVERSACIÓN completa**
- ✅ Se mantiene **constante** durante toda la sesión
- ✅ Permite mantener el **contexto** entre múltiples preguntas
- ✅ Es **persistente** (dura toda la conversación)

**Ejemplos:**
- `"4"` (simple)
- `"abc123-def456-ghi789"` (formato UUID)
- `"conversation_user_123_2024"` (formato descriptivo)

---

## 🚀 MÉTODOS PARA OBTENER THREAD_ID

### Método 1: Automático con el Webhook (RECOMENDADO)

El webhook ahora crea y gestiona automáticamente los thread IDs por usuario.

#### Paso 1: Envía tu primera pregunta

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué vinos malbec tengo en stock?",
    "user_id": "usuario_123"
  }'
```

**Respuesta:**
```json
{
  "status": "success",
  "query": "¿Qué vinos malbec tengo en stock?",
  "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f",
  "sql": "SELECT * FROM wines WHERE type='malbec' AND stock > 0",
  "answer": "He generado la siguiente consulta SQL..."
}
```

#### Paso 2: Obtén el `thread_id` de la respuesta

El webhook devuelve automáticamente el `thread_id` en cada respuesta.

#### Paso 3: Reutiliza el mismo `thread_id` para la siguiente pregunta

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuál es el más caro?",
    "user_id": "usuario_123",
    "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f"
  }'
```

**Ventaja:** La IA mantiene el contexto de tu pregunta anterior.

---

### Método 2: Con Script Python `get_thread_id.py`

Tenemos un script dedicado para gestionar threads:

#### Ver ayuda completa:
```bash
python get_thread_id.py help
```

#### Crear un nuevo thread:
```bash
python get_thread_id.py create usuario_123 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6
```

**Salida:**
```
✅ Thread creado exitosamente!
   User ID: usuario_123
   Thread ID: 7a8b9c0d1e2f3a4b5c6d7e8f
   Query ID: abc123def456
```

#### Obtener thread existente:
```bash
python get_thread_id.py get usuario_123
```

#### Hacer pregunta con thread:
```bash
python get_thread_id.py ask usuario_123 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6 "¿Cuántos vinos hay?"
```

---

### Método 3: Directamente desde la API de WrenAI

Si trabajas directamente con la API sin el webhook:

```python
from wren_client import WrenAIClient

client = WrenAIClient(
    base_url="http://localhost:5555",
    project_id="7",
    deploy_id="707d0c244de6313b67bd9bdb0d0504d70a70fff6"
)

# Primera pregunta (crea un nuevo thread)
response = client.ask_question("¿Qué vinos tengo?")
thread_id = response.get("thread_id")  # 👈 AQUÍ OBTIENES EL THREAD_ID

print(f"Thread ID: {thread_id}")

# Segunda pregunta (reutiliza el mismo thread)
response2 = client.ask_question(
    "¿Cuál es el más caro?",
    thread_id=thread_id  # 👈 PASA EL THREAD_ID
)
```

---

## 📊 CONSULTAS ÚTILES DEL WEBHOOK

### Ver todos los threads activos:
```bash
curl http://localhost:5000/webhook/threads
```

**Respuesta:**
```json
{
  "status": "ok",
  "total_threads": 2,
  "threads": {
    "usuario_123": {
      "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f",
      "messages_count": 5,
      "created_at": "2024-11-27T10:30:00"
    },
    "usuario_456": {
      "thread_id": "9f0e1d2c3b4a5968778695a4",
      "messages_count": 2,
      "created_at": "2024-11-27T11:00:00"
    }
  }
}
```

### Obtener thread específico de un usuario:
```bash
curl http://localhost:5000/webhook/threads/usuario_123
```

**Respuesta:**
```json
{
  "status": "ok",
  "user_id": "usuario_123",
  "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f",
  "messages_count": 5,
  "created_at": "2024-11-27T10:30:00"
}
```

### Eliminar un thread:
```bash
curl -X DELETE http://localhost:5000/webhook/threads/usuario_123
```

---

## 🧪 PRUEBA RÁPIDA: CONVERSACIÓN COMPLETA

### Prueba automática (con Python):
```bash
python test_webhook.py conversation
```

Esto ejecuta:
1. Primera pregunta: "¿Qué vinos malbec tengo en stock?"
2. Segunda pregunta: "¿Cuál es el más caro?"
3. Tercera pregunta: "¿Cuántas botellas hay?"

Todas mantienen el mismo `thread_id`.

### Prueba manual (con curl):

**Pregunta 1:**
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":"¿Qué vinos malbec tengo?","user_id":"test1"}'
```

Copia el `thread_id` de la respuesta (ej: `abc123`)

**Pregunta 2:**
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":"¿Cuál es el más vendido?","user_id":"test1","thread_id":"abc123"}'
```

---

## 🔧 ALMACENAMIENTO DE THREADS

Los threads se guardan en: **`threads_storage.json`**

Contenido ejemplo:
```json
{
  "usuario_123": {
    "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f",
    "project_id": "7",
    "deploy_id": "707d0c244de6313b67bd9bdb0d0504d70a70fff6",
    "created_at": "2024-11-27T10:30:00.123456",
    "messages_count": 5,
    "last_message": "2024-11-27T10:35:00.123456"
  }
}
```

Puedes:
- ✅ Editarlo manualmente
- ✅ Compartirlo entre servidores
- ✅ Hacer backup de conversaciones

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

### Error: "El campo 'user_id' es requerido"
```json
{
  "status": "error",
  "message": "El campo 'user_id' es requerido para mantener la conversación"
}
```

**Solución:** Siempre incluye `user_id` en tus peticiones:
```json
{
  "message": "tu pregunta",
  "user_id": "identificador_unico"
}
```

---

### Error: "No se recibió thread_id"
```json
{
  "status": "error",
  "message": "No se recibió thread_id en la respuesta"
}
```

**Soluciones:**
1. Verifica que WrenAI esté corriendo en `http://localhost:5555`
2. Verifica que el `project_id` y `deploy_id` sean correctos
3. Consulta los logs del servidor con:
   ```bash
   docker logs -f wren_ai_service
   ```

---

### Error: "Timeout esperando resultado"
```json
{
  "status": "error",
  "message": "Timeout esperando resultado",
  "status": "timeout"
}
```

**Soluciones:**
1. Aumenta el timeout en el webhook (por defecto 120s):
   ```bash
   # Edita webhook_server.py, línea de ask_and_wait
   timeout=300  # 5 minutos
   ```
2. Verifica que WrenAI no esté sobrecargado
3. Intenta con preguntas más simples primero

---

## 💡 EJEMPLOS COMPLETOS

### JavaScript/Node.js:
```javascript
const axios = require('axios');

async function askWithThread() {
  const userId = 'usuario_123';
  let threadId = null;
  
  // Primera pregunta
  const response1 = await axios.post('http://localhost:5000/webhook', {
    message: '¿Qué vinos tengo?',
    user_id: userId
  });
  
  threadId = response1.data.thread_id;
  console.log('Thread ID:', threadId);
  
  // Segunda pregunta (reutiliza thread)
  const response2 = await axios.post('http://localhost:5000/webhook', {
    message: '¿Cuál es el más caro?',
    user_id: userId,
    thread_id: threadId
  });
  
  console.log('Respuesta:', response2.data.answer);
}

askWithThread();
```

### Python (requests):
```python
import requests

def ask_with_thread():
    webhook_url = 'http://localhost:5000/webhook'
    user_id = 'usuario_123'
    
    # Primera pregunta
    response1 = requests.post(webhook_url, json={
        'message': '¿Qué vinos tengo?',
        'user_id': user_id
    })
    
    thread_id = response1.json()['thread_id']
    print(f'Thread ID: {thread_id}')
    
    # Segunda pregunta (reutiliza thread)
    response2 = requests.post(webhook_url, json={
        'message': '¿Cuál es el más caro?',
        'user_id': user_id,
        'thread_id': thread_id
    })
    
    print('Respuesta:', response2.json()['answer'])

ask_with_thread()
```

### cURL (Bash):
```bash
#!/bin/bash

USER_ID="usuario_123"
WEBHOOK_URL="http://localhost:5000/webhook"

# Primera pregunta
RESPONSE1=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"¿Qué vinos tengo?\",
    \"user_id\": \"$USER_ID\"
  }")

THREAD_ID=$(echo "$RESPONSE1" | jq -r '.thread_id')
echo "Thread ID: $THREAD_ID"

# Segunda pregunta (reutiliza thread)
curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"¿Cuál es el más caro?\",
    \"user_id\": \"$USER_ID\",
    \"thread_id\": \"$THREAD_ID\"
  }" | jq '.answer'
```

---

## 🎯 RESUMEN RÁPIDO

| Tarea | Comando |
|-------|---------|
| **Crear thread** | `python get_thread_id.py create usuario_123 7 deploy_id` |
| **Obtener thread** | `curl http://localhost:5000/webhook/threads/usuario_123` |
| **Ver todos threads** | `curl http://localhost:5000/webhook/threads` |
| **Hacer pregunta** | `curl -X POST http://localhost:5000/webhook -d '{"message":"...","user_id":"...","thread_id":"..."}'` |
| **Prueba conversación** | `python test_webhook.py conversation` |
| **Listar threads Python** | `python test_webhook.py threads` |

---

## 🆘 NECESITAS AYUDA?

1. **Verifica los logs:**
   ```bash
   tail -f /root/wren_ai/examples/webhook/threads_storage.json
   ```

2. **Prueba la salud del webhook:**
   ```bash
   curl http://localhost:5000/health
   ```

3. **Prueba la conexión a WrenAI:**
   ```bash
   curl http://localhost:5555/health
   ```

4. **Ejecuta la prueba completa:**
   ```bash
   python test_webhook.py conversation
   ```

---

**✅ ¡Ahora estás listo para mantener conversaciones persistentes con WrenAI usando Thread IDs!**
