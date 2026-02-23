import { randomUUID } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { discoverClawCorePlugins } from "./discovery.js";

const tempDirs: string[] = [];

function makeTempDir() {
  const dir = path.join(os.tmpdir(), `clawcore-plugins-${randomUUID()}`);
  fs.mkdirSync(dir, { recursive: true });
  tempDirs.push(dir);
  return dir;
}

async function withStateDir<T>(stateDir: string, fn: () => Promise<T>) {
  const prev = process.env.CLAWCORE_STATE_DIR;
  const prevBundled = process.env.CLAWCORE_BUNDLED_PLUGINS_DIR;
  process.env.CLAWCORE_STATE_DIR = stateDir;
  process.env.CLAWCORE_BUNDLED_PLUGINS_DIR = "/nonexistent/bundled/plugins";
  try {
    return await fn();
  } finally {
    if (prev === undefined) {
      delete process.env.CLAWCORE_STATE_DIR;
    } else {
      process.env.CLAWCORE_STATE_DIR = prev;
    }
    if (prevBundled === undefined) {
      delete process.env.CLAWCORE_BUNDLED_PLUGINS_DIR;
    } else {
      process.env.CLAWCORE_BUNDLED_PLUGINS_DIR = prevBundled;
    }
  }
}

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    try {
      fs.rmSync(dir, { recursive: true, force: true });
    } catch {
      // ignore cleanup failures
    }
  }
});

describe("discoverClawCorePlugins", () => {
  it("discovers global and workspace extensions", async () => {
    const stateDir = makeTempDir();
    const workspaceDir = path.join(stateDir, "workspace");

    const globalExt = path.join(stateDir, "extensions");
    fs.mkdirSync(globalExt, { recursive: true });
    fs.writeFileSync(path.join(globalExt, "alpha.js"), "export default function () {}", "utf-8");

    const workspaceExt = path.join(workspaceDir, ".clawcore", "extensions");
    fs.mkdirSync(workspaceExt, { recursive: true });
    fs.writeFileSync(path.join(workspaceExt, "beta.js"), "export default function () {}", "utf-8");

    const { candidates } = await withStateDir(stateDir, async () => {
      return discoverClawCorePlugins({ workspaceDir });
    });

    const ids = candidates.map((c) => c.idHint);
    expect(ids).toContain("alpha");
    expect(ids).toContain("beta");
  });

  it("loads package extension packs", async () => {
    const stateDir = makeTempDir();
    const globalExt = path.join(stateDir, "extensions", "pack");
    fs.mkdirSync(path.join(globalExt, "src"), { recursive: true });

    fs.writeFileSync(
      path.join(globalExt, "package.json"),
      JSON.stringify({
        name: "pack",
        clawcore: { extensions: ["./src/one.js", "./src/two.js"] },
      }),
      "utf-8",
    );
    fs.writeFileSync(
      path.join(globalExt, "src", "one.js"),
      "export default function () {}",
      "utf-8",
    );
    fs.writeFileSync(
      path.join(globalExt, "src", "two.js"),
      "export default function () {}",
      "utf-8",
    );

    const { candidates } = await withStateDir(stateDir, async () => {
      return discoverClawCorePlugins({});
    });

    const ids = candidates.map((c) => c.idHint);
    expect(ids).toContain("pack/one");
    expect(ids).toContain("pack/two");
  });

  it("derives unscoped ids for scoped packages", async () => {
    const stateDir = makeTempDir();
    const globalExt = path.join(stateDir, "extensions", "voice-call-pack");
    fs.mkdirSync(path.join(globalExt, "src"), { recursive: true });

    fs.writeFileSync(
      path.join(globalExt, "package.json"),
      JSON.stringify({
        name: "@clawcore/voice-call",
        clawcore: { extensions: ["./src/index.js"] },
      }),
      "utf-8",
    );
    fs.writeFileSync(
      path.join(globalExt, "src", "index.js"),
      "export default function () {}",
      "utf-8",
    );

    const { candidates } = await withStateDir(stateDir, async () => {
      return discoverClawCorePlugins({});
    });

    const ids = candidates.map((c) => c.idHint);
    expect(ids).toContain("voice-call");
  });

  it("treats configured directory paths as plugin packages", async () => {
    const stateDir = makeTempDir();
    const packDir = path.join(stateDir, "packs", "demo-plugin-dir");
    fs.mkdirSync(packDir, { recursive: true });

    fs.writeFileSync(
      path.join(packDir, "package.json"),
      JSON.stringify({
        name: "@clawcore/demo-plugin-dir",
        clawcore: { extensions: ["./index.js"] },
      }),
      "utf-8",
    );
    fs.writeFileSync(path.join(packDir, "index.js"), "module.exports = {}", "utf-8");

    const { candidates } = await withStateDir(stateDir, async () => {
      return discoverClawCorePlugins({ extraPaths: [packDir] });
    });

    const ids = candidates.map((c) => c.idHint);
    expect(ids).toContain("demo-plugin-dir");
  });
});
