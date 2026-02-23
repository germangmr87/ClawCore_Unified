---
summary: "CLI reference for `clawcore reset` (reset local state/config)"
read_when:
  - You want to wipe local state while keeping the CLI installed
  - You want a dry-run of what would be removed
title: "reset"
---

# `clawcore reset`

Reset local config/state (keeps the CLI installed).

```bash
clawcore reset
clawcore reset --dry-run
clawcore reset --scope config+creds+sessions --yes --non-interactive
```
