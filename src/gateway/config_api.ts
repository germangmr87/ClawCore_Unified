import * as http from 'http';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';

const CONFIG_PATH = path.resolve(__dirname, '../clawcore_system/neuronas/cerebro_config.json');

function loadCfg(): any {
  try { return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8')); }
  catch { return {}; }
}

function saveCfg(c: any) { fs.writeFileSync(CONFIG_PATH, JSON.stringify(c, null, 2)); }

export function handleGetBrainConfig(_req: http.IncomingMessage, res: http.ServerResponse) {
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(loadCfg()));
}

export function handlePostBrainConfig(req: http.IncomingMessage, res: http.ServerResponse) {
  let body = '';
  req.on('data', (c: Buffer) => (body += c.toString()));
  req.on('end', () => {
    try {
      const inc = JSON.parse(body);
      const merged = { ...loadCfg(), ...inc };
      saveCfg(merged);
      if (inc.use_local === true) {
        exec(`ollama pull ${merged.model_local || 'llama3.2:3b'}`, (err, out) => {
          if (err) console.error('❌ Model download error:', err.message);
          else console.log('✅ Model ready:', out.trim());
        });
      }
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ status: 'ok', config: merged }));
    } catch {
      res.statusCode = 400;
      res.end('Invalid JSON');
    }
  });
}
