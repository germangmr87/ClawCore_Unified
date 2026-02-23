# 🗺️ MAPA DE ARQUITECTURA MODULAR (v2.5 - SOBERANA)

## 🛡️ Núcleo ClawCore (ESTE PROYECTO)
- `src/brain/` -> Motores de Inteligencia (Orchestrator, MindReader, RAGPro).
- `src/ui/` -> Portal de Configuración Web (ConfigPortal.ts).
- `src/neurons/` -> Capacidades Autónomas (Vision, Arbitrage, Sensory).
- `src/gateway/` -> Transporte WebSocket (Inmutable).

## 📦 Proyectos Externos (Auditados)
- **ConfMachine:** Localizado en \`/Users/german/ConfgManagerMachine-main\`. 
  - *Estado:* Estable (Build 23).
  - *Relación:* ClawCore actúa como Arquitecto y Auditor externo, NO como parte del código fuente.

## ⚙️ Herramientas y Súper Poderes
- **n8n:** Conocimiento destilado para automatización de negocios.
- **Maxun:** Motor de Web-to-API para ingesta de datos.
- **Vapi & Browser-Use:** Agentes de Voz y Navegación.
