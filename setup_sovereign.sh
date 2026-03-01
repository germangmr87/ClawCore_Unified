#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# CLAWCORE SOVEREIGN SETUP — v5.5
# Script de instalación y configuración del ecosistema soberano.
# Copia los archivos corregidos al runtime y verifica que todo funcione.
# ─────────────────────────────────────────────────────────────────────────────
set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
RUNTIME_DIR="$HOME/.clawcore"
RUNTIME_SRC="$RUNTIME_DIR/src"
UI_DIST="$REPO_ROOT/dist/control-ui"

echo "🔱 ClawCore Sovereign Setup v5.5"
echo "──────────────────────────────────────────────────────"
echo "  Repo:    $REPO_ROOT"
echo "  Runtime: $RUNTIME_DIR"
echo ""

# 1. Crear estructura de directorios si no existe
mkdir -p "$RUNTIME_SRC/brain"
mkdir -p "$RUNTIME_SRC/clawcore_system/neuronas"
mkdir -p "$RUNTIME_DIR/logs"

# (Sync movido abajo para incluir el build de la UI)

# 3. Verificar dependencias Python
echo ""
echo "🐍 Verificando dependencias Python..."
python3 -c "import fastapi, uvicorn, aiohttp, dotenv; print('   ✅ dependencias base OK')" 2>/dev/null \
  || { echo "   ⚠️  Instalando dependencias faltantes..."; python3 -m pip install fastapi uvicorn aiohttp websockets python-dotenv edge-tts --break-system-packages -q || echo "   ❌ Error: Pip no encontrado. Corre: sudo apt update && sudo apt install python3-pip -y"; }
python3 -c "import websockets; print('   ✅ websockets OK')" 2>/dev/null \
  || python3 -m pip install websockets --break-system-packages -q 2>/dev/null

# 4. Verificar sintaxis del gateway
echo ""
echo "🔍 Verificando sintaxis de api_gateway.py..."
python3 -m py_compile "$RUNTIME_SRC/brain/api_gateway.py" && echo "   ✅ Sin errores de sintaxis"

# 5. Matar procesos conflictivos
echo ""
echo "🧹 Limpiando procesos anteriores en puertos soberanos..."
lsof -ti:18791 | xargs kill -9 2>/dev/null || true
pkill -9 -f "ecosistema_soberano" 2>/dev/null || true
pkill -9 -f "src/brain/api_gateway.py" 2>/dev/null || true
echo "   ✅ Puertos 18791 liberados (18789 se respeta para el gateway oficial)"

# 6. Construir la UI si hay un dist más antiguo
echo ""
echo "🏗️  Verificando entorno Node.js y build de la UI..."
if ! command -v npm &> /dev/null; then
  echo "   ⚠️  NPM no encontrado. Intentando instalar Node.js..."
  sudo apt update && sudo apt install -y nodejs npm || echo "   ❌ No se pudo instalar Node.js automáticamente."
fi

if [ ! -f "$UI_DIST/index.html" ]; then
  if command -v npm &> /dev/null; then
    echo "   🏗️  Compilando UI..."
    cd "$REPO_ROOT/ui" && npm install -q && npm run build -q
    cd "$REPO_ROOT"
    if [ -f "$UI_DIST/index.html" ]; then
      echo "   ✅ UI compilada con éxito."
    else
      echo "   ❌ Fallo al compilar la UI."
    fi
  else
    echo "   ⚠️  Saltando compilación de UI (NPM no disponible)."
  fi
else
  echo "   ✅ dist/control-ui encontrado"
fi

# 2. Configuración Interactiva (Soberanía)
echo ""
echo "⚙️  CONFIGURACIÓN DEL NÚCLEO SOFIA"
echo "   (Pulsa Enter para usar los valores de respaldo)"
echo ""

DOTENV="$RUNTIME_DIR/.env"
[ -f "$DOTENV" ] && source "$DOTENV"

read -p "   🔑 Telegram Bot Token [${TELEGRAM_BOT_TOKEN:-Respaldo}]: " NEW_TG
read -p "   🔑 Gemini API Key [${GEMINI_API_KEY:-Respaldo}]: " NEW_GEM
read -p "   🔑 DeepSeek API Key [${DEEPSEEK_API_KEY:-Ninguno}]: " NEW_DS
read -p "   🛰️ Ollama Remote URL [${OLLAMA_REMOTE_URL:-http://localhost:11434}]: " NEW_OLLAMA

