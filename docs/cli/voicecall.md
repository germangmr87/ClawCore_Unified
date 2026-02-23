---
summary: "CLI reference for `clawcore voicecall` (voice-call plugin command surface)"
read_when:
  - You use the voice-call plugin and want the CLI entry points
  - You want quick examples for `voicecall call|continue|status|tail|expose`
title: "voicecall"
---

# `clawcore voicecall`

`voicecall` is a plugin-provided command. It only appears if the voice-call plugin is installed and enabled.

Primary doc:

- Voice-call plugin: [Voice Call](/plugins/voice-call)

## Common commands

```bash
clawcore voicecall status --call-id <id>
clawcore voicecall call --to "+15555550123" --message "Hello" --mode notify
clawcore voicecall continue --call-id <id> --message "Any questions?"
clawcore voicecall end --call-id <id>
```

## Exposing webhooks (Tailscale)

```bash
clawcore voicecall expose --mode serve
clawcore voicecall expose --mode funnel
clawcore voicecall unexpose
```

Security note: only expose the webhook endpoint to networks you trust. Prefer Tailscale Serve over Funnel when possible.
