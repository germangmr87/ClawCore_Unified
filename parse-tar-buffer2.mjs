import fs from "fs";
import { resolve } from "path";
import * as tar from "tar";
import zlib from "zlib";

const buffer = fs.readFileSync(resolve("test/fixtures/hooks-install/npm-pack-hooks.tgz"));

const tmp = "test-extract-buffer2";
fs.rmSync(tmp, { recursive: true, force: true });
fs.mkdirSync(tmp, { recursive: true });

const tmpFile = resolve(tmp, "archive.tar");
fs.writeFileSync(tmpFile, zlib.unzipSync(buffer));

tar.x({
  file: tmpFile,
  cwd: tmp,
  sync: true
});

const hookDir = resolve(tmp, "package", "hooks", "one-hook");
console.log("Extracted files:", fs.readdirSync(hookDir));