# Crear .env con los nuevos valores o mantener antiguos
cat > "$DOTENV" << EOF
TELEGRAM_BOT_TOKEN=${NEW_TG:-$TELEGRAM_BOT_TOKEN}
GEMINI_API_KEY=${NEW_GEM:-$GEMINI_API_KEY}
DEEPSEEK_API_KEY=${NEW_DS:-$DEEPSEEK_API_KEY}
OLLAMA_REMOTE_URL=${NEW_OLLAMA:-$OLLAMA_REMOTE_URL}
NODE_NAME=Sofia_VPS
EOF

echo "   ✅ Configuración guardada en $DOTENV"

# 2. Sincronizar código y UI al runtime
echo ""
echo "📂 Sincronizando archivos al runtime ($RUNTIME_DIR)..."
rsync -avq --delete "$REPO_ROOT/src/" "$RUNTIME_SRC/"
if [ -d "$REPO_ROOT/dist" ]; then
  rsync -avq --delete "$REPO_ROOT/dist/" "$RUNTIME_DIR/dist/"
fi
# Ya no sobreescribimos el .env si lo configuramos arriba
# cp -f "$REPO_ROOT/.env" "$RUNTIME_DIR/.env" 2>/dev/null || echo "   ⚠️  .env no encontrado en el repo."

# Verificación de integridad soberana antes del lanzamiento
echo "🔍 Verificando integridad de neuronas en runtime..."
if [ -f "$RUNTIME_SRC/clawcore_system/neuronas/buscador_red.py" ]; then
  echo "   ✅ buscador_red.py presente"
else
  echo "   ❌ ERROR: buscador_red.py NO ENCONTRADO en $RUNTIME_SRC/clawcore_system/neuronas/"
  ls -la "$RUNTIME_SRC/clawcore_system/neuronas/"
fi

echo "   ✅ Sincronización completada."

# 7. Lanzar el Gateway Sofia en background
echo ""
echo "🚀 Iniciando Sofia AI Gateway en puerto 18791..."
cd "$RUNTIME_DIR"
export PYTHONPATH="$RUNTIME_DIR"
nohup python3 "$RUNTIME_SRC/brain/api_gateway.py" \
  > "$RUNTIME_DIR/logs/sofia_gateway.log" 2>&1 &
SOFIA_PID=$!
sleep 5

# 8. Verificar que el gateway levantó
if lsof -ti:18791 > /dev/null 2>&1; then
  echo "   ✅ Sofia Gateway corriendo (PID $SOFIA_PID)"
else
  echo "   ❌ Sofia Gateway no levantó. Ver: $RUNTIME_DIR/logs/sofia_gateway.log"
  tail -20 "$RUNTIME_DIR/logs/sofia_gateway.log"
  exit 1
fi

# 9. Test rápido del endpoint de modelos
echo ""
echo "🧪 Verificando endpoints..."
MODELS_RESP=$(curl -s "http://localhost:18791/v1/models" 2>/dev/null)
if echo "$MODELS_RESP" | grep -q '"active"'; then
  echo "   ✅ GET /v1/models OK"
else
  echo "   ⚠️  GET /v1/models no respondió correctamente"
fi

HEALTH_RESP=$(curl -s "http://localhost:18791/health" 2>/dev/null)
if echo "$HEALTH_RESP" | grep -q '"healthy"'; then
  echo "   ✅ GET /health OK"
fi

# 10. Instrucciones finales
echo ""
echo "──────────────────────────────────────────────────────"
echo "✅ ECOSISTEMA SOBERANO CONFIGURADO Y ACTIVO"
echo ""
echo "  🧠 Sofia AI Dashboard:   http://localhost:18791/sofia"
echo "  📡 Sofia Models API:     http://localhost:18791/v1/models"
echo "  🔱 ClawCore Portal:      http://localhost:18789/__clawcore__/"
echo ""
echo "  📋 Ver logs:  tail -f $RUNTIME_DIR/logs/sofia_gateway.log"
echo "──────────────────────────────────────────────────────"
