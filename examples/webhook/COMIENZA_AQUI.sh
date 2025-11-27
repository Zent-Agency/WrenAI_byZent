#!/bin/bash
# 🎯 GUÍA RÁPIDA DE INICIO - OBTENER THREAD_ID

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════════╗
║                      🧵 SOLUCIÓN: OBTENER THREAD_ID                           ║
║                                                                                ║
║  ✅ Problema resuelto: Ahora puedes obtener y mantener thread_id             ║
║  ✅ Las conversaciones mantienen contexto automáticamente                    ║
║  ✅ Múltiples usuarios simultáneos soportados                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

📋 TABLA DE CONTENIDOS:
  1. Inicio Rápido (30 segundos)
  2. Ejemplo Completo
  3. Archivos Disponibles
  4. Comandos Útiles
  5. Troubleshooting

════════════════════════════════════════════════════════════════════════════════

1️⃣  INICIO RÁPIDO (30 SEGUNDOS)

   Paso 1: Asegúrate que WrenAI esté corriendo
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   curl http://localhost:5555/health
   
   Paso 2: Inicia el webhook en otra terminal
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   python webhook_server.py
   
   Paso 3: Prueba el webhook
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   curl -X POST http://localhost:5000/webhook \
     -H "Content-Type: application/json" \
     -d '{
       "message": "¿Qué vinos tengo?",
       "user_id": "usuario_123"
     }'
   
   ✅ Recibirás el thread_id en la respuesta!

════════════════════════════════════════════════════════════════════════════════

2️⃣  EJEMPLO COMPLETO (CONVERSACIÓN)

   # Terminal 1: Inicia el servidor
   python webhook_server.py
   
   # Terminal 2: Ejecuta el test
   bash quick_test.sh
   
   ✅ Esto hará 3 preguntas seguidas manteniendo contexto!

════════════════════════════════════════════════════════════════════════════════

3️⃣  ARCHIVOS DISPONIBLES

   📄 README_THREAD_ID.md
      └─ Guía principal (Inicia aquí!)
   
   📄 OBTENER_THREAD_ID.md
      └─ Documentación completa con ejemplos
   
   📄 RESUMEN_CAMBIOS.md
      └─ Cambios técnicos implementados
   
   🐍 get_thread_id.py
      └─ Script para gestionar threads
   
   🔧 quick_test.sh
      └─ Prueba rápida completa
   
   ⚙️  config_example.sh
      └─ Variables de configuración

════════════════════════════════════════════════════════════════════════════════

4️⃣  COMANDOS ÚTILES

   Prueba rápida:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   bash quick_test.sh
   
   Ver ayuda del script Python:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   python get_thread_id.py help
   
   Crear un thread:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   python get_thread_id.py create usuario_123 7 707d0c244de6313b67bd9bdb0d0504d70a70fff6
   
   Ver threads almacenados:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   python get_thread_id.py list
   
   Hacer pregunta con thread:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   python get_thread_id.py ask usuario_123 7 deploy_id "¿Cuántos vinos?"
   
   Prueba conversación completa:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   python test_webhook.py conversation
   
   Ver threads del webhook:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   curl http://localhost:5000/webhook/threads
   
   Obtener thread de usuario:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   curl http://localhost:5000/webhook/threads/usuario_123

════════════════════════════════════════════════════════════════════════════════

5️⃣  TROUBLESHOOTING

   ❌ "user_id is required"
      → Incluye "user_id" en tu JSON:
        {"message": "...", "user_id": "identificador"}
   
   ❌ "No se recibió thread_id"
      → Verifica que WrenAI esté corriendo:
        curl http://localhost:5555/health
   
   ❌ "Connection refused"
      → Inicia el webhook:
        python webhook_server.py
   
   ❌ Conversación no mantiene contexto
      → Verifica que estés reutilizando el MISMO thread_id:
        {"message": "...", "user_id": "...", "thread_id": "abc123"}

════════════════════════════════════════════════════════════════════════════════

🎯 FLUJO RECOMENDADO:

   1. Lee README_THREAD_ID.md                    (5 min)
   2. Ejecuta bash quick_test.sh                 (1 min)
   3. Prueba python test_webhook.py conversation (2 min)
   4. Integra en tu aplicación                   (∞ min)

════════════════════════════════════════════════════════════════════════════════

📞 ENLACES ÚTILES:

   Documentación:
   • cat README_THREAD_ID.md
   • cat OBTENER_THREAD_ID.md
   • cat RESUMEN_CAMBIOS.md
   
   Scripts:
   • python get_thread_id.py help
   • bash quick_test.sh
   • python test_webhook.py conversation

════════════════════════════════════════════════════════════════════════════════

✅ ¡TODO ESTÁ LISTO!

Ahora puedes:
  ✓ Obtener thread_id automáticamente
  ✓ Mantener conversaciones con contexto
  ✓ Gestionar múltiples usuarios
  ✓ Persistir threads entre sesiones

¡Comienza leyendo README_THREAD_ID.md! 📖

EOF
