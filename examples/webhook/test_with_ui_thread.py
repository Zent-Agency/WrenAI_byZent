"""
Script para probar el webhook usando un thread_id de la UI
Esto permite mantener el contexto de conversación
"""
import requests
import json
import sys

def test_with_thread(message: str, thread_id: str, webhook_url: str = "http://localhost:5001/webhook"):
    """
    Envía un mensaje de prueba al webhook con un thread_id específico
    
    Args:
        message: La pregunta a enviar
        thread_id: ID del thread de la UI
        webhook_url: URL del webhook
    """
    print(f"\n{'='*60}")
    print(f"📤 Enviando mensaje al webhook...")
    print(f"Pregunta: {message}")
    print(f"Thread ID: {thread_id}")
    print(f"{'='*60}\n")
    
    payload = {
        "message": message,
        "user_id": "test_user_123",
        "thread_id": thread_id  # Usar el thread_id de la UI
    }
    
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
            
            if result.get('sql'):
                print(f"\n📊 SQL Generado:")
                print(result.get('sql'))
            
            print(f"\n💬 Respuesta:")
            print(result.get('answer', 'Sin respuesta'))
            
        else:
            print("❌ ERROR EN LA RESPUESTA")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
    
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT - La solicitud tardó demasiado")
    
    except requests.exceptions.ConnectionError:
        print("🔌 ERROR DE CONEXIÓN - ¿Está corriendo el servidor webhook?")
        print(f"Verifica que el servidor esté corriendo en {webhook_url}")
    
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    webhook_url = "http://localhost:5001/webhook"
    
    # El thread_id debe obtenerse de la UI
    # Abre http://localhost:4000, ve a DevTools > Network, haz una pregunta
    # y copia el thread_id del payload de la petición POST /v1/asks
    
    if len(sys.argv) < 2:
        print("❌ Error: Debes proporcionar un thread_id")
        print("\n📝 Cómo obtener el thread_id:")
        print("1. Abre http://localhost:4000 en tu navegador")
        print("2. Abre DevTools (F12) > pestaña Network")
        print("3. Haz una pregunta en la UI")
        print("4. Busca la petición POST a /v1/asks")
        print("5. En el payload verás el 'thread_id'")
        print(f"\n💡 Uso: python {sys.argv[0]} <thread_id> [pregunta]")
        print(f"   Ejemplo: python {sys.argv[0]} 'abc123' '¿Cuántos malbec tengo?'")
        sys.exit(1)
    
    thread_id = sys.argv[1]
    
    if len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])
    else:
        message = "¿Cuantos malbec tengo en stock?"
    
    test_with_thread(message, thread_id, webhook_url)
