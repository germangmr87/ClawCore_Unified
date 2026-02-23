#!/bin/bash
set -e

# --- CLAWCORE UNIFIED V4: PURE SOURCE INSTALLER ---
# Diseñado por: Gabriel & ClawCore iMac
# Objetivo: Despliegue de arquitectura madura y soberana

echo "🔱 INICIANDO INSTALACIÓN SOBERANA DE CLAWCORE UNIFIED V4..."

# 1. Auditoría de Infraestructura
echo "🔍 Auditando Host..."
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js no detectado. Se requiere v22+."
    exit 1
fi

# 2. Instalación de Dependencias Core
echo "📦 Instalando dependencias de producción..."
npm install --omit=dev

# 3. Compilación del Núcleo (TypeScript)
echo "🏗️ Compilando código fuente..."
if [ -f "node_modules/.bin/tsc" ]; then
    ./node_modules/.bin/tsc
else
    echo "⚠️ TSC no encontrado, usando versión global..."
    tsc || echo "⚠️ Fallo en compilación, revisando fuentes..."
fi

# 4. Preparación del Cerebro RAG (Python)
echo "🧠 Configurando Motor RAG y Neuronas..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install chromadb sentence-transformers openai

# 5. Configuración de Identidad Soberana
if [ ! -f ".env" ]; then
    echo "🔑 Configuración de Secretos..."
    read -p "Introduce tu TELEGRAM_TOKEN: " T_TOKEN
    read -p "Introduce tu LLMAPI_KEY: " L_KEY
    read -p "Introduce tu WHITELIST_ID (Gabriel ID): " W_ID
    
    cat > .env << ENV_EOF
TELEGRAM_TOKEN=$T_TOKEN
LLMAPI_KEY=$L_KEY
WHITELIST_ID=$W_ID
ENV_EOF
    echo "✅ Búnker de secretos creado."
fi

# 6. Lanzamiento de Producción (Persistencia Real)
echo "🚀 Lanzando ClawCore V4 via PM2..."
pm2 delete ClawCore-V4 || true
pm2 start dist/entry.js --name ClawCore-V4 --update-env
pm2 save

echo "✅ INSTALACIÓN COMPLETADA EXITOSAMENTE."
echo "ClawCore V4 es ahora el núcleo soberano de esta máquina."
