"""
Cliente Python para interactuar con la API de WrenAI
"""
import requests
import time
from typing import Optional, Dict, Any


class WrenAIClient:
    def __init__(self, base_url: str = "http://localhost:5555", project_id: Optional[str] = None, deploy_id: Optional[str] = None):
        """
        Inicializa el cliente de WrenAI
        
        Args:
            base_url: URL base del servicio de IA (default: http://localhost:5555)
            project_id: ID del proyecto configurado en la UI de WrenAI
            deploy_id: Hash del despliegue (deployment ID)
        """
        self.base_url = base_url.rstrip('/')
        self.project_id = project_id
        self.deploy_id = deploy_id

    def ask_question(self, query: str, project_id: Optional[str] = None, deploy_id: Optional[str] = None, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Envía una pregunta a WrenAI
        
        Args:
            query: La pregunta en lenguaje natural
            project_id: ID del proyecto (opcional, usa el del constructor si no se especifica)
            deploy_id: Hash del despliegue (opcional, usa el del constructor si no se especifica)
            thread_id: ID del hilo de conversación (opcional, para mantener contexto)
            
        Returns:
            Dict con query_id y thread_id para consultar el resultado
        """
        url = f"{self.base_url}/v1/asks"
        
        payload = {
            "query": query,
        }
        
        # Usar project_id si está disponible
        pid = project_id or self.project_id
        if pid:
            payload["project_id"] = pid

        # Usar deploy_id si está disponible (mapeado a 'id' en la API)
        did = deploy_id or self.deploy_id
        if did:
            payload["id"] = did
        
        # Agregar thread_id si está disponible
        if thread_id:
            payload["thread_id"] = thread_id
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            # Guardar el thread_id de la respuesta si está disponible
            if "thread_id" in result:
                self.last_thread_id = result["thread_id"]
            return result
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "query_id": None}

    def get_result(self, query_id: str) -> Dict[str, Any]:
        """
        Obtiene el resultado de una consulta
        
        Args:
            query_id: ID de la consulta obtenido de ask_question()
            
        Returns:
            Dict con el resultado de la consulta
        """
        url = f"{self.base_url}/v1/asks/{query_id}/result"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}

    def wait_for_result(
        self, 
        query_id: str, 
        poll_interval: int = 2, 
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Espera hasta que la consulta esté completa
        
        Args:
            query_id: ID de la consulta
            poll_interval: Segundos entre cada verificación
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            Dict con el resultado final
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.get_result(query_id)
            
            error = result.get("error")
            if error:
                return result
            
            status = result.get("status")
            
            if status == "finished":
                return result
            elif status == "failed":
                return result
            
            # Estados intermedios: understanding, searching, planning, generating, correcting
            print(f"DEBUG: Status is {status}, waiting...")
            time.sleep(poll_interval)
        
        print("DEBUG: Timeout reached!")
        
        return {
            "error": "Timeout esperando resultado",
            "status": "timeout",
            "query_id": query_id
        }

    def ask_and_wait(
        self, 
        query: str, 
        project_id: Optional[str] = None,
        deploy_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Método conveniente que hace la pregunta y espera el resultado
        
        Args:
            query: La pregunta en lenguaje natural
            project_id: ID del proyecto (opcional)
            deploy_id: Hash del despliegue (opcional)
            thread_id: ID del hilo de conversación (opcional, para mantener contexto)
            timeout: Tiempo máximo de espera
            
        Returns:
            Dict con el resultado completo
        """
        # Enviar pregunta
        ask_response = self.ask_question(query, project_id, deploy_id, thread_id)
        
        if "error" in ask_response:
            return ask_response
        
        query_id = ask_response.get("query_id")
        if not query_id:
            return {"error": "No se recibió query_id", "status": "failed"}
        
        # Esperar resultado
        return self.wait_for_result(query_id, timeout=timeout)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear cliente
    client = WrenAIClient(
        base_url="http://localhost:5555",
        # project_id="tu-project-id-aqui"  # Obtén esto desde la UI
    )
    
    # Hacer una pregunta
    print("Enviando pregunta...")
    result = client.ask_and_wait("¿Cuántos pedidos tenemos este mes?")
    
    print("\nResultado:")
    print(f"Status: {result.get('status')}")
    
    if result.get('status') == 'finished':
        responses = result.get('response', [])
        for resp in responses:
            print(f"\nSQL generado:\n{resp.get('sql')}")
    else:
        print(f"Error: {result.get('error')}")
