import * as tar from "tar";
import fs from "fs";
import path from "path";
const file = "test/fixtures/hooks-install/npm-pack-hooks.tgz";
const cwd = "test-extract";
fs.mkdirSync(cwd, { recursive: true });
await tar.x({
  file,
  cwd,
  onReadEntry(entry) {
    console.log("reading", entry.path);
  }
});
console.log("Files:", fs.readdirSync(cwd));
const hooksDir = path.join(cwd, "package/hooks/one-hook");
console.log("Hooks Files:", fs.readdirSync(hooksDir));
