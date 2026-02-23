---
summary: "CLI reference for `clawcore logs` (tail gateway logs via RPC)"
read_when:
  - You need to tail Gateway logs remotely (without SSH)
  - You want JSON log lines for tooling
title: "logs"
---

# `clawcore logs`

Tail Gateway file logs over RPC (works in remote mode).

Related:

- Logging overview: [Logging](/logging)

## Examples

```bash
clawcore logs
clawcore logs --follow
clawcore logs --json
clawcore logs --limit 500
clawcore logs --local-time
clawcore logs --follow --local-time
```

Use `--local-time` to render timestamps in your local timezone.
