import TelegramBot from 'node-telegram-bot-api';
import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs/promises';
import { execSync } from 'child_process';

dotenv.config();

const config = {
    token: process.env.TELEGRAM_TOKEN,
    apiKey: process.env.LLMAPI_KEY,
    adminId: parseInt(process.env.WHITELIST_ID || '0'),
    version: '5.1.0-sovereign-neural'
};

if (!config.token || !config.apiKey) {
    console.error('❌ Error: Faltan credenciales en el .env');
    process.exit(1);
}

const bot = new TelegramBot(config.token, { polling: true });
const openai = new OpenAI({ apiKey: config.apiKey, baseURL: 'https://internal.llmapi.ai/v1' });

// --- Neural Core Bridge ---
function queryNeuralCore(situation: string): any {
    try {
        const rootDir = path.resolve(__dirname, '..');
        const cmd = `cd "${rootDir}" && python3 -c "
import sys, json; sys.path.insert(0,'.')
from src.clawcore_system.neuronas.neuronas_locales import decidir_autonomamente
r = decidir_autonomamente('${situation.replace(/'/g, "\\'")}', {'recursos_disponibles': True})
print(json.dumps(r, ensure_ascii=False))
"`;
        const result = execSync(cmd, { timeout: 10000, encoding: 'utf-8' });
        return JSON.parse(result.trim());
    } catch (e) {
        return null;
    }
}

function queryVibe(): any {
    try {
        const rootDir = path.resolve(__dirname, '..');
        const cmd = `cd "${rootDir}" && python3 -c "
import sys, json; sys.path.insert(0,'.')
from src.clawcore_system.neuronas.vibe_dashboard import vibe
print(json.dumps(vibe.calcular_vibe(), ensure_ascii=False))
"`;
        return JSON.parse(execSync(cmd, { timeout: 5000, encoding: 'utf-8' }).trim());
    } catch {
        return { vibe: 'DESCONOCIDO', score: 0 };
    }
}

// --- Formateo Seguro ---
async function sendSovereignMessage(chatId: number, text: string) {
    try {
        await bot.sendMessage(chatId, text, { parse_mode: 'Markdown' });
    } catch {
        console.warn('⚠️ Degradando a Texto Plano...');
        await bot.sendMessage(chatId, text);
    }
}

// --- Ojos de Sistema ---
async function leerCodigoPropio(fileName: string): Promise<string | null> {
    try {
        const safePath = path.resolve(process.cwd(), fileName);
        if (!safePath.includes('ClawCore_Unified')) return null;
        let content = await fs.readFile(safePath, 'utf8');
        const MAX_CHARS = 24000; // ~6000 tokens máximo
        if (content.length > MAX_CHARS) {
            content = content.substring(0, MAX_CHARS) + "\n... [CONTENIDO TRUNCADO POR SEGURIDAD Y AHORRO DE TOKENS] ...";
        }
        return content;
    } catch { return null; }
}

// --- Handler Principal ---
bot.on('message', async (msg) => {
    if (msg.chat.id !== config.adminId) return;
    if (!msg.text) return;

    const text = msg.text;

    // Comandos especiales
    if (text === '/status') {
        const v = queryVibe();
        await sendSovereignMessage(msg.chat.id,
            `🔱 *ClawCore ${config.version}*\n` +
            `• Vibe: ${v.emoji || '?'} ${v.vibe} (${v.score})\n` +
            `• Éxito: ${((v.tasa_exito || 0) * 100).toFixed(0)}%\n` +
            `• Uptime: ${v.uptime_s || 0}s`);
        return;
    }

    if (text === '/vibe') {
        const v = queryVibe();
        await sendSovereignMessage(msg.chat.id,
            `${v.emoji || '🙂'} *VIBE: ${v.vibe}*\nScore: ${v.score}\nLatencia: ${v.latencia_media_ms?.toFixed(2)}ms`);
        return;
    }

    if (text === '/brain') {
        try {
            const cfgPath = path.resolve(__dirname, '../clawcore_system/neuronas/cerebro_config.json');
            const cfg = JSON.parse(await fs.readFile(cfgPath, 'utf-8'));
            await sendSovereignMessage(msg.chat.id,
                `🧠 *Cerebro Activo:* ${cfg.use_local ? 'LOCAL (Ollama)' : 'API (Gemini)'}\n` +
                `Modelo local: ${cfg.model_local}\nModelo API: ${cfg.model_api}`);
        } catch {
            await sendSovereignMessage(msg.chat.id, '❌ No se pudo leer config del cerebro.');
        }
        return;
    }

    // 1. Intentar respuesta desde el Neural Core local
    const neural = queryNeuralCore(text);
    if (neural && neural.autonomo && neural.raw) {
        // El núcleo neuronal pudo resolver localmente
        await sendSovereignMessage(msg.chat.id,
            `🔱 *[Decisión Soberana]*\n${neural.raw}\n\n_Confianza: ${(neural.confianza * 100).toFixed(1)}% | Neurona: ${neural.neurona}_`);
        return;
    }

    // 2. Fallback: API externa (Gemini)
    let context = '';
    const fileMatch = text.match(/[a-zA-Z0-9._-]+\.(ts|js|md|py|json)/);
    if (fileMatch) {
        const content = await leerCodigoPropio(fileMatch[0]);
        if (content) context = `\n\n[CONTEXTO DE ARCHIVO]:\n${content}`;
    }

    try {
        const completion = await openai.chat.completions.create({
            model: 'gemini-3-flash-preview',
            messages: [
                { role: 'system', content: `Eres ClawCore V5. Arquitecto Senior. Soberano, eficiente y técnico. Versión: ${config.version}` },
                { role: 'user', content: text + context }
            ],
            temperature: 0.1
        });

        const reply = completion.choices[0].message.content || 'Sin respuesta del núcleo.';
        await sendSovereignMessage(msg.chat.id, reply);
    } catch (e: any) {
        console.error('[CORE]:', e.message);
        await sendSovereignMessage(msg.chat.id, `❌ Error del motor: ${e.message}`);
    }
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('🔱 Apagado soberano del bot...');
    bot.stopPolling();
    process.exit(0);
});

console.log(`🛡️ ClawCore ${config.version} Activado (Neural Core integrado).`);
sendSovereignMessage(config.adminId,
    `🔱 *ClawCore V5.1: Despliegue Neural-Soberano.*\n\n` +
    `Cerebro profundo integrado. Comandos: /status /vibe /brain`);
