#!/bin/bash

# Script para probar el webhook de WrenAI

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
cd "$(dirname "$0")"

# Activar entorno virtual
source venv/bin/activate

# Mensaje por defecto o del argumento
MESSAGE="${1:-¿Que vinos malbec tengo en stock?}"

echo -e "${BLUE}🧪 Probando Webhook de WrenAI${NC}\n"
echo -e "${GREEN}Pregunta:${NC} $MESSAGE\n"

# Ejecutar test
python3 test_webhook.py "$MESSAGE"
