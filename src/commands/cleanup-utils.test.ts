import path from "node:path";
import { describe, expect, it, test } from "vitest";
import type { ClawCoreConfig } from "../config/config.js";
import { buildCleanupPlan } from "./cleanup-utils.js";
import { applyAgentDefaultPrimaryModel } from "./model-default.js";

describe("buildCleanupPlan", () => {
  test("resolves inside-state flags and workspace dirs", () => {
    const tmpRoot = path.join(path.parse(process.cwd()).root, "tmp");
    const cfg = {
      agents: {
        defaults: { workspace: path.join(tmpRoot, "clawcore-workspace-1") },
        list: [{ workspace: path.join(tmpRoot, "clawcore-workspace-2") }],
      },
    };
    const plan = buildCleanupPlan({
      cfg: cfg as unknown as ClawCoreConfig,
      stateDir: path.join(tmpRoot, "clawcore-state"),
      configPath: path.join(tmpRoot, "clawcore-state", "clawcore.json"),
      oauthDir: path.join(tmpRoot, "clawcore-oauth"),
    });

    expect(plan.configInsideState).toBe(true);
    expect(plan.oauthInsideState).toBe(false);
    expect(new Set(plan.workspaceDirs)).toEqual(
      new Set([
        path.join(tmpRoot, "clawcore-workspace-1"),
        path.join(tmpRoot, "clawcore-workspace-2"),
      ]),
    );
  });
});

describe("applyAgentDefaultPrimaryModel", () => {
  it("does not mutate when already set", () => {
    const cfg = { agents: { defaults: { model: { primary: "a/b" } } } } as ClawCoreConfig;
    const result = applyAgentDefaultPrimaryModel({ cfg, model: "a/b" });
    expect(result.changed).toBe(false);
    expect(result.next).toBe(cfg);
  });

  it("normalizes legacy models", () => {
    const cfg = { agents: { defaults: { model: { primary: "legacy" } } } } as ClawCoreConfig;
    const result = applyAgentDefaultPrimaryModel({
      cfg,
      model: "a/b",
      legacyModels: new Set(["legacy"]),
    });
    expect(result.changed).toBe(false);
    expect(result.next).toBe(cfg);
  });
});
