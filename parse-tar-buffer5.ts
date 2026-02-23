import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { extractArchive } from "./src/infra/archive.js";

async function run() {
  const tmp = "test-extract-buffer5";
  await fs.rm(tmp, { recursive: true, force: true }).catch(()=>null);
  await fs.mkdir(tmp, { recursive: true });

  const archivePath = path.resolve("test/fixtures/hooks-install/npm-pack-hooks.tgz");
  console.log("Archive exists:", await fs.stat(archivePath).then(()=>true,()=>false));

  try {
    await extractArchive({
      archivePath,
      destDir: tmp,
      timeoutMs: 10000,
    });
    console.log("Extraction complete.");
    const ls = await fs.readdir(path.join(tmp, "package", "hooks", "one-hook"));
    console.log("Hook contents:", ls);
  } catch(e) {
    console.error("Error extracting:", e);
  }
}

run().catch(console.error);
