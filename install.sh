#!/usr/bin/env bash
# ============================================================
#   ClawCore — Instalador Universal
#   macOS · Linux
#   Uso: curl -fsSL https://raw.githubusercontent.com/germangmr87/openclaw/main/install.sh | bash
# ============================================================
set -euo pipefail

REPO_URL="https://github.com/germangmr87/openclaw.git"
INSTALL_DIR="$HOME/.clawcore"
VERSION="2026.2.22"

# ── Colores ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Helpers ───────────────────────────────────────────────
print_header() {
  echo ""
  echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}${BOLD}║       🦞  ClawCore Installer v${VERSION}    ║${NC}"
  echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${NC}"
  echo ""
}

step() { echo -e "\n${BLUE}${BOLD}▶ $1${NC}"; }
ok()   { echo -e "${GREEN}  ✓ $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠ $1${NC}"; }
err()  { echo -e "${RED}  ✗ $1${NC}"; exit 1; }
ask()  { echo -e "${BOLD}  → $1${NC}"; }

# ── Detectar OS ───────────────────────────────────────────
detect_os() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
  elif [[ "$OSTYPE" == "linux"* ]]; then
    OS="linux"
    if command -v apt-get &>/dev/null; then DISTRO="debian"
    elif command -v dnf &>/dev/null;   then DISTRO="fedora"
    elif command -v pacman &>/dev/null; then DISTRO="arch"
    else DISTRO="unknown"; fi
  else
    err "Sistema operativo no soportado: $OSTYPE"
  fi
}

# ── Verificar / instalar Node.js ──────────────────────────
check_node() {
  step "Verificando Node.js..."
  if command -v node &>/dev/null; then
    NODE_VER=$(node --version | sed 's/v//' | cut -d. -f1)
    if [[ "$NODE_VER" -ge 22 ]]; then
      ok "Node.js $(node --version) detectado"
      return
    else
      warn "Node.js $(node --version) es muy antiguo. Se requiere v22+."
    fi
  else
    warn "Node.js no encontrado."
  fi

  # Instalar via nvm
  echo ""
  ask "¿Instalar Node.js v22 automáticamente? (S/n): "
  read -r INSTALL_NODE
  if [[ "${INSTALL_NODE:-s}" =~ ^[Ss]$ ]] || [[ -z "${INSTALL_NODE}" ]]; then
    step "Instalando NVM + Node.js v22..."
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    # shellcheck source=/dev/null
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    nvm install 22 && nvm use 22 && nvm alias default 22
    ok "Node.js $(node --version) instalado"
  else
    err "Node.js v22+ es requerido. Instálalo desde https://nodejs.org"
  fi
}

# ── Verificar / instalar pnpm ─────────────────────────────
check_pnpm() {
  step "Verificando pnpm..."
  if command -v pnpm &>/dev/null; then
    ok "pnpm $(pnpm --version) detectado"
    return
  fi
  warn "pnpm no encontrado. Instalando..."
  npm install -g pnpm
  pnpm setup 2>/dev/null || true
  export PNPM_HOME="$HOME/.local/share/pnpm"
  [[ "$OS" == "macos" ]] && PNPM_HOME="$HOME/Library/pnpm"
  export PATH="$PNPM_HOME:$PATH"
  ok "pnpm instalado"
}

# ── Clonar o actualizar el repo ───────────────────────────
install_repo() {
  step "Instalando ClawCore en $INSTALL_DIR..."
  if [[ -d "$INSTALL_DIR/.git" ]]; then
    warn "Instalación existente detectada. Actualizando..."
    git -C "$INSTALL_DIR" pull --rebase origin main
    ok "Repositorio actualizado"
  else
    git clone "$REPO_URL" "$INSTALL_DIR"
    ok "Repositorio clonado en $INSTALL_DIR"
  fi
}

# ── Instalar dependencias y compilar ─────────────────────
build_project() {
  step "Instalando dependencias JS..."
  cd "$INSTALL_DIR"
  pnpm install --frozen-lockfile 2>/dev/null || pnpm install --no-frozen-lockfile
  ok "Dependencias instaladas"

  step "Compilando ClawCore..."
  pnpm build
  ok "Build completado"
}

# ── Configuración interactiva ─────────────────────────────
configure() {
  step "Configuración inicial"
  echo ""

  ENV_FILE="$INSTALL_DIR/.env"

  if [[ -f "$ENV_FILE" ]]; then
    warn "Ya existe un archivo .env en $ENV_FILE"
    ask "¿Reconfigurar? (s/N): "
    read -r RECONF
    if [[ ! "${RECONF:-n}" =~ ^[Ss]$ ]]; then
      ok "Usando configuración existente"
      return
    fi
  fi

  echo -e "\n${BOLD}  Necesito algunos datos para configurar tu asistente:${NC}\n"

  # Telegram Token
  ask "Token de Telegram (de @BotFather) — deja vacío para omitir:"
  read -r TELEGRAM_TOKEN

  # OpenAI / Anthropic
  ask "OpenAI API Key — deja vacío para omitir:"
  read -r OPENAI_KEY

  ask "Anthropic API Key — deja vacío para omitir:"
  read -r ANTHROPIC_KEY

  # Gemini
  ask "Gemini API Key — deja vacío para omitir:"
  read -r GEMINI_KEY

  # Puerto del gateway
  ask "Puerto del Gateway (por defecto: 18789):"
  read -r GATEWAY_PORT
  GATEWAY_PORT="${GATEWAY_PORT:-18789}"

  # Crear .env
  cat > "$ENV_FILE" <<EOF
# ClawCore — Configuración generada el $(date)

# ── Telegram ──────────────────────────
TELEGRAM_TOKEN=${TELEGRAM_TOKEN:-}

# ── Modelos de IA ─────────────────────
OPENAI_API_KEY=${OPENAI_KEY:-}
ANTHROPIC_API_KEY=${ANTHROPIC_KEY:-}
GEMINI_API_KEY=${GEMINI_KEY:-}

# ── Gateway ───────────────────────────
CLAWCORE_GATEWAY_PORT=${GATEWAY_PORT}
EOF

  ok ".env creado en $ENV_FILE"
}

