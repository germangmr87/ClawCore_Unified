#!/bin/bash
set -e

# --- CLAWCORE UNIFIED V5: ATOMIC & SOVEREIGN INSTALLER ---
# Basado en los estándares maduros de OpenClaw.

echo "🔱 INICIANDO DESPLIEGUE CLAWCORE UNIFIED V5..."

# 1. Validación de Entorno
echo "🔍 Verificando herramientas..."
if ! command -v node &> /dev/null; then echo "❌ Node.js no encontrado."; exit 1; fi
PM="npm"
if command -v pnpm &> /dev/null; then PM="pnpm"; fi

# 2. Configuración Interactiva (Búnker de Seguridad)
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  CONFIGURACIÓN DE IDENTIDAD (Se guardará en .env)"
    read -p "   🔑 Telegram Bot Token: " T_TOKEN
    read -p "   🔑 Gemini API Key: " G_KEY
    read -p "   🔑 DeepSeek API Key: " D_KEY
    read -p "   🛰️ Ollama Remote URL [http://localhost:11434]: " O_URL
    O_URL=${O_URL:-http://localhost:11434}
    
    cat > .env << EOF
TELEGRAM_BOT_TOKEN=$T_TOKEN
GEMINI_API_KEY=$G_KEY
DEEPSEEK_API_KEY=$D_KEY
OLLAMA_REMOTE_URL=$O_URL
WHITELIST_ID=12345678 # Ajustar según sea necesario
NODE_NAME=ClawCore_VPS
EOF
    echo "   ✅ Archivo .env configurado."
fi

# 3. Instalación de Dependencias Core (Node.js)
echo "📦 Instalando dependencias de Node.js con $PM..."
if [ "$PM" = "npm" ]; then
    $PM install --omit=dev --legacy-peer-deps
else
    $PM install --production
fi

# 4. Instalación de Dependencias de Neuronas (Python)
echo "🐍 Configurando dependencias de Python (Neuronas Soberanas)..."
python3 -m pip install fastapi uvicorn aiohttp python-dotenv websockets edge-tts --break-system-packages -q || \
python3 -m pip install fastapi uvicorn aiohttp python-dotenv websockets edge-tts -q

# 5. Compilación Profesional
echo "🏗️ Compilando código fuente..."
if [ -f "node_modules/.bin/tsdown" ]; then
    $PM run build
else
    npx tsc
fi

# 6. Lanzamiento vía PM2
echo "🚀 Lanzando ClawCore V5 (Sofia AI Gateway)..."
pm2 delete ClawCore-V5 2>/dev/null || true
# Lanzamos el Gateway que orquestra todo (incluyendo el Bot de Telegram)
export PYTHONPATH=$PYTHONPATH:.
pm2 start src/brain/api_gateway.py --name ClawCore-V5 --interpreter python3 --update-env
pm2 save

echo "✅ DESPLIEGUE COMPLETADO EXITOSAMENTE."
echo "Dashbord Sofia: http://tu-ip:18791/sofia"
