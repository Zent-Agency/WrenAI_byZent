#!/bin/bash
# Script de prueba rápida para obtener thread_id
# Ejecuta un flujo completo de conversación reutilizando thread_id

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     PRUEBA RÁPIDA: OBTENER Y USAR THREAD_ID                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL base
WEBHOOK_URL="http://localhost:5000/webhook"
USER_ID="usuario_test_$(date +%s)"

echo -e "${YELLOW}ℹ️  Configuración:${NC}"
echo "   Webhook: $WEBHOOK_URL"
echo "   Usuario: $USER_ID"
echo ""

# Verificar que el servidor esté corriendo
echo -e "${BLUE}🔍 Verificando que el servidor esté corriendo...${NC}"
if ! curl -s "$WEBHOOK_URL/../health" > /dev/null 2>&1; then
    echo "❌ El webhook no está disponible en $WEBHOOK_URL"
    echo "   ¿Está corriendo? python webhook_server.py"
    exit 1
fi
echo -e "${GREEN}✅ Servidor disponible${NC}"
echo ""

# Primera pregunta
echo -e "${BLUE}1️⃣  Enviando primera pregunta...${NC}"
RESPONSE1=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Dame 5 vinos malbec que tenga en stock.\",
    \"user_id\": \"$USER_ID\"
  }")

echo "$RESPONSE1" | jq '.' 2>/dev/null || echo "$RESPONSE1"
echo ""

# Extraer thread_id
THREAD_ID=$(echo "$RESPONSE1" | jq -r '.thread_id' 2>/dev/null)
if [ -z "$THREAD_ID" ] || [ "$THREAD_ID" = "null" ]; then
    echo -e "${YELLOW}⚠️  No se pudo obtener thread_id${NC}"
    echo "   Respuesta: $RESPONSE1"
    exit 1
fi

echo -e "${GREEN}✅ Thread ID obtenido: $THREAD_ID${NC}"
echo ""

# Segunda pregunta (reutilizando thread)
echo -e "${BLUE}2️⃣  Enviando segunda pregunta (reutilizando thread)...${NC}"
RESPONSE2=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"¿Cuál es el más caro?\",
    \"user_id\": \"$USER_ID\",
    \"thread_id\": \"$THREAD_ID\"
  }")

echo "$RESPONSE2" | jq '.' 2>/dev/null || echo "$RESPONSE2"
echo ""

# Tercera pregunta (continuando conversación)
echo -e "${BLUE}3️⃣  Enviando tercera pregunta (continuando conversación)...${NC}"
RESPONSE3=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Dame 3 pedidos que esten sin entregar.\",
    \"user_id\": \"$USER_ID\",
    \"thread_id\": \"$THREAD_ID\"
  }")

echo "$RESPONSE3" | jq '.' 2>/dev/null || echo "$RESPONSE3"
echo ""

# Ver todos los threads
echo -e "${BLUE}📋 Listando todos los threads...${NC}"
THREADS=$(curl -s "$WEBHOOK_URL/threads")
echo "$THREADS" | jq '.' 2>/dev/null || echo "$THREADS"
echo ""

echo -e "${GREEN}✅ PRUEBA COMPLETADA${NC}"
echo ""
echo -e "${YELLOW}📝 Resumen:${NC}"
echo "   Usuario: $USER_ID"
echo "   Thread ID: $THREAD_ID"
echo "   Mensajes enviados: 3"
echo ""
echo -e "${YELLOW}💡 Próximos pasos:${NC}"
echo "   1. Ver documentación: cat OBTENER_THREAD_ID.md"
echo "   2. Ejecutar prueba de conversación: python test_webhook.py conversation"
echo "   3. Obtener thread de usuario: python test_webhook.py get-thread $USER_ID"
echo ""
