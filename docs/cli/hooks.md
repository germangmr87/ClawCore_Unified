---
summary: "CLI reference for `clawcore hooks` (agent hooks)"
read_when:
  - You want to manage agent hooks
  - You want to install or update hooks
title: "hooks"
---

# `clawcore hooks`

Manage agent hooks (event-driven automations for commands like `/new`, `/reset`, and gateway startup).

Related:

- Hooks: [Hooks](/automation/hooks)
- Plugin hooks: [Plugins](/tools/plugin#plugin-hooks)

## List All Hooks

```bash
clawcore hooks list
```

List all discovered hooks from workspace, managed, and bundled directories.

**Options:**

- `--eligible`: Show only eligible hooks (requirements met)
- `--json`: Output as JSON
- `-v, --verbose`: Show detailed information including missing requirements

**Example output:**

```
Hooks (4/4 ready)

Ready:
  🚀 boot-md ✓ - Run BOOT.md on gateway startup
  📎 bootstrap-extra-files ✓ - Inject extra workspace bootstrap files during agent bootstrap
  📝 command-logger ✓ - Log all command events to a centralized audit file
  💾 session-memory ✓ - Save session context to memory when /new command is issued
```

**Example (verbose):**

```bash
clawcore hooks list --verbose
```

Shows missing requirements for ineligible hooks.

**Example (JSON):**

```bash
clawcore hooks list --json
```

Returns structured JSON for programmatic use.

## Get Hook Information

```bash
clawcore hooks info <name>
```

Show detailed information about a specific hook.

**Arguments:**

- `<name>`: Hook name (e.g., `session-memory`)

**Options:**

- `--json`: Output as JSON

**Example:**

```bash
clawcore hooks info session-memory
```

**Output:**

```
💾 session-memory ✓ Ready

Save session context to memory when /new command is issued

Details:
  Source: clawcore-bundled
  Path: /path/to/clawcore/hooks/bundled/session-memory/HOOK.md
  Handler: /path/to/clawcore/hooks/bundled/session-memory/handler.ts
  Homepage: https://docs.clawcore.ai/automation/hooks#session-memory
  Events: command:new

Requirements:
  Config: ✓ workspace.dir
```

## Check Hooks Eligibility

```bash
clawcore hooks check
```

Show summary of hook eligibility status (how many are ready vs. not ready).

**Options:**

- `--json`: Output as JSON

**Example output:**

```
Hooks Status

Total hooks: 4
Ready: 4
Not ready: 0
```

## Enable a Hook

```bash
clawcore hooks enable <name>
```

Enable a specific hook by adding it to your config (`~/.clawcore/config.json`).

**Note:** Hooks managed by plugins show `plugin:<id>` in `clawcore hooks list` and
can’t be enabled/disabled here. Enable/disable the plugin instead.

**Arguments:**

- `<name>`: Hook name (e.g., `session-memory`)

**Example:**

```bash
clawcore hooks enable session-memory
```

**Output:**

```
✓ Enabled hook: 💾 session-memory
```

**What it does:**

- Checks if hook exists and is eligible
- Updates `hooks.internal.entries.<name>.enabled = true` in your config
- Saves config to disk

**After enabling:**

- Restart the gateway so hooks reload (menu bar app restart on macOS, or restart your gateway process in dev).

## Disable a Hook

```bash
clawcore hooks disable <name>
```

Disable a specific hook by updating your config.

**Arguments:**

- `<name>`: Hook name (e.g., `command-logger`)

**Example:**

```bash
clawcore hooks disable command-logger
```

**Output:**

```
⏸ Disabled hook: 📝 command-logger
```

**After disabling:**

- Restart the gateway so hooks reload

## Install Hooks

```bash
clawcore hooks install <path-or-spec>
```

Install a hook pack from a local folder/archive or npm.

Npm specs are **registry-only** (package name + optional version/tag). Git/URL/file
specs are rejected. Dependency installs run with `--ignore-scripts` for safety.

**What it does:**

- Copies the hook pack into `~/.clawcore/hooks/<id>`
- Enables the installed hooks in `hooks.internal.entries.*`
- Records the install under `hooks.internal.installs`

**Options:**

- `-l, --link`: Link a local directory instead of copying (adds it to `hooks.internal.load.extraDirs`)

**Supported archives:** `.zip`, `.tgz`, `.tar.gz`, `.tar`

**Examples:**

```bash
# Local directory
clawcore hooks install ./my-hook-pack

# Local archive
clawcore hooks install ./my-hook-pack.zip

# NPM package
clawcore hooks install @clawcore/my-hook-pack

# Link a local directory without copying
clawcore hooks install -l ./my-hook-pack
```

## Update Hooks

```bash
clawcore hooks update <id>
clawcore hooks update --all
```

Update installed hook packs (npm installs only).

**Options:**

- `--all`: Update all tracked hook packs
- `--dry-run`: Show what would change without writing

## Bundled Hooks

### session-memory

Saves session context to memory when you issue `/new`.

**Enable:**

```bash
clawcore hooks enable session-memory
```

**Output:** `~/.clawcore/workspace/memory/YYYY-MM-DD-slug.md`

**See:** [session-memory documentation](/automation/hooks#session-memory)

### bootstrap-extra-files

Injects additional bootstrap files (for example monorepo-local `AGENTS.md` / `TOOLS.md`) during `agent:bootstrap`.

**Enable:**

```bash
clawcore hooks enable bootstrap-extra-files
```

**See:** [bootstrap-extra-files documentation](/automation/hooks#bootstrap-extra-files)

### command-logger

Logs all command events to a centralized audit file.

**Enable:**

```bash
clawcore hooks enable command-logger
```

**Output:** `~/.clawcore/logs/commands.log`

**View logs:**

```bash
# Recent commands
tail -n 20 ~/.clawcore/logs/commands.log

# Pretty-print
cat ~/.clawcore/logs/commands.log | jq .

# Filter by action
grep '"action":"new"' ~/.clawcore/logs/commands.log | jq .
```

**See:** [command-logger documentation](/automation/hooks#command-logger)

### boot-md

Runs `BOOT.md` when the gateway starts (after channels start).

**Events**: `gateway:startup`

**Enable**:

```bash
clawcore hooks enable boot-md
```

**See:** [boot-md documentation](/automation/hooks#boot-md)
