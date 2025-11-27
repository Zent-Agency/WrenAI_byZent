# 📋 RESUMEN DE CAMBIOS - SOLUCIÓN THREAD_ID

## 🎯 PROBLEMA ORIGINAL
❌ No podías obtener el `thread_id` aunque conseguías el `query_id`
❌ El webhook no mantenía el contexto entre preguntas

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. **Webhook Mejorado** (`webhook_server.py`)
El webhook ahora:
- ✅ **Automáticamente crea un `thread_id` por usuario**
- ✅ **Reutiliza el mismo thread para mantener contexto**
- ✅ **Persiste threads en `threads_storage.json`**
- ✅ **Devuelve el `thread_id` en cada respuesta**

**Cambios principales:**
```python
# Ahora el webhook requiere user_id (importante!)
{
  "message": "tu pregunta",
  "user_id": "identificador_unico"  # 👈 REQUERIDO
}

# Y devuelve el thread_id
{
  "status": "success",
  "thread_id": "7a8b9c0d...",  # 👈 AQUÍ ESTÁ
  "query": "...",
  "answer": "..."
}
```

### 2. **Script de Gestión de Threads** (`get_thread_id.py`)
Herramienta completa para:
- ✅ Crear threads
- ✅ Obtener threads existentes
- ✅ Hacer preguntas manteniendo conversación
- ✅ Listar y eliminar threads

**Uso:**
```bash
# Crear thread
python get_thread_id.py create usuario_123 7 deploy_id

# Obtener thread
python get_thread_id.py get usuario_123

# Hacer pregunta
python get_thread_id.py ask usuario_123 7 deploy_id "¿Qué vinos tengo?"

# Listar todos
python get_thread_id.py list
```

### 3. **Scripts de Prueba Actualizados** (`test_webhook.py`)
Nuevas funciones:
- ✅ Prueba de conversación completa
- ✅ Listado de threads activos
- ✅ Obtención de thread por usuario

**Uso:**
```bash
# Prueba completa
python test_webhook.py conversation

# Ver threads
python test_webhook.py threads

# Obtener thread de usuario
python test_webhook.py get-thread usuario_123
```

### 4. **Client Mejorado** (`wren_client.py`)
- ✅ Captura el `thread_id` desde la respuesta de WrenAI
- ✅ Lo almacena en `self.last_thread_id` para reutilización

### 5. **Nuevos Endpoints del Webhook**
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/webhook` | POST | Enviar pregunta (ahora con thread_id) |
| `/webhook/threads` | GET | Ver todos los threads |
| `/webhook/threads/<user_id>` | GET | Obtener thread de un usuario |
| `/webhook/threads/<user_id>` | DELETE | Eliminar thread de un usuario |
| `/health` | GET | Estado del servidor (mejorado) |

### 6. **Documentación Completa** (`OBTENER_THREAD_ID.md`)
- ✅ Explicación de qué es thread_id
- ✅ 3 métodos diferentes para obtenerlo
- ✅ Ejemplos en Python, JavaScript, cURL
- ✅ Guía de troubleshooting
- ✅ Casos de uso completos

---

## 🚀 FLUJO DE USO RECOMENDADO

### Opción 1: Automático (FÁCIL)
```bash
# El webhook crea y gestiona automáticamente
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué vinos tengo?",
    "user_id": "usuario_123"
  }'

# Respuesta incluye thread_id
# {
#   "status": "success",
#   "thread_id": "abc123...",
#   ...
# }
```

### Opción 2: Con Script (RECOMENDADO)
```bash
# Crear thread
python get_thread_id.py create usuario_123 7 deploy_id

# Obtener thread_id devuelto
# Thread ID: 7a8b9c0d1e2f3a4b5c6d7e8f

# Usar en preguntas
python get_thread_id.py ask usuario_123 7 deploy_id "¿Qué vinos hay?"
```

### Opción 3: Directa (AVANZADO)
```python
client = WrenAIClient(...)
response = client.ask_question("Primera pregunta")
thread_id = response.get("thread_id")

# Reutilizar en siguientes preguntas
response2 = client.ask_question(
    "Segunda pregunta",
    thread_id=thread_id
)
```

---

## 📁 ARCHIVOS CREADOS/MODIFICADOS

### Creados:
- ✅ `get_thread_id.py` - Gestor de threads
- ✅ `OBTENER_THREAD_ID.md` - Documentación completa
- ✅ `quick_test.sh` - Script de prueba rápida
- ✅ `RESUMEN_CAMBIOS.md` - Este archivo

### Modificados:
- ✅ `webhook_server.py` - Gestión automática de threads
- ✅ `wren_client.py` - Captura de thread_id
- ✅ `test_webhook.py` - Nuevas funciones de prueba

---

## 🧪 PRUEBAS RÁPIDAS

### Verificar que funciona:
```bash
# 1. Prueba rápida completa
bash quick_test.sh

# 2. Prueba conversación
python test_webhook.py conversation

# 3. Ver threads almacenados
python test_webhook.py threads

# 4. Obtener thread específico
python test_webhook.py get-thread usuario_123
```

---

## 💾 PERSISTENCIA DE THREADS

Los threads se guardan en: **`threads_storage.json`**

```json
{
  "usuario_123": {
    "thread_id": "7a8b9c0d1e2f3a4b5c6d7e8f",
    "project_id": "7",
    "deploy_id": "707d0c244de6313b67bd9bdb0d0504d70a70fff6",
    "created_at": "2024-11-27T10:30:00",
    "messages_count": 5,
    "last_message": "2024-11-27T10:35:00"
  }
}
```

**Beneficios:**
- ✅ Conversaciones persisten entre reinicios
- ✅ Múltiples usuarios simultáneos
- ✅ Fácil de compartir entre servidores
- ✅ Backup y auditoría disponibles

---

## ✨ VENTAJAS DE ESTA SOLUCIÓN

1. **Automática**: No necesitas generar manualmente thread_ids
2. **Persistente**: Los threads se guardan y reutilizan
3. **Por Usuario**: Cada usuario tiene su propia conversación
4. **Flexible**: 3 formas diferentes de usarla
5. **Escalable**: Maneja múltiples usuarios simultáneos
6. **Documentada**: Guías completas y ejemplos
7. **Testeable**: Scripts incluidos para probar todo

---

## 🔄 MIGRACIÓN DESDE CÓDIGO ANTIGUO

Si tenías código anterior:

**Antes:**
```python
payload = {
    "message": "pregunta",
    "user_id": "unknown"  # No importaba
}
```

**Ahora:**
```python
payload = {
    "message": "pregunta",
    "user_id": "usuario_123"  # ✅ REQUERIDO e importante
}
```

**Ventaja:** El mismo `user_id` reutiliza el `thread_id` automáticamente.

---

## 🆘 TROUBLESHOOTING

| Problema | Solución |
|----------|----------|
| "user_id is required" | Incluye `user_id` en cada petición |
| No se recibe `thread_id` | Verifica que WrenAI esté corriendo |
| Conversación no mantiene contexto | Verifica que uses el mismo `thread_id` |
| Threads file corrupted | Elimina `threads_storage.json` y reinicia |

---

## 📞 SOPORTE

Consulta:
1. `OBTENER_THREAD_ID.md` - Documentación completa
2. `python get_thread_id.py help` - Ayuda del script
3. `python test_webhook.py conversation` - Prueba funcional
4. Logs del servidor: `docker logs wren-ui`

---

**✅ ¡Tu webhook ahora soporta conversaciones persistentes con thread_id!**
