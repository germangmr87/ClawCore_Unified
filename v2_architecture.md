# 🏗️ Arquitectura ClawCore v2.0 (Real)

## 🎼 Orchestrator (Cerebro Central)
Desacoplado del transporte. Decide el flujo de ejecución:
1.  **Crítico:** Guardian.ts (Auto-sanación).
2.  **Local (0 tokens):** NanoInfer.ts (Lógica axiomática).
3.  **Cloud (Avanzado):** Router.ts (Gemini 3 Flash).

## 🌉 Brain Bridge
Módulo que traduce el tráfico del Gateway (WebSocket) al lenguaje del Orchestrator. 
**Regla:** Si el Gateway se cae, el cerebro sigue vivo en local.

## 📉 Protocolo de Austeridad
- Máximo 300 tokens de razonamiento por tarea atómica.
- Uso prioritario de NanoInfer para respuestas de estatus e identidad.
