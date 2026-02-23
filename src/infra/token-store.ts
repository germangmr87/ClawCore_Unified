// Token Store – persistent JSON file with in‑memory cache
// ------------------------------------------------------------
// This module provides a simple key‑value store for authentication tokens.
// Tokens are persisted to a JSON file under the data directory so that they survive
// process restarts ("infinite memory" limited only by disk space).  At runtime the
// tokens are also kept in an in‑memory Map for fast look‑ups.
//
// The store is deliberately lightweight – no external DB dependencies – but can be
// swapped for a real database if needed.

import fs from "node:fs";
import path from "node:path";

// Directory where persistent data lives (already used by other parts of ClawCore).
const dataDir = path.resolve(process.cwd(), "data");
const tokenFile = path.join(dataDir, "tokens.json");

// In‑memory cache
let tokenCache: Map<string, string> | null = null;

/** Load the token file into memory (called lazily). */
function loadTokens(): Map<string, string> {
  if (tokenCache) return tokenCache;
  try {
    const raw = fs.readFileSync(tokenFile, { encoding: "utf-8" });
    const obj = JSON.parse(raw) as Record<string, string>;
    tokenCache = new Map(Object.entries(obj));
  } catch (e) {
    // If the file does not exist or is malformed, start with an empty map.
    tokenCache = new Map();
  }
  return tokenCache;
}

/** Persist the current cache to disk atomically. */
function persistTokens(): void {
  if (!tokenCache) return;
  const obj: Record<string, string> = {};
  for (const [k, v] of tokenCache.entries()) obj[k] = v;
  // Ensure the data directory exists.
  fs.mkdirSync(dataDir, { recursive: true });
  // Write to a temporary file then rename for atomicity.
  const tmp = tokenFile + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2), { encoding: "utf-8" });
  fs.renameSync(tmp, tokenFile);
}

/** Add or update a token. */
export function setToken(key: string, token: string): void {
  const store = loadTokens();
  store.set(key, token);
  persistTokens();
}

/** Remove a token. */
export function deleteToken(key: string): boolean {
  const store = loadTokens();
  const removed = store.delete(key);
  if (removed) persistTokens();
  return removed;
}

/** Retrieve a token value (or undefined). */
export function getToken(key: string): string | undefined {
  return loadTokens().get(key);
}

/** List all stored keys (values are omitted for security). */
export function listTokenKeys(): string[] {
  return Array.from(loadTokens().keys());
}

/** Export the whole map – useful for internal checks (read‑only). */
export function getAllTokens(): ReadonlyMap<string, string> {
  return new Map(loadTokens());
}
