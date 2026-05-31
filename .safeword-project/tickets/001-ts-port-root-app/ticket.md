---
id: 001
type: task
phase: implement
status: in_progress
created: 2026-05-30T22:52:00Z
last_modified: 2026-05-30T22:52:00Z
scope:
  - Port the root Holoform app from Python to TypeScript on Bun
  - Modules covered: settings, labels, message, thread, message_processor, lm_services, utils, main
  - Keep behavior faithful to the existing Python source (the spec)
  - Arcade service layer ported as a typed stub interface (no live SDK wiring)
out_of_scope:
  - email-priority-agent/ sub-project (stays Python)
  - Wiring the real @arcadeai/arcadejs SDK or live Gmail calls
  - Deleting the Python files (kept alongside for now)
  - Changing/observing classification behavior beyond a faithful translation
done_when:
  - src/ contains TS equivalents of all root-app modules
  - tsc --noEmit passes with no type errors
  - Pure logic (labels, markdown_to_json, message/thread modeling) covered by passing tests
  - bun run src/main.ts runs end-to-end against the Arcade stub without crashing
---

# Port root Holoform app to TypeScript

**Goal:** Re-implement the root email-classification app in TypeScript on Bun, faithful to the Python behavior.

**Why:** Holoform is becoming a TypeScript project; the root app is the README's core demo and the natural first slice.

## Work Log

- 2026-05-31T00:30:00Z Complete: All 8 modules ported to src/ on Bun. tsc --noEmit clean, eslint (safeword strict) clean, 22 tests pass, `bun run src/main.ts` runs end-to-end against the Arcade stub (exit 0). Extracted pure `computeLabelChanges` and `Thread.buildTree` for testability. (refs: src/, commit pending)
- 2026-05-30T22:52:00Z Started: Read all 10 root-app Python modules; reclassified feature→task (faithful translation of pre-defined behavior); Arcade set aside as a typed stub per user direction.

---

### Scope

**In scope:**

- settings, labels, message, thread, message_processor, lm_services, utils, main → TS under `src/`

**Out of scope:**

- `email-priority-agent/`, real Arcade SDK wiring, deleting Python files
