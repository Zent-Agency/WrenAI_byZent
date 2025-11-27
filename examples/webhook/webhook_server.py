"""
Servidor webhook simple para recibir mensajes y responder usando WrenAI
Ideal para integración con WhatsApp, Telegram, etc.

Mantiene conversaciones persistentes usando thread_id para cada usuario
"""
from flask import Flask, request, jsonify
import os
import sys
import json
from datetime import datetime

# Agregar el directorio actual al path para importar wren_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wren_client import WrenAIClient

app = Flask(__name__)

# Configuración
WREN_AI_URL = os.getenv("WREN_AI_URL", "http://localhost:5555")
PROJECT_ID = os.getenv("WREN_PROJECT_ID", "7")  # ID descubierto: 7
DEPLOY_ID = os.getenv("WREN_DEPLOY_ID", "707d0c244de6313b67bd9bdb0d0504d70a70fff6")  # ID descubierto

# Archivo para almacenar threads por usuario
THREADS_FILE = "threads_storage.json"

# Inicializar cliente de WrenAI
wren_client = WrenAIClient(base_url=WREN_AI_URL, project_id=PROJECT_ID, deploy_id=DEPLOY_ID)


def load_threads():
    """Cargar threads desde archivo"""
    if os.path.exists(THREADS_FILE):
        try:
            with open(THREADS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_threads(threads):
    """Guardar threads en archivo"""
    with open(THREADS_FILE, 'w') as f:
        json.dump(threads, f, indent=2)


def get_or_create_thread(user_id: str, project_id: str, deploy_id: str) -> str:
    """
    Obtener el thread_id de un usuario o crear uno nuevo
    
    Args:
        user_id: ID del usuario
        project_id: ID del proyecto
        deploy_id: ID del despliegue
        
    Returns:
        thread_id: El ID del thread
    """
    threads = load_threads()
    
    if user_id in threads and threads[user_id].get("thread_id"):
        print(f"♻️  Reutilizando thread existente para {user_id}")
        return threads[user_id]["thread_id"]
    
    print(f"🆕 Creando nuevo thread para usuario {user_id}")
    
    # Crear un nuevo thread haciendo la primera pregunta
    ask_response = wren_client.ask_question(
        "Inicia una nueva conversación",
        project_id=project_id,
        deploy_id=deploy_id
    )
    
    # El thread_id viene en la respuesta
    thread_id = ask_response.get("thread_id")
    
    if not thread_id:
        print("⚠️  No se recibió thread_id, generando uno basado en user_id")
        # Fallback: generar thread_id basado en user_id si la API no lo proporciona
        import hashlib
        thread_id = hashlib.md5(f"thread_{user_id}_{datetime.now().isoformat()}".encode()).hexdigest()
    
    # Guardar thread en memoria
    threads[user_id] = {
        "thread_id": thread_id,
        "project_id": project_id,
        "deploy_id": deploy_id,
        "created_at": datetime.now().isoformat(),
        "messages_count": 0
    }
    save_threads(threads)
    
    print(f"✅ Thread creado: {thread_id}")
    return thread_id


@app.route('/webhook/threads', methods=['GET'])
def get_threads():
    """Endpoint para ver todos los threads activos"""
    threads = load_threads()
    return jsonify({
        "status": "ok",
        "total_threads": len(threads),
        "threads": threads
    })


@app.route('/webhook/threads/<user_id>', methods=['GET'])
def get_user_thread(user_id):
    """Endpoint para obtener el thread_id de un usuario"""
    threads = load_threads()
    if user_id in threads:
        return jsonify({
            "status": "ok",
            "user_id": user_id,
            "thread_id": threads[user_id]["thread_id"],
            "messages_count": threads[user_id].get("messages_count", 0),
            "created_at": threads[user_id].get("created_at")
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"No hay thread para el usuario {user_id}"
        }), 404


@app.route('/webhook/threads/<user_id>', methods=['DELETE'])
def delete_thread(user_id):
    """Endpoint para eliminar el thread de un usuario"""
    threads = load_threads()
    if user_id in threads:
        del threads[user_id]
        save_threads(threads)
        return jsonify({
            "status": "ok",
            "message": f"Thread de {user_id} eliminado"
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"No hay thread para el usuario {user_id}"
        }), 404


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que el servidor está corriendo"""
    return jsonify({
        "status": "ok",
        "wren_ai_url": WREN_AI_URL,
        "project_id_configured": PROJECT_ID is not None,
        "active_threads": len(load_threads())
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint principal del webhook
    
    Espera un JSON con formato:
    {
        "message": "tu pregunta aquí",
        "user_id": "id-usuario",  # REQUERIDO para mantener conversación
        "project_id": "opcional-project-id",
        "thread_id": "opcional-si-ya-tienes-uno"
    }
    
    Responde con:
    {
        "status": "success|error",
        "query": "pregunta original",
        "thread_id": "id-de-conversacion",
        "sql": "SQL generado (si aplica)",
        "answer": "respuesta formateada",
        "raw_response": {...}  // respuesta completa de WrenAI
    }
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No se recibió JSON en el request"
            }), 400
        
        # Extraer mensaje
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                "status": "error",
                "message": "El campo 'message' es requerido"
            }), 400
        
        # Extraer user_id (IMPORTANTE para mantener threads)
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({
                "status": "error",
                "message": "El campo 'user_id' es requerido para mantener la conversación",
                "hint": "Envía: {'message': 'tu pregunta', 'user_id': 'identificador_unico'}"
            }), 400
        
        # Extraer project_id y deploy_id (pueden venir en el request o usar los configurados)
        project_id = data.get('project_id') or PROJECT_ID
        deploy_id = data.get('deploy_id') or DEPLOY_ID
        
        # Obtener o crear thread_id para este usuario
        if 'thread_id' in data:
            # Si viene en la petición, usarlo directamente
            thread_id = data.get('thread_id')
            print(f"🔗 Usando thread_id proporcionado: {thread_id}")
        else:
            # Si no, obtener uno existente o crear uno nuevo
            thread_id = get_or_create_thread(user_id, project_id, deploy_id)
        
        print(f"📩 Mensaje recibido de {user_id}: {message}")
        print(f"🔧 Config: ProjectID={project_id}, DeployID={deploy_id}, ThreadID={thread_id}")
        
        # Procesar con WrenAI
        print(f"🤖 Procesando con WrenAI...")
        result = wren_client.ask_and_wait(
            message, 
            project_id=project_id, 
            deploy_id=deploy_id, 
            thread_id=thread_id, 
            timeout=300
        )
        
        # Actualizar contador de mensajes
        threads = load_threads()
        if user_id in threads:
            threads[user_id]["messages_count"] = threads[user_id].get("messages_count", 0) + 1
            threads[user_id]["last_message"] = datetime.now().isoformat()
            save_threads(threads)
        
        # Verificar resultado
        status = result.get('status')
        
        if status == 'finished' or status == 'understanding' or status == 'searching' or status == 'planning' or status == 'generating':
            # Estados válidos - procesar respuesta
            responses = result.get('response', [])
            
            if responses and isinstance(responses, list) and len(responses) > 0:
                sql = responses[0].get('sql', '')
                answer = f"He generado la siguiente consulta SQL:\n\n```sql\n{sql}\n```"
            else:
                # Si está en estado intermedio pero sin respuesta aún, enviar mensaje útil
                if status != 'finished':
                    answer = f"Tu pregunta fue recibida y está siendo procesada (estado: {status}). Por favor intenta de nuevo en unos segundos."
                else:
                    answer = "He procesado tu pregunta."
            
            print(f"✅ Respuesta procesada (estado: {status})")
            
            return jsonify({
                "status": "success",
                "query": message,
                "thread_id": thread_id,
                "sql": responses[0].get('sql', '') if responses else None,
                "answer": answer,
                "wren_status": status,
                "raw_response": result
            })
        
        elif status == 'failed':
            error_info = result.get('error', {})
            error_message = error_info.get('message', 'Error desconocido') if isinstance(error_info, dict) else str(error_info)
            
            print(f"❌ Error: {error_message}")
            
            return jsonify({
                "status": "error",
                "query": message,
                "thread_id": thread_id,
                "message": f"No pude procesar tu pregunta: {error_message}",
                "raw_response": result
            }), 500
        
        else:
            print(f"⚠️ Estado inesperado: {result.get('status')}")
            
            return jsonify({
                "status": "error",
                "query": message,
                "thread_id": thread_id,
                "message": f"Estado inesperado: {result.get('status')}",
                "raw_response": result
            }), 500
    
    except Exception as e:
        print(f"💥 Error en webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": f"Error interno: {str(e)}"
        }), 500


@app.route('/webhook/test', methods=['GET'])
def webhook_test():
    """Endpoint de prueba para verificar que el webhook funciona"""
    return jsonify({
        "message": "Webhook funcionando correctamente",
        "instructions": {
            "method": "POST",
            "url": "/webhook",
            "body": {
                "message": "tu pregunta aquí",
                "user_id": "opcional",
                "project_id": "opcional"
            }
        }
    })


if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    
    print(f"""
    🚀 Servidor Webhook iniciado
    
    📍 URL: http://localhost:{port}
    🔗 Webhook: http://localhost:{port}/webhook
    💚 Health: http://localhost:{port}/health
    🧪 Test: http://localhost:{port}/webhook/test
    
    🤖 WrenAI URL: {WREN_AI_URL}
    📊 Project ID: {PROJECT_ID or 'No configurado'}
    🚀 Deploy ID:  {DEPLOY_ID or 'No configurado'}
    
    Para configurar el Project ID:
    export WREN_PROJECT_ID=tu-project-id
    
    """)
    
    app.run(host='0.0.0.0', port=port, debug=True)
