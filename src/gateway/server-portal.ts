import { IncomingMessage, ServerResponse } from "node:http";
import fs from "node:fs";
import path from "node:path";
import { authorizeGatewayConnect, ResolvedGatewayAuth } from "./auth.js";
import { getHeader } from "./http-utils.js";

/**
 * Sofia Assistant Portal
 * Provides a secure landing page for downloading the mobile application.
 */
export async function handlePortalRequest(
  req: IncomingMessage,
  res: ServerResponse,
  opts: {
    auth: ResolvedGatewayAuth;
    trustedProxies: string[];
  }
): Promise<boolean> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const pathname = url.pathname;

  // 1. Route: /sofia (Landing Page)
  if (pathname === "/sofia" || pathname === "/sofia/") {
    const authResult = await checkPortalAuth(req, res, opts);
    if (!authResult.ok) return true; // Handled 401 in checkPortalAuth

    res.statusCode = 200;
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(renderPortalHtml());
    return true;
  }

  // 2. Route: /sofia/download (APK download)
  if (pathname === "/sofia/download") {
    const authResult = await checkPortalAuth(req, res, opts);
    if (!authResult.ok) return true;

    return handleApkDownload(res);
  }

  return false;
}

async function checkPortalAuth(
  req: IncomingMessage,
  res: ServerResponse,
  opts: { auth: ResolvedGatewayAuth; trustedProxies: string[] }
): Promise<{ ok: boolean }> {
  const authHeader = getHeader(req, "authorization");
  if (!authHeader || !authHeader.startsWith("Basic ")) {
    requestBasicAuth(res);
    return { ok: false };
  }

  const otpHeader = getHeader(req, "x-otp");
  const expectedOtp = process.env.SOFA_OTP;
  if (expectedOtp && otpHeader !== expectedOtp) {
    requestBasicAuth(res, "OTP Inválido");
    return { ok: false };
  }

  try {
    const credentials = Buffer.from(authHeader.slice(6), "base64").toString("utf-8");
    const [user, pass] = credentials.split(":");

    // We allow user "sofia" and the configured gateway password
    const authResult = await authorizeGatewayConnect({
      auth: opts.auth,
      connectAuth: { password: pass },
      req,
      trustedProxies: opts.trustedProxies,
    });

    if (!authResult.ok || user.toLowerCase() !== "sofia") {
      requestBasicAuth(res, "Credenciales Inválidas");
      return { ok: false };
    }

    return { ok: true };
  } catch {
    requestBasicAuth(res);
    return { ok: false };
  }
}

function requestBasicAuth(res: ServerResponse, message = "Sofia Assistant Portal") {
  res.statusCode = 401;
  res.setHeader("WWW-Authenticate", `Basic realm="${message}"`);
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.end("Authentication Required");
}

function handleApkDownload(res: ServerResponse): boolean {
  // Standard Gradle build path
  // Resolve APK path dynamically – works on Linux/macOS where the build output may differ
  const possiblePaths = [
    path.resolve("apps/android/app/build/outputs/apk/debug/app-debug.apk"),
    path.resolve("apps/android/app/build/outputs/apk/release/app-release.apk"),
    // Fallback for custom build directories
    path.resolve("apps/android/app/build/outputs/apk/app-debug.apk"),
  ];
  const apkPath = possiblePaths.find((p) => fs.existsSync(p));
  
  if (!apkPath) {
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(`
      <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
          <h1>📦 APK No Encontrado</h1>
          <p>La aplicación Sofia Assistant aún no ha sido compilada.</p>
          <p>Ejecuta <code>./gradlew assembleDebug</code> en <code>apps/android</code> para generarla.</p>
          <br>
          <a href="/sofia" style="color: #6366f1;">Volver al Portal</a>
        </body>
      </html>
    `);
    return true;
  }

  res.statusCode = 200;
  res.setHeader("Content-Type", "application/vnd.android.package-archive");
  res.setHeader("Content-Disposition", 'attachment; filename="SofiaAssistant.apk"');
  
  const stream = fs.createReadStream(apkPath);
  stream.pipe(res);
  return true;
}

function renderPortalHtml() {
  return `
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sofia Assistant | Download Portal</title>
    <style>
        :root {
            --primary: #6366f1;
            --bg: #0f172a;
            --text: #f8fafc;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        .container {
            text-align: center;
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            padding: 3rem;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            max-width: 500px;
            width: 90%;
            position: relative;
        }
        .glow {
            position: absolute;
            top: -50px;
            left: -50px;
            width: 200px;
            height: 200px;
            background: var(--primary);
            filter: blur(80px);
            opacity: 0.2;
            z-index: -1;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 2rem;
        }
        .bot-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            display: inline-block;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .btn {
            display: inline-block;
            background: var(--primary);
            color: white;
            text-decoration: none;
            padding: 1rem 2.5rem;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(99, 102, 241, 0.4);
            filter: brightness(1.1);
        }
        .footer {
            margin-top: 2rem;
            font-size: 0.8rem;
            color: #475569;
        }
    </style>
</head>
<body>
    <div class="glow"></div>
    <div class="container">
        <div class="bot-icon">🤖</div>
        <h1>Sofia Assistant</h1>
        <p>Bienvenido a tu portal de descarga seguro. Accede a tu asistente formal y competente en cualquier lugar.</p>
        
        <a href="/sofia/download" class="btn">Descargar APK</a>
        
        <div class="footer">
            Versión 1.0.21 | Conexión Encriptada E2E
        </div>
    </div>
</body>
</html>
`;
}
