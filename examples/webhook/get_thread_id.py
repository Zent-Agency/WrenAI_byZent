#!/usr/bin/env python3
"""
Script para obtener y gestionar Thread IDs en WrenAI
Un Thread ID representa una conversación completa que persiste durante toda la sesión
"""
import requests
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any


class ThreadManager:
    """Gestor de threads para mantener conversaciones persistentes"""
    
    def __init__(self, wren_url: str = "http://localhost:5555"):
        self.wren_url = wren_url.rstrip('/')
        self.threads = {}  # Almacenar threads localmente
        self.thread_file = "threads_storage.json"
        self.load_threads()
    
    def load_threads(self):
        """Cargar threads desde archivo"""
        try:
            with open(self.thread_file, 'r') as f:
                self.threads = json.load(f)
                print(f"✅ Threads cargados: {len(self.threads)} conversaciones activas")
        except FileNotFoundError:
            print("📝 Primer uso: Se creará un nuevo archivo de threads")
            self.threads = {}
    
    def save_threads(self):
        """Guardar threads en archivo"""
        with open(self.thread_file, 'w') as f:
            json.dump(self.threads, f, indent=2)
    
    def create_thread(self, user_id: str, project_id: str, deploy_id: str) -> str:
        """
        Crear un nuevo thread enviando la primera pregunta
        
        Args:
            user_id: ID del usuario
            project_id: ID del proyecto en WrenAI
            deploy_id: ID del despliegue
            
        Returns:
            thread_id: El ID del thread creado
        """
        print(f"\n🆕 Creando nuevo thread para usuario: {user_id}")
        
        # Primera pregunta para iniciar el thread
        url = f"{self.wren_url}/v1/asks"
        payload = {
            "query": "Hola, inicia una nueva conversación",  # Pregunta inicial simple
            "project_id": project_id,
            "id": deploy_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # El thread_id viene en la respuesta
            thread_id = data.get("thread_id")
            query_id = data.get("query_id")
            
            if not thread_id:
                print("⚠️  No se recibió thread_id en la respuesta")
                print(f"📋 Respuesta del servidor: {json.dumps(data, indent=2)}")
                return None
            
            # Almacenar información del thread
            self.threads[user_id] = {
                "thread_id": thread_id,
                "query_id": query_id,
                "project_id": project_id,
                "deploy_id": deploy_id,
                "created_at": datetime.now().isoformat(),
                "messages_count": 1
            }
            
            self.save_threads()
            
            print(f"✅ Thread creado exitosamente!")
            print(f"   User ID: {user_id}")
            print(f"   Thread ID: {thread_id}")
            print(f"   Query ID: {query_id}")
            
            return thread_id
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al crear thread: {str(e)}")
            return None
    
    def get_thread(self, user_id: str) -> Optional[str]:
        """
        Obtener el thread_id de un usuario existente
        
        Args:
            user_id: ID del usuario
            
        Returns:
            thread_id: El ID del thread si existe
        """
        if user_id in self.threads:
            thread_id = self.threads[user_id]["thread_id"]
            print(f"✅ Thread encontrado para usuario {user_id}: {thread_id}")
            return thread_id
        else:
            print(f"❌ No hay thread para usuario {user_id}")
            return None
    
    def ask_with_thread(
        self,
        user_id: str,
        question: str,
        project_id: str,
        deploy_id: str
    ) -> Dict[str, Any]:
        """
        Hacer una pregunta manteniendo el contexto del thread
        
        Args:
            user_id: ID del usuario
            question: La pregunta
            project_id: ID del proyecto
            deploy_id: ID del despliegue
            
        Returns:
            Dict con query_id, thread_id y respuesta
        """
        # Si no existe thread para este usuario, crear uno
        if user_id not in self.threads:
            thread_id = self.create_thread(user_id, project_id, deploy_id)
            if not thread_id:
                return {"error": "No se pudo crear thread"}
        else:
            thread_id = self.threads[user_id]["thread_id"]
        
        # Hacer la pregunta con el thread_id
        print(f"\n📤 Enviando pregunta con thread_id: {thread_id}")
        
        url = f"{self.wren_url}/v1/asks"
        payload = {
            "query": question,
            "project_id": project_id,
            "id": deploy_id,
            "thread_id": thread_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            query_id = data.get("query_id")
            response_thread_id = data.get("thread_id", thread_id)
            
            # Actualizar contador de mensajes
            if user_id in self.threads:
                self.threads[user_id]["messages_count"] = self.threads[user_id].get("messages_count", 0) + 1
                self.save_threads()
            
            print(f"✅ Pregunta enviada")
            print(f"   Query ID: {query_id}")
            print(f"   Thread ID: {response_thread_id}")
            
            return {
                "query_id": query_id,
                "thread_id": response_thread_id,
                "status": "sent",
                "raw_response": data
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al enviar pregunta: {str(e)}")
            return {"error": str(e)}
    
    def list_threads(self):
        """Listar todos los threads almacenados"""
        if not self.threads:
            print("📭 No hay threads almacenados")
            return
        
        print("\n📋 Threads almacenados:")
        print("-" * 80)
        for user_id, info in self.threads.items():
            print(f"User: {user_id}")
            print(f"  Thread ID: {info['thread_id']}")
            print(f"  Mensajes: {info.get('messages_count', 0)}")
            print(f"  Creado: {info.get('created_at', 'N/A')}")
            print("-" * 80)
    
    def delete_thread(self, user_id: str):
        """Eliminar un thread"""
        if user_id in self.threads:
            del self.threads[user_id]
            self.save_threads()
            print(f"✅ Thread de {user_id} eliminado")
        else:
            print(f"❌ No hay thread para {user_id}")


def show_help():
    """Mostrar ayuda"""
    print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                   GESTOR DE THREAD IDs PARA WrenAI                            ║
╚════════════════════════════════════════════════════════════════════════════════╝

¿QUÉ ES UN THREAD_ID?
  • Identificador de una CONVERSACIÓN completa
  • Se mantiene constante durante toda la sesión
  • Permite mantener el contexto entre múltiples preguntas
  • Es persistente (dura toda la conversación)

USO:
  python get_thread_id.py <comando> [argumentos]

COMANDOS:
  
  1. Crear thread (inicio de conversación)
     python get_thread_id.py create <user_id> <project_id> <deploy_id>
     
     Ejemplo:
     python get_thread_id.py create user123 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6

  2. Obtener thread existente
     python get_thread_id.py get <user_id>
     
     Ejemplo:
     python get_thread_id.py get user123

  3. Hacer pregunta manteniendo conversación
     python get_thread_id.py ask <user_id> <project_id> <deploy_id> "<pregunta>"
     
     Ejemplo:
     python get_thread_id.py ask user123 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6 "¿Qué vinos tengo?"

  4. Listar todos los threads
     python get_thread_id.py list

  5. Eliminar un thread
     python get_thread_id.py delete <user_id>

FLUJO RECOMENDADO:
  
  1. Primero, crear un thread:
     python get_thread_id.py create myuser 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6
     
     📝 Esto devuelve un thread_id
  
  2. Hacer preguntas reutilizando el mismo thread_id:
     python get_thread_id.py ask myuser 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6 "¿Cuántos vinos hay?"
     python get_thread_id.py ask myuser 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6 "¿Cuál es el más caro?"
     
     ✅ Las preguntas mantienen contexto de conversación

WEBHOOK MEJORADO:
  
  El webhook ahora automáticamente:
  • Crea un thread_id por usuario
  • Mantiene la conversación en el mismo thread
  • Persiste el contexto entre preguntas
  • Gestiona múltiples usuarios simultáneamente
  
  Uso:
    curl -X POST http://localhost:5000/webhook \\
      -H "Content-Type: application/json" \\
      -d '{
        "message": "¿Qué vinos tengo?",
        "user_id": "usuario_123"
      }'

VARIABLES DE ENTORNO:
  
  WREN_AI_URL=http://localhost:5555
  WREN_PROJECT_ID=7
  WREN_DEPLOY_ID=707d0c244de6313b67bd9bdb0d0504d70a70fff6

ALMACENAMIENTO:
  
  Los threads se guardan en: threads_storage.json
  Puedes editar este archivo manualmente si es necesario

╚════════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    # Valores por defecto (modifica según tu configuración)
    wren_url = "http://localhost:5555"
    
    manager = ThreadManager(wren_url)
    
    if command == "create":
        if len(sys.argv) < 5:
            print("❌ Uso: python get_thread_id.py create <user_id> <project_id> <deploy_id>")
            sys.exit(1)
        user_id = sys.argv[2]
        project_id = sys.argv[3]
        deploy_id = sys.argv[4]
        thread_id = manager.create_thread(user_id, project_id, deploy_id)
        if thread_id:
            print(f"\n🎉 Thread ID para usar en tu webhook:")
            print(f"   {thread_id}")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("❌ Uso: python get_thread_id.py get <user_id>")
            sys.exit(1)
        user_id = sys.argv[2]
        thread_id = manager.get_thread(user_id)
    
    elif command == "ask":
        if len(sys.argv) < 6:
            print("❌ Uso: python get_thread_id.py ask <user_id> <project_id> <deploy_id> \"<pregunta>\"")
            sys.exit(1)
        user_id = sys.argv[2]
        project_id = sys.argv[3]
        deploy_id = sys.argv[4]
        question = " ".join(sys.argv[5:])
        result = manager.ask_with_thread(user_id, question, project_id, deploy_id)
        if "query_id" in result:
            print(f"\n✅ Resultado:")
            print(json.dumps(result, indent=2))
    
    elif command == "list":
        manager.list_threads()
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Uso: python get_thread_id.py delete <user_id>")
            sys.exit(1)
        user_id = sys.argv[2]
        manager.delete_thread(user_id)
    
    elif command == "help" or command == "-h" or command == "--help":
        show_help()
    
    else:
        print(f"❌ Comando desconocido: {command}")
        show_help()
