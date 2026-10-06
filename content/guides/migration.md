---
title: "Migrating from another TUI"
description: "What carries over from Bubble Tea, Ink or tcell — and what does not."
weight: 56
toc: true
---

# Migrating from another TUI

The short version:

> **Nothing wraps `tcell`, Bubble Tea, Textual or any other terminal library.
> Programs migrating from one of those will find no drop-in compatibility layer
> here; the shape of a TermMosaic program is its own.**

That is a deliberate position, and it is a cost of the architecture rather than an
accident of the implementation. So this page is about **what transfers and what
does not**, not about a compatibility shim that does not exist.

## The honest summary

| From | What you keep | What does not carry |
|---|---|---|
| **Bubble Tea** | the layout vocabulary — `Length`, `Min`, `Max`, `Percentage`, `Ratio`, `Fill` were chosen to match what Bubble Tea users already know | the Elm loop, the message algebra, the command model, `tea.Model` |
| **Ink** | nothing structural. The reason to leave is the thing to learn | — |
| **`tcell` / `termui`** | the terminal abstraction's shape — two narrow interfaces rather than one fat one | the API, the event model, the cell access |

## Bubble Tea

**The layout vocabulary is deliberately familiar.** [ADR 0004](/adr/0004-layout-engine/)
chose those six constraints precisely so that constraint-style layout is not a
migration cost. That is the one substantial thing that carries over, and it is
not an accident.

### The loop is different, and this is the real work

Bubble Tea's model is `Update(msg) (Model, Cmd)` with a message algebra. TermMosaic
has:

- **A retained widget tree you keep**, invalidated by rectangle.
- **`Draw(buf)` that runs every frame for every widget.**
- **`Handle(Event) bool`** — offered to the focused widget first, then to the
  tree.

**There is no reconciler, no virtual tree and no message algebra**, because
requiring widget authors to implement correct incremental invalidation is a
discipline Go cannot enforce, and a silent invalidation bug is the worst failure
mode a TUI can
have. See [Renderer and diff](/concepts/renderer/).

The consequence you will feel: **there is no "state" to diff against**, so the
mental model shifts from "reconcile my model against the last one" to "mutate
plain values and invalidate the rectangle that changed."

### What replaces `tea.Cmd`

**Asynchronous work is yours.** There is no command runner, no `tea.Batch`, no
effect system. A goroutine that finishes some work sets a field and calls
`Invalidate()`.

That is more code for the same thing, and it is honest about the cost: the
framework is a renderer and a widget catalog, not a concurrency framework.

### `tea.KeyMsg` becomes `termmosaic.Event`

One event type with a `Kind` (`EventKey`, `EventResize`, `EventPaste`, mouse,
focus) rather than a message hierarchy. And **paste is one `EventPaste` carrying
the whole payload**, never a stream — so a widget gets the whole thing and makes
it one undoable operation.

`Ctrl-C` arrives as `Ctrl+'c'` rather than as `0x03`, and `Escape` arrives as
`KeyEscape` only after the decoder has waited out its ambiguity delay. That is a
real improvement over matching raw bytes, and it is also a behavioural difference
you will notice in tests.

## Ink

Structurally there is nothing to carry over. Ink is React; TermMosaic is a
retained tree with a `Draw` method.

**The reason to leave Ink is worth stating, because it is not that Ink is badly
built:** Ink clears and repaints the whole screen on each update, which works
until the application gets large and then shows up as input lag. The diff in
[Renderer and diff](/concepts/renderer/) is the specific answer to that, and it is
measurable — 141 bytes where a full repaint writes 19,979.

If you are evaluating rather than migrating, that comparison is the argument.

## `tcell` and `termui`

**Two reasons, both independent:**

1. **`tcell`'s flush costs 280,814 ns/op** on a one-row-dirty workload where
   TermMosaic's two-tier diff costs **7,133 ns/op**.
2. **`tcell`'s headless backend cannot expose the cell buffer** that widget tests
   need — and being able to assert on cells without a terminal is what makes a
   widget testable at all. See
   [Headless testing](/concepts/headless-testing/).

TermMosaic owns the terminal layer through two narrow interfaces, `Terminal` and
`Sink`, with a direct `golang.org/x/sys` implementation. The cost of owning it is
real: **Windows console mode flags are now the project's problem**, and the
Windows backend is a stub that returns a loud error from every console
operation. See [Limitations](/limitations/#platform).

## What has no equivalent

Four things a TUI user may expect, which do not exist here:

- **No theme system.** By decision, with a stated trigger — see
  [No theme, and why](/concepts/no-theme/).
- **No `Form` container.** Composition is `layout.Solve` plus your own focus
  order — see [Forms](/guides/forms/).
- **No accessibility tree.** A terminal is a grid of cells; see
  [Accessibility](/concepts/accessibility/).
- **No animation and no reduced-motion gate**, because the catalog animates
  nothing today.

And two that are missing for reasons that are not philosophy:

- **No IME or composition**, by deliberate deferral. And it is *wrong* behaviour
  for CJK input, not degraded behaviour — see [Input](/concepts/input/).
- **No tmux DCS passthrough.** A real gap; if you develop under tmux, test in a
  plain terminal.

## A migration that works

1. **Start from `examples/hello`.** It is the whole shape: terminal, renderer,
   input source, focus, resize, pacer. Walk through
   [Your first app](/getting-started/your-first-app/) for the annotated version.
2. **Keep your layout constraints.** If you wrote `layout` constraints for Bubble
   Tea, they are the same vocabulary and the same argument order.
3. **Port the rendering before the interaction.** A screen that draws correctly
   and does not respond is easy to debug; the reverse is not.
4. **Rebuild your state as plain fields, not as a message algebra.** If you find
   yourself wanting `tea.Batch`, you want a goroutine and an `Invalidate()`.
5. **Read [Limitations](/limitations/) in full.** It is short, it is specific, and
   three of its items will change what you plan.

## And before you commit

**v1.0.0 is the first release that makes a stability promise.** The public API
freezes there and Semantic Versioning applies in earnest: from v1.0.0 a
behaviour change means a minor, not a quiet patch. Migrating a working
application onto it still means accepting that the next minor version may
change what a widget *draws* — the promise is about the API surface, and the
release notes say so explicitly: "the v1.0 promise is really a promise about
pixel output, not signatures."

The one thing deliberately held fixed since the beginning is `Widget` — four
methods, unchanged across all ten architecture decisions and now frozen under
the v1.0.0 promise. If you write a widget against it today, it is the part most
likely to still compile at v1.1.0.

## Reading next

- [Your first app](/getting-started/your-first-app/) — the whole shape in one file.
- [ADR 0001](/adr/0001-backend-strategy/) — why the terminal layer is owned, with
  the benchmark that settled it.
- [ADR 0004](/adr/0004-layout-engine/) — why the layout vocabulary is the
  familiar one.