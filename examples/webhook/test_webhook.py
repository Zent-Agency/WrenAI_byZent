"""
Script de prueba para el webhook
Simula el envío de mensajes al webhook manteniendo conversación con thread_id
"""
import requests
import json
import sys


def test_webhook(message: str, user_id: str = "test_user", webhook_url: str = "http://localhost:5000/webhook", thread_id: str = None):
    """
    Envía un mensaje de prueba al webhook
    
    Args:
        message: La pregunta a enviar
        user_id: ID del usuario (importante para mantener thread)
        webhook_url: URL del webhook
        thread_id: Thread ID opcional
    """
    print(f"\n{'='*60}")
    print(f"📤 Enviando mensaje al webhook...")
    print(f"Usuario: {user_id}")
    print(f"Pregunta: {message}")
    if thread_id:
        print(f"Thread ID: {thread_id}")
    print(f"{'='*60}\n")
    
    payload = {
        "message": message,
        "user_id": user_id
    }
    
    # Agregar thread_id si se proporciona
    if thread_id:
        payload["thread_id"] = thread_id
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=180  # 3 minutos de timeout
        )
        
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ RESPUESTA EXITOSA")
            print(f"\nEstado: {result.get('status')}")
            print(f"Pregunta: {result.get('query')}")
            
            # Mostrar thread_id (importante para la siguiente pregunta)
            if result.get('thread_id'):
                print(f"🔗 Thread ID: {result.get('thread_id')}")
            
            if result.get('sql'):
                print(f"\n📊 SQL Generado:")
                print(result.get('sql'))
            
            print(f"\n💬 Respuesta:")
            print(result.get('answer', 'Sin respuesta'))
            
            # Devolver el thread_id para la siguiente pregunta
            return result.get('thread_id')
            
        else:
            print("❌ ERROR EN LA RESPUESTA")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return None
    
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT - La solicitud tardó demasiado")
        return None
    
    except requests.exceptions.ConnectionError:
        print("🔌 ERROR DE CONEXIÓN - ¿Está corriendo el servidor webhook?")
        print(f"Verifica que el servidor esté corriendo en {webhook_url}")
        return None
    
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        return None
    
    finally:
        print(f"\n{'='*60}\n")


def test_conversation():
    """Test de una conversación completa manteniendo contexto"""
    print("\n" + "="*60)
    print("🧵 PRUEBA DE CONVERSACIÓN CON CONTEXT")
    print("="*60)
    
    webhook_url = "http://localhost:5000/webhook"
    user_id = "usuario_conversacion_01"
    
    # Primera pregunta
    print("\n1️⃣ Primera pregunta...")
    thread_id = test_webhook(
        "¿Qué vinos malbec tengo en stock?",
        user_id=user_id,
        webhook_url=webhook_url
    )
    
    if thread_id:
        # Segunda pregunta reutilizando el mismo thread
        print("\n2️⃣ Segunda pregunta (reutilizando thread)...")
        thread_id = test_webhook(
            "¿Cuál es el más caro?",
            user_id=user_id,
            webhook_url=webhook_url,
            thread_id=thread_id
        )
        
        # Tercera pregunta
        if thread_id:
            print("\n3️⃣ Tercera pregunta (continuando conversación)...")
            test_webhook(
                "¿Cuántas botellas hay?",
                user_id=user_id,
                webhook_url=webhook_url,
                thread_id=thread_id
            )


def get_user_threads(webhook_url: str = "http://localhost:5000"):
    """Obtener todos los threads activos"""
    print("\n" + "="*60)
    print("📋 THREADS ACTIVOS")
    print("="*60 + "\n")
    
    try:
        response = requests.get(f"{webhook_url}/webhook/threads", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Total de threads: {data['total_threads']}\n")
            
            for user_id, info in data['threads'].items():
                print(f"Usuario: {user_id}")
                print(f"  Thread ID: {info['thread_id']}")
                print(f"  Mensajes: {info.get('messages_count', 0)}")
                print(f"  Creado: {info.get('created_at', 'N/A')}")
                print("-" * 40)
    except Exception as e:
        print(f"Error: {str(e)}")


def get_user_thread_id(user_id: str, webhook_url: str = "http://localhost:5000"):
    """Obtener el thread_id de un usuario específico"""
    print(f"\n🔍 Buscando thread para usuario: {user_id}\n")
    
    try:
        response = requests.get(f"{webhook_url}/webhook/threads/{user_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Thread encontrado:")
            print(f"   Thread ID: {data['thread_id']}")
            print(f"   Mensajes: {data['messages_count']}")
            print(f"   Creado: {data['created_at']}")
            return data['thread_id']
        else:
            print(f"❌ {response.json()['message']}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    # URL del webhook (puedes cambiarla si es necesario)
    webhook_url = "http://localhost:5000/webhook"
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "conversation":
            # Prueba de conversación completa
            test_conversation()
        
        elif command == "threads":
            # Listar todos los threads
            get_user_threads("http://localhost:5000")
        
        elif command == "get-thread":
            # Obtener thread de un usuario
            if len(sys.argv) > 2:
                user_id = sys.argv[2]
                thread_id = get_user_thread_id(user_id, "http://localhost:5000")
            else:
                print("Uso: python test_webhook.py get-thread <user_id>")
        
        else:
            # Enviar mensaje individual
            message = " ".join(sys.argv[1:])
            test_webhook(message, webhook_url=webhook_url)
    
    else:
        # Mensaje de prueba por defecto
        print("\n💡 EJEMPLOS DE USO:\n")
        print("  # Prueba individual:")
        print("  python test_webhook.py '¿Qué vinos tengo?'\n")
        
        print("  # Prueba de conversación completa (mantiene thread):")
        print("  python test_webhook.py conversation\n")
        
        print("  # Listar todos los threads activos:")
        print("  python test_webhook.py threads\n")
        
        print("  # Obtener thread de un usuario:")
        print("  python test_webhook.py get-thread usuario_123\n")
        
        # Por defecto, hacer una prueba simple
        message = "¿Que vinos malbec tengo en stock?"
        test_webhook(message, webhook_url=webhook_url)

