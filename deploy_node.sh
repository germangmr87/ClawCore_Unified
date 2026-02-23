#!/bin/bash
# ClawCore Sovereign Deployer (V5.2 Hybrid)
# Este script asegura una instalación limpia desde el fuente sin parches manuales.

NODE=$1
TOKEN=$2
KEY=$3
IP=$4
USER=$5

echo "🔱 Desplegando Nodo Soberano: $NODE en $IP..."

# 1. Limpieza absoluta
ssh -o StrictHostKeyChecking=no -i /Users/german/.ssh/id_ed25519 ${USER}@${IP} "sudo pkill -9 -f python; sudo rm -rf ~/clawcore_deploy && mkdir -p ~/clawcore_deploy"

# 2. Sincronización de Fuente Maestro
scp -o StrictHostKeyChecking=no -i /Users/german/.ssh/id_ed25519 /Users/german/ClawCore_V5_Modular.tar.gz ${USER}@${IP}:~/

# 3. Instalación y Arranque con Identidad Inyectada
ssh -o StrictHostKeyChecking=no -i /Users/german/.ssh/id_ed25519 ${USER}@${IP} "tar -xzf ~/ClawCore_V5_Modular.tar.gz -C ~/clawcore_deploy && \
export TELEGRAM_BOT_TOKEN='$TOKEN' && \
export DEEPSEEK_API_KEY='$KEY' && \
export NODE_NAME='$NODE' && \
export PYTHONPATH=\$PYTHONPATH:~/clawcore_deploy && \
cd ~/clawcore_deploy && \
screen -dmS clawcore python3 src/clawcore_system/neuronas/interface_telegram.py"

echo "✅ Nodo $NODE desplegado con éxito."
