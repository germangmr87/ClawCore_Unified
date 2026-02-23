# ✂️ Refactor Plan: integracion_clawcore_evolutivo.py

## 🎯 Objetivos:
1.  **Deprecar Ollama:** Reemplazar `probar_ollama` por `probar_gemini_llmapi`.
2.  **Modularización:** Mover la lógica de reporte a un módulo independiente.
3.  **Soberanía:** Cambiar verificación de ChromaDB por el nuevo `MemoryCore`.

## 🛠️ Archivos afectados:
- `src/brain/integracion_clawcore_evolutivo.py`

## 🧬 Impacto:
Reducción de dependencia cloud en un 50% al centralizar el razonamiento en Gemini 3 Flash y el almacenamiento en local.
