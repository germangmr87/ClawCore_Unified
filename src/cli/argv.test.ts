import { describe, expect, it } from "vitest";
import {
  buildParseArgv,
  getFlagValue,
  getCommandPath,
  getPrimaryCommand,
  getPositiveIntFlagValue,
  getVerboseFlag,
  hasHelpOrVersion,
  hasFlag,
  shouldMigrateState,
  shouldMigrateStateFromPath,
} from "./argv.js";

describe("argv helpers", () => {
  it("detects help/version flags", () => {
    expect(hasHelpOrVersion(["node", "clawcore", "--help"])).toBe(true);
    expect(hasHelpOrVersion(["node", "clawcore", "-V"])).toBe(true);
    expect(hasHelpOrVersion(["node", "clawcore", "status"])).toBe(false);
  });

  it("extracts command path ignoring flags and terminator", () => {
    expect(getCommandPath(["node", "clawcore", "status", "--json"], 2)).toEqual(["status"]);
    expect(getCommandPath(["node", "clawcore", "agents", "list"], 2)).toEqual(["agents", "list"]);
    expect(getCommandPath(["node", "clawcore", "status", "--", "ignored"], 2)).toEqual(["status"]);
  });

  it("returns primary command", () => {
    expect(getPrimaryCommand(["node", "clawcore", "agents", "list"])).toBe("agents");
    expect(getPrimaryCommand(["node", "clawcore"])).toBeNull();
  });

  it("parses boolean flags and ignores terminator", () => {
    expect(hasFlag(["node", "clawcore", "status", "--json"], "--json")).toBe(true);
    expect(hasFlag(["node", "clawcore", "--", "--json"], "--json")).toBe(false);
  });

  it("extracts flag values with equals and missing values", () => {
    expect(getFlagValue(["node", "clawcore", "status", "--timeout", "5000"], "--timeout")).toBe(
      "5000",
    );
    expect(getFlagValue(["node", "clawcore", "status", "--timeout=2500"], "--timeout")).toBe(
      "2500",
    );
    expect(getFlagValue(["node", "clawcore", "status", "--timeout"], "--timeout")).toBeNull();
    expect(getFlagValue(["node", "clawcore", "status", "--timeout", "--json"], "--timeout")).toBe(
      null,
    );
    expect(getFlagValue(["node", "clawcore", "--", "--timeout=99"], "--timeout")).toBeUndefined();
  });

  it("parses verbose flags", () => {
    expect(getVerboseFlag(["node", "clawcore", "status", "--verbose"])).toBe(true);
    expect(getVerboseFlag(["node", "clawcore", "status", "--debug"])).toBe(false);
    expect(getVerboseFlag(["node", "clawcore", "status", "--debug"], { includeDebug: true })).toBe(
      true,
    );
  });

  it("parses positive integer flag values", () => {
    expect(getPositiveIntFlagValue(["node", "clawcore", "status"], "--timeout")).toBeUndefined();
    expect(
      getPositiveIntFlagValue(["node", "clawcore", "status", "--timeout"], "--timeout"),
    ).toBeNull();
    expect(
      getPositiveIntFlagValue(["node", "clawcore", "status", "--timeout", "5000"], "--timeout"),
    ).toBe(5000);
    expect(
      getPositiveIntFlagValue(["node", "clawcore", "status", "--timeout", "nope"], "--timeout"),
    ).toBeUndefined();
  });

  it("builds parse argv from raw args", () => {
    const nodeArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["node", "clawcore", "status"],
    });
    expect(nodeArgv).toEqual(["node", "clawcore", "status"]);

    const versionedNodeArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["node-22", "clawcore", "status"],
    });
    expect(versionedNodeArgv).toEqual(["node-22", "clawcore", "status"]);

    const versionedNodeWindowsArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["node-22.2.0.exe", "clawcore", "status"],
    });
    expect(versionedNodeWindowsArgv).toEqual(["node-22.2.0.exe", "clawcore", "status"]);

    const versionedNodePatchlessArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["node-22.2", "clawcore", "status"],
    });
    expect(versionedNodePatchlessArgv).toEqual(["node-22.2", "clawcore", "status"]);

    const versionedNodeWindowsPatchlessArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["node-22.2.exe", "clawcore", "status"],
    });
    expect(versionedNodeWindowsPatchlessArgv).toEqual(["node-22.2.exe", "clawcore", "status"]);

    const versionedNodeWithPathArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["/usr/bin/node-22.2.0", "clawcore", "status"],
    });
    expect(versionedNodeWithPathArgv).toEqual(["/usr/bin/node-22.2.0", "clawcore", "status"]);

    const nodejsArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["nodejs", "clawcore", "status"],
    });
    expect(nodejsArgv).toEqual(["nodejs", "clawcore", "status"]);

    const nonVersionedNodeArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["node-dev", "clawcore", "status"],
    });
    expect(nonVersionedNodeArgv).toEqual(["node", "clawcore", "node-dev", "clawcore", "status"]);

    const directArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["clawcore", "status"],
    });
    expect(directArgv).toEqual(["node", "clawcore", "status"]);

    const bunArgv = buildParseArgv({
      programName: "clawcore",
      rawArgs: ["bun", "src/entry.js", "status"],
    });
    expect(bunArgv).toEqual(["bun", "src/entry.js", "status"]);
  });

  it("builds parse argv from fallback args", () => {
    const fallbackArgv = buildParseArgv({
      programName: "clawcore",
      fallbackArgv: ["status"],
    });
    expect(fallbackArgv).toEqual(["node", "clawcore", "status"]);
  });

  it("decides when to migrate state", () => {
    expect(shouldMigrateState(["node", "clawcore", "status"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "health"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "sessions"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "config", "get", "update"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "config", "unset", "update"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "models", "list"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "models", "status"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "memory", "status"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "agent", "--message", "hi"])).toBe(false);
    expect(shouldMigrateState(["node", "clawcore", "agents", "list"])).toBe(true);
    expect(shouldMigrateState(["node", "clawcore", "message", "send"])).toBe(true);
  });

  it("reuses command path for migrate state decisions", () => {
    expect(shouldMigrateStateFromPath(["status"])).toBe(false);
    expect(shouldMigrateStateFromPath(["config", "get"])).toBe(false);
    expect(shouldMigrateStateFromPath(["models", "status"])).toBe(false);
    expect(shouldMigrateStateFromPath(["agents", "list"])).toBe(true);
  });
});
