#!/bin/bash
set -e

# --- CLAWCORE UNIFIED V5: ATOMIC INSTALLER ---
# No parches. Solo código fuente compilado.

echo "🔱 INICIANDO INSTALACIÓN PURA CLAWCORE V5..."

# 1. Limpieza de residuos de instalaciones fallidas
echo "🧹 Limpiando entorno..."
rm -rf dist node_modules package-lock.json

# 2. Instalación de dependencias (Madurez de ClawCore)
echo "📦 Instalando dependencias de producción..."
npm install --omit=dev

# 3. Compilación Profesional (TypeScript a JS)
echo "🏗️ Compilando código fuente..."
if ! ./node_modules/.bin/tsc; then
    echo "⚠️ Fallo tsc local. Intentando con tsc global..."
    tsc
fi

# 4. Verificación de Búnker .env
if [ ! -f ".env" ]; then
    echo "🔑 Configurando .env (Soberanía)..."
    read -p "TELEGRAM_TOKEN: " T_TOKEN
    read -p "LLMAPI_KEY: " L_KEY
    read -p "WHITELIST_ID: " W_ID
    
    cat > .env << EOF
TELEGRAM_TOKEN=$T_TOKEN
LLMAPI_KEY=$L_KEY
WHITELIST_ID=$W_ID
EOF
fi

# 5. Ignición Profesional vía PM2
echo "🚀 Lanzando ClawCore V5..."
pm2 delete ClawCore-V5 || true
pm2 start dist/index.js --name ClawCore-V5 --update-env
pm2 save

echo "✅ INSTALACIÓN PURA COMPLETADA. ClawCore V5 está vivo."
