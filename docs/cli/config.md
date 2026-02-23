---
summary: "CLI reference for `clawcore config` (get/set/unset config values)"
read_when:
  - You want to read or edit config non-interactively
title: "config"
---

# `clawcore config`

Config helpers: get/set/unset values by path. Run without a subcommand to open
the configure wizard (same as `clawcore configure`).

## Examples

```bash
clawcore config get browser.executablePath
clawcore config set browser.executablePath "/usr/bin/google-chrome"
clawcore config set agents.defaults.heartbeat.every "2h"
clawcore config set agents.list[0].tools.exec.node "node-id-or-name"
clawcore config unset tools.web.search.apiKey
```

## Paths

Paths use dot or bracket notation:

```bash
clawcore config get agents.defaults.workspace
clawcore config get agents.list[0].id
```

Use the agent list index to target a specific agent:

```bash
clawcore config get agents.list
clawcore config set agents.list[1].tools.exec.node "node-id-or-name"
```

## Values

Values are parsed as JSON5 when possible; otherwise they are treated as strings.
Use `--json` to require JSON5 parsing.

```bash
clawcore config set agents.defaults.heartbeat.every "0m"
clawcore config set gateway.port 19001 --json
clawcore config set channels.whatsapp.groups '["*"]' --json
```

Restart the gateway after edits.
