import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  resolveDefaultConfigCandidates,
  resolveConfigPathCandidate,
  resolveConfigPath,
  resolveOAuthDir,
  resolveOAuthPath,
  resolveStateDir,
} from "./paths.js";

describe("oauth paths", () => {
  it("prefers CLAWCORE_OAUTH_DIR over CLAWCORE_STATE_DIR", () => {
    const env = {
      CLAWCORE_OAUTH_DIR: "/custom/oauth",
      CLAWCORE_STATE_DIR: "/custom/state",
    } as NodeJS.ProcessEnv;

    expect(resolveOAuthDir(env, "/custom/state")).toBe(path.resolve("/custom/oauth"));
    expect(resolveOAuthPath(env, "/custom/state")).toBe(
      path.join(path.resolve("/custom/oauth"), "oauth.json"),
    );
  });

  it("derives oauth path from CLAWCORE_STATE_DIR when unset", () => {
    const env = {
      CLAWCORE_STATE_DIR: "/custom/state",
    } as NodeJS.ProcessEnv;

    expect(resolveOAuthDir(env, "/custom/state")).toBe(path.join("/custom/state", "credentials"));
    expect(resolveOAuthPath(env, "/custom/state")).toBe(
      path.join("/custom/state", "credentials", "oauth.json"),
    );
  });
});

describe("state + config path candidates", () => {
  it("uses CLAWCORE_STATE_DIR when set", () => {
    const env = {
      CLAWCORE_STATE_DIR: "/new/state",
    } as NodeJS.ProcessEnv;

    expect(resolveStateDir(env, () => "/home/test")).toBe(path.resolve("/new/state"));
  });

  it("uses CLAWCORE_HOME for default state/config locations", () => {
    const env = {
      CLAWCORE_HOME: "/srv/clawcore-home",
    } as NodeJS.ProcessEnv;

    const resolvedHome = path.resolve("/srv/clawcore-home");
    expect(resolveStateDir(env)).toBe(path.join(resolvedHome, ".clawcore"));

    const candidates = resolveDefaultConfigCandidates(env);
    expect(candidates[0]).toBe(path.join(resolvedHome, ".clawcore", "clawcore.json"));
  });

  it("prefers CLAWCORE_HOME over HOME for default state/config locations", () => {
    const env = {
      CLAWCORE_HOME: "/srv/clawcore-home",
      HOME: "/home/other",
    } as NodeJS.ProcessEnv;

    const resolvedHome = path.resolve("/srv/clawcore-home");
    expect(resolveStateDir(env)).toBe(path.join(resolvedHome, ".clawcore"));

    const candidates = resolveDefaultConfigCandidates(env);
    expect(candidates[0]).toBe(path.join(resolvedHome, ".clawcore", "clawcore.json"));
  });

  it("orders default config candidates in a stable order", () => {
    const home = "/home/test";
    const resolvedHome = path.resolve(home);
    const candidates = resolveDefaultConfigCandidates({} as NodeJS.ProcessEnv, () => home);
    const expected = [
      path.join(resolvedHome, ".clawcore", "clawcore.json"),
      path.join(resolvedHome, ".clawcore", "clawdbot.json"),
      path.join(resolvedHome, ".clawcore", "moldbot.json"),
      path.join(resolvedHome, ".clawcore", "moltbot.json"),
      path.join(resolvedHome, ".clawdbot", "clawcore.json"),
      path.join(resolvedHome, ".clawdbot", "clawdbot.json"),
      path.join(resolvedHome, ".clawdbot", "moldbot.json"),
      path.join(resolvedHome, ".clawdbot", "moltbot.json"),
      path.join(resolvedHome, ".moldbot", "clawcore.json"),
      path.join(resolvedHome, ".moldbot", "clawdbot.json"),
      path.join(resolvedHome, ".moldbot", "moldbot.json"),
      path.join(resolvedHome, ".moldbot", "moltbot.json"),
      path.join(resolvedHome, ".moltbot", "clawcore.json"),
      path.join(resolvedHome, ".moltbot", "clawdbot.json"),
      path.join(resolvedHome, ".moltbot", "moldbot.json"),
      path.join(resolvedHome, ".moltbot", "moltbot.json"),
    ];
    expect(candidates).toEqual(expected);
  });

  it("prefers ~/.clawcore when it exists and legacy dir is missing", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "clawcore-state-"));
    try {
      const newDir = path.join(root, ".clawcore");
      await fs.mkdir(newDir, { recursive: true });
      const resolved = resolveStateDir({} as NodeJS.ProcessEnv, () => root);
      expect(resolved).toBe(newDir);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("CONFIG_PATH prefers existing config when present", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "clawcore-config-"));
    try {
      const legacyDir = path.join(root, ".clawcore");
      await fs.mkdir(legacyDir, { recursive: true });
      const legacyPath = path.join(legacyDir, "clawcore.json");
      await fs.writeFile(legacyPath, "{}", "utf-8");

      const resolved = resolveConfigPathCandidate({} as NodeJS.ProcessEnv, () => root);
      expect(resolved).toBe(legacyPath);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("respects state dir overrides when config is missing", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "clawcore-config-override-"));
    try {
      const legacyDir = path.join(root, ".clawcore");
      await fs.mkdir(legacyDir, { recursive: true });
      const legacyConfig = path.join(legacyDir, "clawcore.json");
      await fs.writeFile(legacyConfig, "{}", "utf-8");

      const overrideDir = path.join(root, "override");
      const env = { CLAWCORE_STATE_DIR: overrideDir } as NodeJS.ProcessEnv;
      const resolved = resolveConfigPath(env, overrideDir, () => root);
      expect(resolved).toBe(path.join(overrideDir, "clawcore.json"));
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });
});
