import { runSecurityAudit } from './dist/security/audit.js';
import path from 'path';
import fs from 'fs/promises';

async function main() {
  const tmp = '/tmp/clawcore-test-extensions-no-allowlist-' + Date.now();
  const stateDir = path.join(tmp, "state");
  await fs.mkdir(path.join(stateDir, "extensions", "some-plugin"), {
    recursive: true,
    mode: 0o700,
  });

  const res = await runSecurityAudit({
    config: {},
    includeFilesystem: true,
    includeChannelSecurity: false,
    stateDir,
    configPath: path.join(stateDir, "clawcore.json"),
  });

  console.log(JSON.stringify(res.findings, null, 2));
}

main().catch(console.error);
