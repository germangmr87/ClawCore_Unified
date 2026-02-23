import fs from "fs";
import { resolve } from "path";
import * as tar from "tar";

const buffer = fs.readFileSync(resolve("test/fixtures/hooks-install/npm-pack-hooks.tgz"));
console.log("Buffer size:", buffer.byteLength);

const tmp = "test-extract-buffer";
fs.rmSync(tmp, { recursive: true, force: true });
fs.mkdirSync(tmp, { recursive: true });
const targetFile = resolve(tmp, "out.tgz");
fs.writeFileSync(targetFile, buffer);

tar.x({
  file: targetFile,
  cwd: tmp,
  sync: true
});

const hookDir = resolve(tmp, "package", "hooks", "one-hook");
console.log("Extracted files:", fs.readdirSync(hookDir));