# ── Agregar alias al shell ────────────────────────────────
setup_path() {
  step "Configurando acceso desde la terminal..."

  SHELL_RC="$HOME/.zshrc"
  [[ "$SHELL" == *"bash"* ]] && SHELL_RC="$HOME/.bashrc"

  ALIAS_LINE="alias clawcore='node $INSTALL_DIR/clawcore.mjs'"

  if grep -qF "alias clawcore=" "$SHELL_RC" 2>/dev/null; then
    ok "Alias 'clawcore' ya configurado en $SHELL_RC"
  else
    echo "" >> "$SHELL_RC"
    echo "# ClawCore" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    ok "Alias agregado a $SHELL_RC"
  fi

  # Aplicar en la sesión actual
  eval "$ALIAS_LINE" 2>/dev/null || true
}

# ── Registrar como servicio ───────────────────────────────
setup_service() {
  step "Configuración de inicio automático"
  echo ""
  ask "¿Iniciar ClawCore automáticamente con el sistema? (S/n): "
  read -r SETUP_SVC
  if [[ ! "${SETUP_SVC:-s}" =~ ^[Ss]$ ]] && [[ -n "${SETUP_SVC}" ]]; then
    warn "Omitiendo servicio de inicio automático"
    return
  fi

  if [[ "$OS" == "macos" ]]; then
    _setup_launchd
  else
    _setup_systemd
  fi
}

_setup_launchd() {
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_FILE="$PLIST_DIR/ai.clawcore.gateway.plist"
  mkdir -p "$PLIST_DIR"
  NODE_BIN=$(command -v node)

  cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ai.clawcore.gateway</string>
  <key>ProgramArguments</key>
  <array>
    <string>${NODE_BIN}</string>
    <string>${INSTALL_DIR}/clawcore.mjs</string>
    <string>gateway</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${INSTALL_DIR}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${HOME}/.clawcore/logs/gateway.log</string>
  <key>StandardErrorPath</key>
  <string>${HOME}/.clawcore/logs/gateway.err</string>
</dict>
</plist>
EOF

  mkdir -p "$HOME/.clawcore/logs"
  launchctl unload "$PLIST_FILE" 2>/dev/null || true
  launchctl load -w "$PLIST_FILE"
  ok "Servicio launchd registrado → se iniciará automáticamente con macOS"
  ok "Logs en: ~/.clawcore/logs/gateway.log"
}

_setup_systemd() {
  if ! command -v systemd &>/dev/null && ! systemctl --version &>/dev/null 2>&1; then
    warn "systemd no encontrado. Omitiendo servicio automático."
    return
  fi

  NODE_BIN=$(command -v node)
  SERVICE_FILE="$HOME/.config/systemd/user/clawcore.service"
  mkdir -p "$(dirname "$SERVICE_FILE")"
  mkdir -p "$HOME/.clawcore/logs"

  cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=ClawCore Gateway
After=network.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStart=${NODE_BIN} ${INSTALL_DIR}/clawcore.mjs gateway
Restart=always
RestartSec=5
StandardOutput=append:${HOME}/.clawcore/logs/gateway.log
StandardError=append:${HOME}/.clawcore/logs/gateway.err

[Install]
WantedBy=default.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now clawcore
  ok "Servicio systemd registrado → se iniciará con la sesión de usuario"
  ok "Estado: systemctl --user status clawcore"
  ok "Logs: journalctl --user -u clawcore -f"
}

# ── Resumen final ─────────────────────────────────────────
print_summary() {
  echo ""
  echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}${BOLD}║     ✅  ClawCore instalado con éxito     ║${NC}"
  echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "  ${BOLD}Comandos disponibles:${NC}"
  echo -e "  ${CYAN}source ~/.zshrc${NC}              # activar en esta terminal"
  echo -e "  ${CYAN}clawcore gateway${NC}             # iniciar el gateway"
  echo -e "  ${CYAN}clawcore --version${NC}           # verificar versión"
  echo -e "  ${CYAN}clawcore onboard${NC}             # asistente de configuración"
  echo ""
  echo -e "  ${BOLD}Logs:${NC}"
  echo -e "  ${CYAN}~/.clawcore/logs/gateway.log${NC}"
  echo ""
  echo -e "  ${BOLD}Reinstalar / actualizar:${NC}"
  echo -e "  ${CYAN}curl -fsSL https://raw.githubusercontent.com/germangmr87/openclaw/main/install.sh | bash${NC}"
  echo ""
}

# ── Main ──────────────────────────────────────────────────
main() {
  print_header
  detect_os
  check_node
  check_pnpm
  install_repo
  build_project
  configure
  setup_path
  setup_service
  print_summary
}

main "$@"
