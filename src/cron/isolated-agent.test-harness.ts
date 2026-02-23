import fs from "node:fs/promises";
import path from "node:path";
import type { ClawCoreConfig } from "../config/config.js";
import type { CronJob } from "./types.js";
import { withTempHome as withTempHomeBase } from "../../test/helpers/temp-home.js";

export async function withTempCronHome<T>(fn: (home: string) => Promise<T>): Promise<T> {
  return withTempHomeBase(fn, { prefix: "clawcore-cron-" });
}

export async function writeSessionStore(
  home: string,
  session: { lastProvider: string; lastTo: string; lastChannel?: string },
): Promise<string> {
  const dir = path.join(home, ".clawcore", "sessions");
  await fs.mkdir(dir, { recursive: true });
  const storePath = path.join(dir, "sessions.json");
  await fs.writeFile(
    storePath,
    JSON.stringify(
      {
        "agent:main:main": {
          sessionId: "main-session",
          updatedAt: Date.now(),
          ...session,
        },
      },
      null,
      2,
    ),
    "utf-8",
  );
  return storePath;
}

export function makeCfg(
  home: string,
  storePath: string,
  overrides: Partial<ClawCoreConfig> = {},
): ClawCoreConfig {
  const base: ClawCoreConfig = {
    agents: {
      defaults: {
        model: "anthropic/claude-opus-4-5",
        workspace: path.join(home, "clawcore"),
      },
    },
    session: { store: storePath, mainKey: "main" },
  } as ClawCoreConfig;
  return { ...base, ...overrides };
}

export function makeJob(payload: CronJob["payload"]): CronJob {
  const now = Date.now();
  return {
    id: "job-1",
    name: "job-1",
    enabled: true,
    createdAtMs: now,
    updatedAtMs: now,
    schedule: { kind: "every", everyMs: 60_000 },
    sessionTarget: "isolated",
    wakeMode: "now",
    payload,
    state: {},
  };
}
