# 🧠 ClawCore Infinite Memory (RAG Index)

Este archivo (y el directorio `memory/`) sirve como la memoria a largo plazo y persistente de ClawCore. Según el **Protocolo de Memoria Infinita** en `SOUL.md`, es mandatorio mantener este índice actualizado.

## 📝 Protocolo de Registro (Auto-Documentación RAG)
Cada vez que el Agente o Arquitecto diseñe, programe o modifique una funcionalidad clave, debe agregarse un bloque descriptivo en este archivo o en la subcarpeta `memory/` bajo el siguiente formato. **Esto asegura que la herramienta `memory_search` recupere literalmente las respuestas técnicas exactas sin alucinaciones:**

```markdown
### [Nombre del Módulo o Funcionalidad] - [Fecha]
- **Propósito**: ¿Para qué sirve?
- **Ubicación**: Rutas de archivos fuente principales (ej. `src/infra/token-store.ts`)
- **Dependencias/Herramientas**: ¿Se crearon en conjunto con llamadas a la DB? ¿Dependen de un Tool?
- **Decisiones Arquitectónicas Clave**: ¿Por qué se hizo así? (Ese detalle que se olvidaría en 2 meses).
```

---

## 📖 Registros Históricos (Knowledge Base)

### Memoria Infinita de Tokens (Token Store Persistence) - 22 Feb 2026
- **Propósito**: Dotar al sistema Gateway de "memoria infinita" para la generación y retención de tokens persistentes entre reinicios de la máquina, sin perder la velocidad del servidor ni romper el Primary Auth del gateway actual.
- **Ubicación**: 
  - `src/infra/token-store.ts` (Nuevo módulo gestor)
  - `src/gateway/auth.ts` (Validación paralela inyectada)
- **Dependencias/Herramientas**: Almacén JSON en disco (`data/tokens.json`) más cache atómica en memoria (`Map`).
- **Decisiones Arquitectónicas Clave**: Se diseñó al estilo iterativo blindado (`safeEqualSecret`) contra timing-attacks. El sistema intenta logearte con el token fijo del `.env` y, si falla, escanea el repositorio JSON persistente. Esto desacopla a ClawCore: su gestor auth principal no se vuelve un cuello de botella para tokens de App temporales.

### Portal de Descarga Segura: Sofia Assistant - 21 Feb 2026
- **Propósito**: Proveer un portal UI público bajo las rutas `/sofia` y `/sofia/download` para distribuir el APK del bot (Android) usando medidas extremas de seguridad (HSTS, CSP).
- **Ubicación**: 
  - `src/gateway/server-portal.ts`
  - `src/gateway/server-http.ts` (Interceptando la carga del portal antes del 404).
- **Dependencias/Herramientas**: Render renderiza HTML directamente en texto de respuesta con doble capa TLS si provees `CLAWCORE_TLS_CERT`.
- **Decisiones Arquitectónicas Clave**: 
  1. MFA: 2-Factor Authentication para descargas. Aparte del usuario "sofia", pide validación del header `x-otp` usando `process.env.SOFA_OTP`.
  2. Búsqueda Multi-OS del `.apk`: Intenta buscar el APK ensamblado dinámicamente mediante `fs` en rutas relativas probables previniendo crashes por distintos path Linux/Mac.
