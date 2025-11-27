# 🧵 WrenAI Webhook - Solución Thread ID

Solución completa para **obtener y usar `thread_id`** en conversaciones persistentes con WrenAI.

---

## 📋 Contenido

- [¿Qué es un Thread ID?](#qué-es-un-thread-id)
- [Inicio Rápido](#inicio-rápido)
- [Métodos para Obtener Thread ID](#métodos-para-obtener-thread-id)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Archivos Incluidos](#archivos-incluidos)
- [Troubleshooting](#troubleshooting)

---

## ¿Qué es un Thread ID?

Un **Thread ID** es:
- ✅ Identificador de una **conversación completa**
- ✅ Se mantiene **constante** durante toda la sesión
- ✅ Permite mantener **contexto** entre preguntas
- ✅ Es **persistente** (dura toda la conversación)

**Ejemplo:**
```
Pregunta 1: "¿Qué vinos malbec tengo?"
Thread ID: abc123xyz

Pregunta 2: "¿Cuál es el más caro?"  ← Usa MISMO thread → IA recuerda contexto
Thread ID: abc123xyz
```

---

## 🚀 Inicio Rápido

### 1. Prueba en 30 segundos

```bash
# Ejecuta el script de prueba completo
bash quick_test.sh
```

Este script:
1. ✅ Hace 3 preguntas seguidas
2. ✅ Mantiene el mismo `thread_id`
3. ✅ Muestra cómo se persiste el contexto
4. ✅ Lista todos los threads almacenados

### 2. Inicio del Servidor

```bash
# Terminal 1: Asume que WrenAI está corriendo en http://localhost:5555
python webhook_server.py

# Salida:
# 🚀 Servidor Webhook iniciado
# 📍 URL: http://localhost:5000
# 🤖 WrenAI URL: http://localhost:5555
```

### 3. Envía tu Primera Pregunta

```bash
# Terminal 2: Envía una pregunta
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué vinos malbec tengo en stock?",
    "user_id": "usuario_123"
  }'

# Respuesta (¡nótese el thread_id!):
# {
#   "status": "success",
#   "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f",
#   "query": "¿Qué vinos malbec tengo en stock?",
#   "answer": "He generado la siguiente consulta SQL..."
# }
```

### 4. Reutiliza el Thread ID

```bash
# Usa el MISMO thread_id para mantener contexto
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuál es el más caro?",
    "user_id": "usuario_123",
    "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f"
  }'

# ✅ La IA recuerda que estamos hablando de vinos malbec
```

---

## 📖 Métodos para Obtener Thread ID

### Método 1: Automático (RECOMENDADO)

El webhook **automáticamente**:
1. Crea un `thread_id` para cada usuario
2. Lo devuelve en la respuesta
3. Lo reutiliza automáticamente si usas el mismo `user_id`

```bash
# Simplemente envía una pregunta con user_id
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué vinos tengo?",
    "user_id": "usuario_123"
  }'

# El webhook automáticamente:
# - Crea thread si es primera vez
# - Devuelve el thread_id en la respuesta
# - Lo guarda en threads_storage.json
```

### Método 2: Script Python

Script dedicado para gestionar threads:

```bash
# Crear nuevo thread
python get_thread_id.py create usuario_123 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6

# Obtener thread existente
python get_thread_id.py get usuario_123

# Hacer pregunta con thread
python get_thread_id.py ask usuario_123 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6 "¿Cuántos vinos?"

# Listar todos los threads
python get_thread_id.py list

# Ver ayuda completa
python get_thread_id.py help
```

### Método 3: Directa desde API

Directamente desde tu código:

```python
from wren_client import WrenAIClient

client = WrenAIClient(
    base_url="http://localhost:5555",
    project_id="7",
    deploy_id="707d0c244de6313b67bd9bdb0d0504d70a70fff6"
)

# Primera pregunta (obtiene thread_id)
response = client.ask_question("¿Qué vinos tengo?")
thread_id = response.get("thread_id")  # 👈 AQUÍ

print(f"Thread ID: {thread_id}")

# Segunda pregunta (reutiliza thread)
response2 = client.ask_question(
    "¿Cuál es el más caro?",
    thread_id=thread_id  # 👈 PASA EL THREAD
)
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Conversación Completa (cURL)

```bash
#!/bin/bash

# Variables
WEBHOOK="http://localhost:5000/webhook"
USER="usuario_123"

# Pregunta 1: Obtener thread_id
echo "1️⃣ Primera pregunta..."
RESPONSE1=$(curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"¿Qué vinos tengo?\",\"user_id\":\"$USER\"}")

THREAD_ID=$(echo "$RESPONSE1" | jq -r '.thread_id')
echo "Thread ID: $THREAD_ID"

# Pregunta 2: Reutilizar thread_id
echo "2️⃣ Segunda pregunta..."
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"¿Cuál es el más caro?\",\"user_id\":\"$USER\",\"thread_id\":\"$THREAD_ID\"}" | jq '.answer'

# Pregunta 3: Continuar conversación
echo "3️⃣ Tercera pregunta..."
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"¿Cuántas botellas hay?\",\"user_id\":\"$USER\",\"thread_id\":\"$THREAD_ID\"}" | jq '.answer'
```

### Ejemplo 2: Python

```python
import requests

webhook = "http://localhost:5000/webhook"
user_id = "usuario_123"

def ask_question(message, thread_id=None):
    payload = {
        "message": message,
        "user_id": user_id,
    }
    if thread_id:
        payload["thread_id"] = thread_id
    
    response = requests.post(webhook, json=payload)
    return response.json()

# Primera pregunta
r1 = ask_question("¿Qué vinos tengo?")
thread_id = r1["thread_id"]
print(f"Thread: {thread_id}")

# Segunda pregunta (con thread)
r2 = ask_question("¿Cuál es el más caro?", thread_id=thread_id)
print(f"Respuesta: {r2['answer']}")

# Tercera pregunta (con thread)
r3 = ask_question("¿Cuántas botellas?", thread_id=thread_id)
print(f"Respuesta: {r3['answer']}")
```

### Ejemplo 3: Prueba Python Incluida

```bash
# Prueba completa de conversación
python test_webhook.py conversation

# Listar todos los threads
python test_webhook.py threads

# Obtener thread de usuario
python test_webhook.py get-thread usuario_123
```

---

## 📁 Archivos Incluidos

| Archivo | Descripción |
|---------|-------------|
| **webhook_server.py** | Servidor webhook (MODIFICADO) |
| **wren_client.py** | Cliente de WrenAI (MODIFICADO) |
| **test_webhook.py** | Tests del webhook (MEJORADO) |
| **get_thread_id.py** | 🆕 Gestor de threads |
| **OBTENER_THREAD_ID.md** | 🆕 Documentación completa |
| **quick_test.sh** | 🆕 Prueba rápida en 30s |
| **config_example.sh** | 🆕 Configuración de ejemplo |
| **RESUMEN_CAMBIOS.md** | 🆕 Cambios implementados |
| **README.md** | Este archivo |
| **threads_storage.json** | 🆕 Almacenamiento de threads (auto-creado) |

### 🆕 Nuevos Endpoints del Webhook

```
POST   /webhook                    → Enviar pregunta
GET    /webhook/threads            → Ver todos los threads
GET    /webhook/threads/<user_id>  → Obtener thread de usuario
DELETE /webhook/threads/<user_id>  → Eliminar thread
GET    /health                     → Estado del servidor
```

---

## 🔧 Configuración

Edita `webhook_server.py` o define variables de entorno:

```bash
# Antes de iniciar
export WREN_AI_URL="http://localhost:5555"
export WREN_PROJECT_ID="7"
export WREN_DEPLOY_ID="707d0c244de6313b67bd9bdb0d0504d70a70fff6"
export WEBHOOK_PORT="5000"

# Luego inicia
python webhook_server.py
```

---

## 🧪 Pruebas

### Verificar que funciona

```bash
# 1. Prueba rápida (30 segundos)
bash quick_test.sh

# 2. Conversación completa
python test_webhook.py conversation

# 3. Ver threads almacenados
cat threads_storage.json
```

### Health Check

```bash
# Estado del webhook
curl http://localhost:5000/health

# Debe responder:
# {
#   "status": "ok",
#   "wren_ai_url": "http://localhost:5555",
#   "project_id_configured": true,
#   "active_threads": 2
# }
```

---

## 💾 Almacenamiento de Threads

Todos los threads se guardan en **`threads_storage.json`**:

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

**Beneficios:**
- ✅ Conversaciones persisten entre reinicios
- ✅ Múltiples usuarios simultáneos
- ✅ Fácil backup y auditoría
- ✅ Compartible entre servidores

---

## 🐛 Troubleshooting

### Error: "user_id is required"

```json
{
  "status": "error",
  "message": "El campo 'user_id' es requerido para mantener la conversación"
}
```

**Solución:** Siempre incluye `user_id`:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "tu pregunta",
    "user_id": "tu_id"  # 👈 REQUERIDO
  }'
```

---

### Error: "No se recibió thread_id"

**Soluciones:**
1. Verifica que WrenAI esté corriendo:
   ```bash
   curl http://localhost:5555/health
   ```

2. Verifica `project_id` y `deploy_id`:
   ```bash
   curl -X GET http://localhost:5555/health
   ```

3. Mira los logs:
   ```bash
   python webhook_server.py  # Inicia en modo debug
   ```

---

### Error: "Timeout esperando resultado"

**Soluciones:**
1. Aumenta el timeout en `webhook_server.py`:
   ```python
   timeout=300  # 5 minutos en lugar de 120
   ```

2. Verifica que WrenAI no esté sobrecargado

3. Intenta preguntas más simples

---

### Threads Corruptos

```bash
# Elimina el archivo de threads
rm threads_storage.json

# Se recreará automáticamente en el siguiente uso
```

---

## 📚 Documentación Adicional

- **OBTENER_THREAD_ID.md** - Guía completa detallada
- **RESUMEN_CAMBIOS.md** - Cambios técnicos implementados
- **config_example.sh** - Variables de configuración

---

## 🆘 Necesitas Ayuda?

1. Lee la documentación completa:
   ```bash
   cat OBTENER_THREAD_ID.md
   ```

2. Ejecuta la prueba rápida:
   ```bash
   bash quick_test.sh
   ```

3. Ve los threads almacenados:
   ```bash
   python get_thread_id.py list
   ```

4. Consulta la ayuda del script:
   ```bash
   python get_thread_id.py help
   ```

---

## ✨ Características Principales

- ✅ **Automático**: Crea y gestiona threads sin intervención
- ✅ **Persistente**: Los threads se guardan entre sesiones
- ✅ **Por Usuario**: Cada usuario tiene su propia conversación
- ✅ **Flexible**: 3 formas diferentes de usar
- ✅ **Escalable**: Maneja múltiples usuarios
- ✅ **Documentado**: Guías y ejemplos completos
- ✅ **Testeable**: Scripts de prueba incluidos
- ✅ **API**: Endpoints REST para gestionar threads

---

## 🎯 Próximos Pasos

1. Ejecuta `bash quick_test.sh` para ver funcionar todo
2. Lee `OBTENER_THREAD_ID.md` para entender mejor
3. Integra en tu aplicación usando los ejemplos
4. ¡Disfruta de conversaciones persistentes con contexto! 🎉

---

**✅ ¡Tu webhook está listo para mantener conversaciones con contexto!**
