# Session interface sketch

A language-neutral shape for the durable session plane. The point is the
boundary, not the syntax: the session is an append-only event log behind a small
interface, and the brain holds none of this state in memory between wakes.

## Event

Every state change is one immutable event. Keep events small and typed; large
payloads (a file an agent wrote, a long tool result) go to blob storage with a
reference here, not inline.

```
Event {
  sessionId:  string
  seq:        integer        // monotonic per session, gives a total order
  ts:         timestamp
  type:       "user_message" | "model_message" | "tool_call" | "tool_result"
            | "checkpoint" | "error"
  payload:    object         // typed by `type`; blob refs for anything large
}
```

## Operations

```
append(sessionId, event)            -> seq
    // the only write. Appends one event and returns its sequence number.

getSession(sessionId)               -> SessionState
    // read-only snapshot: status, last seq, open tool calls, cursors.
    // Does not resume execution.

getEvents(sessionId, fromSeq, toSeq) -> Event[]
    // selective range read. The brain calls this to pull just the slice of
    // history it needs, instead of replaying the whole log into context.

wake(sessionId)                     -> void
    // rehydrate a brain from the log and continue from the last event.
    // Safe to call after any crash; idempotent on an already-running session.
```

## Why these shapes

- **`seq` is monotonic per session.** It gives every event a total order, so a
  rebooted brain knows exactly where it stopped and a reader can page the log.
- **`getEvents` takes a range.** A long session's log will not fit in the
  context window. Range reads let the brain fetch the recent slice, or jump to a
  specific decision, without paying for the whole history.
- **`wake` is idempotent.** Crash recovery calls it blindly. Calling it on a
  live session must not start a second brain on the same log.
- **Blob refs, not inline payloads.** Keeping large artifacts out of the event
  rows keeps the log cheap to scan and cheap to replay.

## Checkpoints

Write a `checkpoint` event at natural boundaries (a completed subtask, a passing
test). On `wake`, a brain can start from the latest checkpoint and replay only
the events after it, rather than reasoning over the entire history again.
