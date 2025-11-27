# 🔍 Diagnóstico: Por qué la UI funciona pero el Webhook no

## El Problema

Cuando usas la **UI de WrenAI** (http://localhost:4000), las preguntas funcionan perfectamente. Sin embargo, cuando usas el **webhook** o la **API directamente**, obtienes el error:

```
"NO_RELEVANT_DATA" - No relevant data
```

O el estado se queda en `"understanding"` indefinidamente.

## La Causa

El problema está en cómo WrenAI recupera las tablas relevantes del esquema. Cuando analizamos los logs:

```
I1127 14:14:18.481 10 wren-ai-service:208] dbschema_retrieval with table_names: []
```

**`table_names` está vacío** - WrenAI no está encontrando las tablas relevantes para tu pregunta.

### ¿Por qué funciona en la UI?

La UI de WrenAI mantiene un **contexto de conversación** a través de `thread_id`. Cuando haces preguntas en la UI:

1. La UI crea un thread (conversación)
2. Ese thread tiene contexto sobre qué tablas y datos están disponibles
3. Las preguntas subsecuentes usan ese contexto

### ¿Por qué no funciona en el webhook?

Cuando llamas a la API directamente (o a través del webhook):

1. Cada llamada es independiente (sin contexto previo)
2. WrenAI intenta inferir qué tablas son relevantes basándose solo en la pregunta
3. Si la pregunta no coincide exactamente con los nombres de las tablas/columnas, falla

## Las Soluciones

### ✅ Solución 1: Usar el thread_id de la UI (Recomendado para pruebas)

1. **Obtén un thread_id válido de la UI:**
   - Abre http://localhost:4000
   - Abre DevTools (F12) > pestaña Network
   - Haz una pregunta en la UI
   - Busca la petición `POST /v1/asks`
   - Copia el `thread_id` del payload

2. **Usa ese thread_id en el webhook:**
   ```bash
   python test_with_ui_thread.py "THREAD_ID_AQUI" "¿Cuántos malbec tengo?"
   ```

3. **O envíalo directamente al webhook:**
   ```bash
   curl -X POST http://localhost:5001/webhook \
     -H "Content-Type: application/json" \
     -d '{
       "message": "¿Cuántos malbec tengo?",
       "thread_id": "THREAD_ID_DE_LA_UI",
       "user_id": "test_user"
     }'
   ```

### ✅ Solución 2: Mejorar las preguntas para incluir nombres exactos

En lugar de preguntar:
- ❌ "¿Cuántos malbec tengo en stock?"

Pregunta usando los nombres exactos de las tablas/columnas:
- ✅ "¿Cuántos productos hay en Listado General donde Cepa es Malbec?"
- ✅ "SELECT COUNT(*) FROM Listado General WHERE Cepa = 'Malbec'"

### ✅ Solución 3: Crear un thread inicial con contexto

Antes de hacer preguntas, puedes "preparar" el thread con información sobre las tablas:

```python
# 1. Primera llamada: Establece el contexto
response1 = requests.post("http://localhost:5555/v1/asks", json={
    "query": "Muéstrame las tablas disponibles",
    "project_id": "7",
    "id": "707d0c244de6313b67bd9bdb0d0504d70a70fff6",
    "thread_id": "mi-thread-123"
})

# 2. Segunda llamada: Usa el mismo thread_id
response2 = requests.post("http://localhost:5555/v1/asks", json={
    "query": "¿Cuántos malbec tengo en stock?",
    "project_id": "7",
    "id": "707d0c244de6313b67bd9bdb0d0504d70a70fff6",
    "thread_id": "mi-thread-123"  # Mismo thread_id
})
```

### ✅ Solución 4: Usar el endpoint de semantics preparation

WrenAI tiene un endpoint para "preparar" el esquema semántico antes de hacer preguntas. Esto ayuda a que el sistema entienda mejor tu esquema.

## Resumen

| Método | Funciona | Requiere | Recomendado para |
|--------|----------|----------|------------------|
| UI directa | ✅ Sí | Navegador | Uso interactivo |
| Webhook sin thread_id | ❌ No | Nada | ❌ No usar |
| Webhook con thread_id de UI | ✅ Sí | Thread de UI | Pruebas rápidas |
| Webhook con thread persistente | ✅ Sí | Gestión de threads | Producción |
| Preguntas con nombres exactos | ⚠️ A veces | Conocer esquema | Queries específicos |

## Próximos Pasos

Para integrar esto con WhatsApp:

1. **Mantén un thread_id por usuario de WhatsApp**
   ```python
   thread_id = hashlib.md5(f"whatsapp_{phone_number}".encode()).hexdigest()
   ```

2. **Inicializa el thread la primera vez que un usuario escribe**
   - Envía una pregunta inicial como "Hola" o "¿Qué puedo preguntar?"
   - Esto establece el contexto

3. **Usa el mismo thread_id para todas las preguntas de ese usuario**
   - Esto mantiene el contexto de la conversación
   - El usuario puede hacer preguntas de seguimiento

4. **Opcionalmente, resetea el thread después de X tiempo de inactividad**
   - Por ejemplo, después de 1 hora sin preguntas
   - Esto evita que el contexto se vuelva obsoleto
