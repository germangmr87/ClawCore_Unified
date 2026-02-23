---
summary: "CLI reference for `clawcore browser` (profiles, tabs, actions, extension relay)"
read_when:
  - You use `clawcore browser` and want examples for common tasks
  - You want to control a browser running on another machine via a node host
  - You want to use the Chrome extension relay (attach/detach via toolbar button)
title: "browser"
---

# `clawcore browser`

Manage ClawCore’s browser control server and run browser actions (tabs, snapshots, screenshots, navigation, clicks, typing).

Related:

- Browser tool + API: [Browser tool](/tools/browser)
- Chrome extension relay: [Chrome extension](/tools/chrome-extension)

## Common flags

- `--url <gatewayWsUrl>`: Gateway WebSocket URL (defaults to config).
- `--token <token>`: Gateway token (if required).
- `--timeout <ms>`: request timeout (ms).
- `--browser-profile <name>`: choose a browser profile (default from config).
- `--json`: machine-readable output (where supported).

## Quick start (local)

```bash
clawcore browser --browser-profile chrome tabs
clawcore browser --browser-profile clawcore start
clawcore browser --browser-profile clawcore open https://example.com
clawcore browser --browser-profile clawcore snapshot
```

## Profiles

Profiles are named browser routing configs. In practice:

- `clawcore`: launches/attaches to a dedicated ClawCore-managed Chrome instance (isolated user data dir).
- `chrome`: controls your existing Chrome tab(s) via the Chrome extension relay.

```bash
clawcore browser profiles
clawcore browser create-profile --name work --color "#FF5A36"
clawcore browser delete-profile --name work
```

Use a specific profile:

```bash
clawcore browser --browser-profile work tabs
```

## Tabs

```bash
clawcore browser tabs
clawcore browser open https://docs.clawcore.ai
clawcore browser focus <targetId>
clawcore browser close <targetId>
```

## Snapshot / screenshot / actions

Snapshot:

```bash
clawcore browser snapshot
```

Screenshot:

```bash
clawcore browser screenshot
```

Navigate/click/type (ref-based UI automation):

```bash
clawcore browser navigate https://example.com
clawcore browser click <ref>
clawcore browser type <ref> "hello"
```

## Chrome extension relay (attach via toolbar button)

This mode lets the agent control an existing Chrome tab that you attach manually (it does not auto-attach).

Install the unpacked extension to a stable path:

```bash
clawcore browser extension install
clawcore browser extension path
```

Then Chrome → `chrome://extensions` → enable “Developer mode” → “Load unpacked” → select the printed folder.

Full guide: [Chrome extension](/tools/chrome-extension)

## Remote browser control (node host proxy)

If the Gateway runs on a different machine than the browser, run a **node host** on the machine that has Chrome/Brave/Edge/Chromium. The Gateway will proxy browser actions to that node (no separate browser control server required).

Use `gateway.nodes.browser.mode` to control auto-routing and `gateway.nodes.browser.node` to pin a specific node if multiple are connected.

Security + remote setup: [Browser tool](/tools/browser), [Remote access](/gateway/remote), [Tailscale](/gateway/tailscale), [Security](/gateway/security)
