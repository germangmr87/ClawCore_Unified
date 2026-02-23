import fs from "fs";
import { resolve } from "path";
import * as tar from "tar";
import zlib from "zlib";
import { extractArchive } from "./src/infra/archive.js";

async function main() {
  const buf = fs.readFileSync('test/fixtures/hooks-install/npm-pack-hooks.tgz');
  const dir = "test-extract-buffer8";
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  const archivePath = resolve(dir, "archive.tgz");
  fs.writeFileSync(archivePath, buf);

  await extractArchive({ archivePath, destDir: dir, timeoutMs: 10000 });
  console.log("Success extraction!");  
}

main().catch(console.error);
