import path from "node:path";
import { describe, expect, it } from "vitest";
import { formatCliCommand } from "./command-format.js";
import { applyCliProfileEnv, parseCliProfileArgs } from "./profile.js";

describe("parseCliProfileArgs", () => {
  it("leaves gateway --dev for subcommands", () => {
    const res = parseCliProfileArgs([
      "node",
      "clawcore",
      "gateway",
      "--dev",
      "--allow-unconfigured",
    ]);
    if (!res.ok) {
      throw new Error(res.error);
    }
    expect(res.profile).toBeNull();
    expect(res.argv).toEqual(["node", "clawcore", "gateway", "--dev", "--allow-unconfigured"]);
  });

  it("still accepts global --dev before subcommand", () => {
    const res = parseCliProfileArgs(["node", "clawcore", "--dev", "gateway"]);
    if (!res.ok) {
      throw new Error(res.error);
    }
    expect(res.profile).toBe("dev");
    expect(res.argv).toEqual(["node", "clawcore", "gateway"]);
  });

  it("parses --profile value and strips it", () => {
    const res = parseCliProfileArgs(["node", "clawcore", "--profile", "work", "status"]);
    if (!res.ok) {
      throw new Error(res.error);
    }
    expect(res.profile).toBe("work");
    expect(res.argv).toEqual(["node", "clawcore", "status"]);
  });

  it("rejects missing profile value", () => {
    const res = parseCliProfileArgs(["node", "clawcore", "--profile"]);
    expect(res.ok).toBe(false);
  });

  it("rejects combining --dev with --profile (dev first)", () => {
    const res = parseCliProfileArgs(["node", "clawcore", "--dev", "--profile", "work", "status"]);
    expect(res.ok).toBe(false);
  });

  it("rejects combining --dev with --profile (profile first)", () => {
    const res = parseCliProfileArgs(["node", "clawcore", "--profile", "work", "--dev", "status"]);
    expect(res.ok).toBe(false);
  });
});

describe("applyCliProfileEnv", () => {
  it("fills env defaults for dev profile", () => {
    const env: Record<string, string | undefined> = {};
    applyCliProfileEnv({
      profile: "dev",
      env,
      homedir: () => "/home/peter",
    });
    const expectedStateDir = path.join(path.resolve("/home/peter"), ".clawcore-dev");
    expect(env.CLAWCORE_PROFILE).toBe("dev");
    expect(env.CLAWCORE_STATE_DIR).toBe(expectedStateDir);
    expect(env.CLAWCORE_CONFIG_PATH).toBe(path.join(expectedStateDir, "clawcore.json"));
    expect(env.CLAWCORE_GATEWAY_PORT).toBe("19001");
  });

  it("does not override explicit env values", () => {
    const env: Record<string, string | undefined> = {
      CLAWCORE_STATE_DIR: "/custom",
      CLAWCORE_GATEWAY_PORT: "19099",
    };
    applyCliProfileEnv({
      profile: "dev",
      env,
      homedir: () => "/home/peter",
    });
    expect(env.CLAWCORE_STATE_DIR).toBe("/custom");
    expect(env.CLAWCORE_GATEWAY_PORT).toBe("19099");
    expect(env.CLAWCORE_CONFIG_PATH).toBe(path.join("/custom", "clawcore.json"));
  });

  it("uses CLAWCORE_HOME when deriving profile state dir", () => {
    const env: Record<string, string | undefined> = {
      CLAWCORE_HOME: "/srv/clawcore-home",
      HOME: "/home/other",
    };
    applyCliProfileEnv({
      profile: "work",
      env,
      homedir: () => "/home/fallback",
    });

    const resolvedHome = path.resolve("/srv/clawcore-home");
    expect(env.CLAWCORE_STATE_DIR).toBe(path.join(resolvedHome, ".clawcore-work"));
    expect(env.CLAWCORE_CONFIG_PATH).toBe(
      path.join(resolvedHome, ".clawcore-work", "clawcore.json"),
    );
  });
});

describe("formatCliCommand", () => {
  it("returns command unchanged when no profile is set", () => {
    expect(formatCliCommand("clawcore doctor --fix", {})).toBe("clawcore doctor --fix");
  });

  it("returns command unchanged when profile is default", () => {
    expect(formatCliCommand("clawcore doctor --fix", { CLAWCORE_PROFILE: "default" })).toBe(
      "clawcore doctor --fix",
    );
  });

  it("returns command unchanged when profile is Default (case-insensitive)", () => {
    expect(formatCliCommand("clawcore doctor --fix", { CLAWCORE_PROFILE: "Default" })).toBe(
      "clawcore doctor --fix",
    );
  });

  it("returns command unchanged when profile is invalid", () => {
    expect(formatCliCommand("clawcore doctor --fix", { CLAWCORE_PROFILE: "bad profile" })).toBe(
      "clawcore doctor --fix",
    );
  });

  it("returns command unchanged when --profile is already present", () => {
    expect(
      formatCliCommand("clawcore --profile work doctor --fix", { CLAWCORE_PROFILE: "work" }),
    ).toBe("clawcore --profile work doctor --fix");
  });

  it("returns command unchanged when --dev is already present", () => {
    expect(formatCliCommand("clawcore --dev doctor", { CLAWCORE_PROFILE: "dev" })).toBe(
      "clawcore --dev doctor",
    );
  });

  it("inserts --profile flag when profile is set", () => {
    expect(formatCliCommand("clawcore doctor --fix", { CLAWCORE_PROFILE: "work" })).toBe(
      "clawcore --profile work doctor --fix",
    );
  });

  it("trims whitespace from profile", () => {
    expect(formatCliCommand("clawcore doctor --fix", { CLAWCORE_PROFILE: "  jbclawcore  " })).toBe(
      "clawcore --profile jbclawcore doctor --fix",
    );
  });

  it("handles command with no args after clawcore", () => {
    expect(formatCliCommand("clawcore", { CLAWCORE_PROFILE: "test" })).toBe(
      "clawcore --profile test",
    );
  });

  it("handles pnpm wrapper", () => {
    expect(formatCliCommand("pnpm clawcore doctor", { CLAWCORE_PROFILE: "work" })).toBe(
      "pnpm clawcore --profile work doctor",
    );
  });
});
