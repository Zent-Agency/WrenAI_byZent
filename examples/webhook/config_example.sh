#!/bin/bash
# Configuración de ejemplo para WrenAI Webhook
# Copia este archivo y ajusta los valores según tu entorno

# ====================================
# CONFIGURACIÓN DE SERVIDOR
# ====================================

# Puerto donde corre el webhook
export WEBHOOK_PORT=5000

# Host donde escucha el webhook
export WEBHOOK_HOST=0.0.0.0

# ====================================
# CONFIGURACIÓN DE WREN AI
# ====================================

# URL del servicio WrenAI
export WREN_AI_URL=http://localhost:5555

# Project ID (obtén esto de la UI de WrenAI)
export WREN_PROJECT_ID=7

# Deploy ID (obtén esto de la UI de WrenAI)
export WREN_DEPLOY_ID=707d0c244de6313b67bd9bdb0d0504d70a70fff6

# ====================================
# ALMACENAMIENTO DE THREADS
# ====================================

# Archivo donde se guardan los threads (relativo al directorio del webhook)
export THREADS_STORAGE_FILE=threads_storage.json

# ====================================
# TIMEOUTS
# ====================================

# Tiempo máximo de espera para respuesta de WrenAI (segundos)
export WREN_TIMEOUT=120

# Intervalo de polling para verificar estado (segundos)
export POLL_INTERVAL=2

# ====================================
# LOGGING
# ====================================

# Nivel de log (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=INFO

# Archivo de log (opcional, en blanco = stdout)
export LOG_FILE=

# ====================================
# EJEMPLOS DE USO
# ====================================

# 1. Cargar esta configuración:
#    source config_example.sh
#
# 2. Iniciar el servidor:
#    python webhook_server.py
#
# 3. Probar el webhook:
#    curl -X POST http://localhost:5000/webhook \
#      -H "Content-Type: application/json" \
#      -d '{"message":"¿Qué vinos tengo?","user_id":"usuario_123"}'
#
# 4. Para Docker Compose:
#    docker-compose -f docker-compose.yml up -d
#    docker exec -it wren-webhook python webhook_server.py
#

# ====================================
# NOTAS IMPORTANTES
# ====================================

# • WREN_PROJECT_ID: Obtén este valor de la UI de WrenAI
#   Entra a http://localhost:4000 y busca el Project ID en la configuración
#
# • WREN_DEPLOY_ID: Es el hash del despliegue
#   Se muestra en la UI después de hacer deploy del modelo
#
# • THREADS_STORAGE_FILE: Por defecto "threads_storage.json"
#   Este archivo se crea automáticamente en el primer uso
#   Contiene el historial de conversaciones por usuario
#
# • WREN_TIMEOUT: 120 segundos es lo recomendado
#   Aumenta si tienes problemas de timeout
#   Disminuye si quieres respuestas más rápidas

echo "✅ Configuración cargada"
echo "   WREN_AI_URL: $WREN_AI_URL"
echo "   PROJECT_ID: $WREN_PROJECT_ID"
echo "   WEBHOOK_PORT: $WEBHOOK_PORT"
