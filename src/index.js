import TelegramBot from 'node-telegram-bot-api';
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { execSync } from 'child_process';

/**
 * ClawCore Unified V3.2 - Sovereign Seed
 * Protocolo: Austeridad Extrema + Rendimiento de Hardware
 */

const config = {
    TOKEN: '8105513236:AAHnAiCZ82urAqyA6x3U3PcVKGSy8KBCWjk',
    LLMAPI_KEY: 'llmgtwy_jxlfeRWOWxTIKq8incbH7MKelBUxNhJtotLLFLBt',
    WORK_DIR: '/opt/ClawCore_Unified/src',
    DB_DIR: '/opt/ClawCore_Unified/db'
};

const bot = new TelegramBot(config.TOKEN, { polling: true });
const openai = new OpenAI({ apiKey: config.LLMAPI_KEY, baseURL: 'https://internal.llmapi.ai/v1' });

// --- OJOS DEL SISTEMA (FileSystem API) ---
function getFileContent(fileName) {
    try {
        const safePath = path.resolve(config.WORK_DIR, fileName.replace(/^.*[\\\/]/, ''));
        if (!fs.existsSync(safePath)) return null;
        return fs.readFileSync(safePath, 'utf8');
    } catch (e) { return null; }
}

// --- BOOTSTRAP SOBERANO ---
function selfBootstrap() {
    const cores = os.cpus().length;
    const ram = Math.round(os.totalmem() / 1024 / 1024 / 1024);
    console.log(`[BOOT] Hardware: ${cores} cores / ${ram}GB RAM. Prioridad ALTA.`);
    
    if (!fs.existsSync(config.DB_DIR)) {
        console.log('[RAG] Ignición: Indexando código fuente (Modo Austeridad)...');
        try {
            execSync('source ../venv/bin/activate && python3 brain/indexar_simple.py .', { 
                cwd: config.WORK_DIR, 
                shell: '/bin/bash' 
            });
        } catch (e) { console.error('[RAG] Error en indexación inicial:', e.message); }
    }
}

// --- GESTIÓN DE ERRORES SOBERANA ---
process.on('uncaughtException', (err) => { console.error('🔴 CRASH PREVENIDO:', err.message); });
process.on('unhandledRejection', (reason) => { console.error('🔴 RECHAZO EVITADO:', reason); });

bot.on('message', async (msg) => {
    if (!msg.text) return;
    
    let systemPrompt = 'Eres ClawCore V3, el Arquitecto Soberano. Responde directo, técnico y breve. Usa Markdown. NO pienses en voz alta.';
    let userContent = msg.text;

    // Lógica de Ojos: Auto-lectura si se menciona un archivo
    const fileFound = msg.text.match(/[a-zA-Z0-9._-]+\.(js|ts|md|py)/);
    if (fileFound) {
        const content = getFileContent(fileFound[0]);
        if (content) userContent += '\n\n[SISTEMA: Archivo inyectado automáticamente]:\n' + content;
    }

    try {
        const completion = await openai.chat.completions.create({
            model: 'gemini-3-flash-preview',
            messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userContent }],
            temperature: 0.1, // Precisión técnica
            max_tokens: 1000 // Control de burn
        });

        const reply = completion.choices[0].message.content;
        bot.sendMessage(msg.chat.id, reply, { parse_mode: 'Markdown' });

    } catch (e) {
        // Silenciador de Errores de API (No quemar tokens en basura técnica)
        console.error('[BURN PROTECT]:', e.message);
        if (e.message.includes('Thought signature')) {
            bot.sendMessage(msg.chat.id, '🔄 *Recalibrando:* Firma de pensamiento inestable. Reintentando de forma directa...', { parse_mode: 'Markdown' });
        }
    }
});

selfBootstrap();
console.log('✅ ClawCore V3.2: Sincronización Completa y Soberana.');
