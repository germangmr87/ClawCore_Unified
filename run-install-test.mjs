import { installHooksFromNpmSpec } from './dist/hooks/install.js';
import path from 'path';
import os from 'os';
import { randomUUID } from 'crypto';

async function run() {
  const result = await installHooksFromNpmSpec({
    spec: "@clawcore/test-hooks@0.0.1",
    hooksDir: path.join(os.tmpdir(), randomUUID()),
  });
  console.log(result);
}
run();
