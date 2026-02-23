# Plan para Implementar Memoria Vectorial (RAG) en ClawCore

## 🎯 Objetivo
Dotar a los agentes de ClawCore de "memoria a largo plazo" real y textual. Actualmente, el sistema comprime las conversaciones largas en resúmenes semánticos (`src/agents/compaction.ts`) para evitar desbordar la ventana de contexto. Con este plan, los agentes podrán consultar el historial *crudo* mediante una herramienta de búsqueda vectorial, recuperando la exactitud que se pierde en la compresión.

## 🏗 Arquitectura Propuesta

1. **Base de Datos Vectorial Local (Embeddings)**
   - Utilizaremos una solución ligera, embebida y sin dependencias pesadas de servidor externo. Opciones ideales para el ecosistema Node.js/TypeScript:
     - **SQLite con extensión VSS/Vector** (ideal para no añadir dependencias externas masivas).
     - **HNSWLib** o un wrapper directo en node, o simplemente almacenamiento JSON estructurado + búsqueda por similitud de coseno en memoria si el historial no escala a millones de mensajes (una primera fase).
   
2. **Generación de Embeddings**
   - Integrar un modelo de embeddings ligero y local (como `all-MiniLM-L6-v2` vía ONNX Runtime Web / Transformers.js o llamadas a un endpoint API configurado como OpenAI `text-embedding-3-small` / Ollama).
   - *Ganador sugerido para fase 1:* API de Embeddings configurada en los providers, similar a la lógica actual de LLMs.

3. **Ingesta Transparente (Indexador)**
   - Hook/Interceptor en el ciclo de vida del chat (ej. donde se agrega a `session-utils.fs.ts`).
   - Cada vez que se graba un bloque de mensajes (> N tokens), se asíncronamente genera su embedding y se guarda en la base vectorial anexando el `sessionId`.

4. **Nueva Herramienta (Tool) para el Agente (`search_long_term_memory`)**
   - Una herramienta que el LLM puede invocar en su JSON: `{"name": "search_long_term_memory", "parameters": {"query": "código de validación de tokens de ayer"}}`.
   - La herramienta busca los N bloques más cercanos y los devuelve preformateados como resultado de la herramienta.

## 🛠 Pasos de Implementación (Fases)

### Fase 1: Motor de Almacenamiento Vectorial y Embebidos
- [ ] Definir interfaz `VectorStore` con operaciones `indexChunk(sessionId, id, text)` y `search(sessionId, queryVector, limit)`.
- [ ] Implementar la clase concreta (ej. SQLite o una persistencia basada en índices en disco).
- [ ] Agregar el cliente de embeddings (`EmbeddingProvider`) al sistema de proveedores de ClawCore.

### Fase 2: Hook de Indexación del Historial
- [ ] Modificar el cierre de la solicitud o la compresión en sí para que, en lugar/además de comprimir, los fragmentos se envíen al indexador vectorial.
- [ ] Procesamiento de fragmentación (Text Chunking): Separar los mensajes muy densos (como archivos de código completos de 400 líneas) en trozos semánticamente útiles.

### Fase 3: Instrumentar la "Tool"
- [ ] Crear el esquema de la herramienta `search_memory` (o similar) e inyectarla por defecto en las habilidades base del agente Proactivo/Arquitecto.
- [ ] Instruir en el prompt del sistema: `"Si necesitas recordar detalles exactos, código o datos de días/sesiones anteriores que parecen estar resumidos o escasos de información, usa la herramienta search_memory para recuperarlos."`

### Fase 4: Pruebas y Retroalimentación
- [ ] Escribir E2E tests inyectando un mensaje gigante al principio del chat y obligando al agente a hacer RAG.
- [ ] Evaluar tiempos de latencia y costo de tokens.

---

## 🚀 Próxima Acción Inmediata
Decidir la tecnología subyacente de la Base Vectorial:
- **A.** ¿Usamos un proveedor en la nube / modelo externo para los embeddings (ej. API de OpenAI u Ollama local)?
- **B.** ¿Persistimos los vectores en un archivo JSON crudo (para prototipado rápido) o instalamos una abstracción madura como `vectra` (librería super ligera para Node) o SQLite local?
