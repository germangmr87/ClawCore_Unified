#!/usr/bin/env bash
# ============================================================
#   ClawCore — Instalador Universal
#   Uso: curl -fsSL https://raw.githubusercontent.com/germangmr87/ClawCore_Unified/main/install.sh | bash
# ============================================================
set -euo pipefail

REPO_URL="https://github.com/germangmr87/ClawCore_Unified.git"
INSTALL_DIR="$HOME/.clawcore"

# ── Colores ───────────────────────────────────────────────
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'

step() { echo -e "\n${CYAN}${BOLD}▶ $1${NC}"; }
ok()   { echo -e "${GREEN}  ✓ $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠ $1${NC}"; }
err()  { echo -e "${RED}  ✗ $1${NC}"; exit 1; }

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║     🦞  ClawCore Installer          ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""

# ── 1. Node.js ≥ 22 ──────────────────────────────────────
step "Verificando Node.js..."
if ! command -v node &>/dev/null; then
  warn "Node.js no encontrado. Instalando v22 via nvm..."
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  nvm install 22 && nvm use 22 && nvm alias default 22
fi

NODE_VER=$(node --version | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_VER" -lt 22 ]]; then
  err "Se requiere Node.js v22+. Tu versión: $(node --version). Actualiza en https://nodejs.org"
fi
ok "Node.js $(node --version)"

# ── 2. pnpm ───────────────────────────────────────────────
step "Verificando pnpm..."
if ! command -v pnpm &>/dev/null; then
  warn "pnpm no encontrado. Instalando..."
  npm install -g pnpm
  export PATH="$HOME/Library/pnpm:$HOME/.local/share/pnpm:$PATH"
fi
ok "pnpm $(pnpm --version)"

# ── 3. Clonar o actualizar ────────────────────────────────
step "Obteniendo ClawCore..."
if [[ -d "$INSTALL_DIR/.git" ]]; then
  warn "Actualizando instalación existente..."
  git -C "$INSTALL_DIR" pull --rebase origin main
  ok "Actualizado"
else
  [[ -d "$INSTALL_DIR" ]] && rm -rf "$INSTALL_DIR"
  git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
  ok "Clonado en $INSTALL_DIR"
fi

# ── 4. Build ──────────────────────────────────────────────
step "Compilando..."
cd "$INSTALL_DIR"
pnpm install --frozen-lockfile 2>/dev/null || pnpm install --no-frozen-lockfile
pnpm build
ok "Build completado"

# ── 5. Alias permanente ───────────────────────────────────
step "Configurando comando 'clawcore'..."
SHELL_RC="$HOME/.zshrc"
[[ "$SHELL" == *bash* ]] && SHELL_RC="$HOME/.bashrc"
ALIAS_LINE="alias clawcore='node $INSTALL_DIR/clawcore.mjs'"
if ! grep -qF "alias clawcore=" "$SHELL_RC" 2>/dev/null; then
  { echo ""; echo "# ClawCore"; echo "$ALIAS_LINE"; } >> "$SHELL_RC"
fi
eval "$ALIAS_LINE"   # activo en esta sesión también
ok "Comando 'clawcore' disponible"

# ── 6. Lanzar onboarding ──────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅ Instalación completa. Iniciando configuración...${NC}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════${NC}"
echo ""

exec node "$INSTALL_DIR/clawcore.mjs" onboard --install-daemon
