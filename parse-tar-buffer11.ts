import fs from "fs";
import { resolve } from "path";
import { installHooksFromNpmSpec } from "./src/hooks/install.js";

async function run() {
  const tmpDir = "test-extract-buffer11";
  fs.rmSync(tmpDir, { recursive: true, force: true });
  fs.mkdirSync(tmpDir, { recursive: true });

  const result = await installHooksFromNpmSpec({
    spec: "@clawcore/test-hooks@0.0.1",
    hooksDir: tmpDir,
  });
  console.log(result);
}

run().catch(console.error);
