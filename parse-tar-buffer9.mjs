import fs from "fs";
import { resolve } from "path";
import { installHooksFromNpmSpec } from "./dist/hooks/install.js";

async function run() {
  const dir = "test-extract-buffer9";
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });

  const result = await installHooksFromNpmSpec({
    spec: "@clawcore/test-hooks@0.0.1",
    hooksDir: dir,
  });
  console.log(result);
}

run().catch(console.error);
