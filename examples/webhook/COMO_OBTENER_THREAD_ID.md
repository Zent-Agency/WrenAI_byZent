# 🔍 Cómo Obtener el Thread ID de la UI

## Paso a Paso (con imágenes de referencia)

### 1. Abre la UI de WrenAI
```
http://localhost:4000
```

### 2. Abre DevTools
- Presiona **F12** o **Ctrl+Shift+I** (Windows/Linux)
- O **Cmd+Option+I** (Mac)

### 3. Ve a la pestaña "Network"
- Haz clic en la pestaña **"Network"** en DevTools
- Asegúrate de que esté grabando (botón rojo activo)

### 4. Haz una pregunta en la UI
- Escribe cualquier pregunta en el chat de WrenAI
- Por ejemplo: "¿Cuántos malbec tengo en stock?"
- Presiona Enter

### 5. Busca la petición correcta
En la lista de peticiones de red, busca:
- **Tipo**: `POST` o `asks`
- **URL**: `/v1/asks` (NO `/graphql` ni `/fetch`)
- **Status**: `200`

### 6. Haz clic en esa petición
- Se abrirá un panel lateral con detalles

### 7. Ve a la pestaña "Payload" o "Request"
- Busca la sección **"Request Payload"** o **"Payload"**
- Verás algo como:

```json
{
  "query": "cuantos malbec tengo en stock?",
  "project_id": "7",
  "id": "707d0c244de6313b67bd9bdb0d0504d70a70fff6",
  "thread_id": "4",  ← ¡ESTE ES EL THREAD_ID!
  "configurations": {
    "language": "Spanish",
    "timezone": {
      "name": "America/Argentina/Buenos_Aires"
    }
  }
}
```

### 8. Copia el thread_id
- En el ejemplo de arriba, el `thread_id` es `"4"`
- **Copia ese valor** (sin las comillas)

---

## 🧪 Cómo Usarlo

### Opción 1: Con el script de prueba

```bash
cd /root/wren_ai/examples/webhook
./venv/bin/python test_with_ui_thread.py "4" "¿Cuántos malbec tengo?"
```

### Opción 2: Con curl directamente

```bash
curl -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuántos malbec tengo en stock?",
    "thread_id": "4",
    "user_id": "test_user"
  }'
```

### Opción 3: Directamente a la API de WrenAI

```bash
curl -X POST http://localhost:5555/v1/asks \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuántos malbec tengo en stock?",
    "project_id": "7",
    "id": "707d0c244de6313b67bd9bdb0d0504d70a70fff6",
    "thread_id": "4"
  }'
```

---

## ⚠️ Importante

### query_id vs thread_id

| Campo | Propósito | Cuándo se usa | Ejemplo |
|-------|-----------|---------------|---------|
| **thread_id** | Identificar la conversación | Se envía EN la petición | `"4"` |
| **query_id** | Identificar una pregunta específica | Se recibe EN la respuesta | `"20e2070c-b63d..."` |

### Flujo completo:

```
1. Envías una pregunta CON thread_id:
   POST /v1/asks
   {
     "query": "¿Cuántos malbec?",
     "thread_id": "4"  ← Tú lo envías
   }

2. Recibes un query_id:
   {
     "query_id": "abc-123-def"  ← WrenAI te lo devuelve
   }

3. Consultas el resultado CON query_id:
   GET /v1/asks/abc-123-def/result
```

---

## 🎯 Resumen Visual

```
┌─────────────────────────────────────────┐
│  CONVERSACIÓN (thread_id: "4")         │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Pregunta 1 (query_id: "abc-123") │ │
│  │ "¿Cuántos malbec tengo?"          │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Pregunta 2 (query_id: "def-456") │ │
│  │ "¿Y cuántos cabernet?"            │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Pregunta 3 (query_id: "ghi-789") │ │
│  │ "¿Cuál es más caro?"              │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘

thread_id = "4" (mismo para todas)
query_id = diferente para cada pregunta
```

---

## 💡 Tip

Si no ves el `thread_id` en el payload, puede ser que:
1. Estás mirando la petición equivocada (busca `/v1/asks`)
2. La UI no está enviando thread_id (poco probable)
3. Necesitas hacer scroll en el payload para verlo

¡Busca específicamente la petición **POST** a **/v1/asks**!
