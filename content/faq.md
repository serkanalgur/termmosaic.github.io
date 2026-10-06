---
title: "FAQ"
description: "The questions a reader arrives with, answered without hedging into uselessness."
weight: 90
toc: true
---

# FAQ

## Should I use this?

**Not in production yet — but v1.0.0 is the first release that says why that
can change.** v1.0.0 (2026-10-06) makes a stability promise: the public API
freezes there and Semantic Versioning applies in earnest — a behaviour change
means a minor, not a quiet patch — with one documented exception:
`widgets/widgettest`, the test harness, is excluded from that promise, because
it must evolve with the framework. Every release before v1.0.0 was a
pre-release under a break-without-notice policy. One honesty note the release
carries itself: the gate's SemVer criterion is recorded **PARTIALLY MET**,
because v0.5.1, v0.5.2 and v0.6.1 were patch numbers that carried behaviour
changes. The promise starts at v1.0.0; it is not retroactive.

What you get for the risk: a renderer whose diff writes 141 bytes where a full
repaint writes 19,979, at 7,133 ns/op and 0 allocs/op; a 24-widget catalog whose
data widgets render 100,000 items in 14,242 ns; a colour quantiser whose
selection error is 0.000 on both the 256 and 16 rungs; and a headless backend
that lets you test a widget without a terminal.

Evaluate it on a side project. If you are evaluating rather than adopting, read
[Limitations](/limitations/) first — it is short, and three of its items will
change what you plan.

## Is this production-ready?

Not yet. See above. The honest statement of what *is* finished: the renderer,
the input layer, the layout solver and the full 24-widget catalog are built and
tested — 28 packages, 1,186 top-level test functions, a zero-allocation frame
path — and v1.0.0 is the first release that freezes the API. What keeps it from
"production-ready" is not instability any more; it is the open items on
[Limitations](/limitations/#still-open) — no IME, no tmux passthrough, and no
Windows runtime.

## Does it work on Windows?

**It compiles and it does not run.** The Windows backend is a **stub that returns
a loud error from every console operation**. Cross-compilation to
`windows/amd64` and `windows/arm64` is still verified in CI (the six
cross-compile legs are unchanged), so the packaging works; the runtime does
not. **Linux and macOS are the supported platforms** — narrowed to that by the
v1.0.0 platform decision ([ADR 0001](/adr/0001-backend-strategy/)). The Windows
CI **test** leg was dropped at v1.0.0 because running the full suite there
asserted only that the stub returns its documented error.

## How many widgets are there?

**24**, and the number is counted rather than estimated: every exported type with
a `New…` constructor that satisfies `termmosaic.Widget`. The two added in v0.2.0
are [`Menu`](/widgets/menu/) and [`Dialog`](/widgets/dialog/), which bring the
navigation-and-modality group into existence.

Two things that are deliberately **not** widgets:

- **`buffer.Buffer`** — it has `Invalidate()` but no `Bounds`, `Draw` or
  `Handle`. It is what widgets draw *into*.
- **`widgets/form/optionlist.go`** — an unexported helper behind `Select`, `Tabs`
  and `KeyHint`.

And one thing that does not exist: **there is no `Form` container widget, on
purpose.** [ADR 0004](/adr/0004-layout-engine/)'s solver plus `layout` covers
composition, and a `Form` would have been a second way to do it. See
[Forms](/guides/forms/).

## Is there a theme?

**No, by decision**, and the decision has a stated trigger: *a theme is triggered
by the first style **role** that two widgets must share.* Widgets carry `Style`
fields; the framework's defaults are the terminal's own colours plus named
attribute styles.

[No theme, and why](/concepts/no-theme/) explains why that is the right call here
and what it would take to reverse it.

## Why no live playground on this site?

**A browser TTY is a declared non-goal of the framework.** The project's own
architecture document lists "not a web framework — no HTTP server, no browser
target, no WASM build" among its non-goals, and the terminal layer is a direct
`golang.org/x/sys` binding with a Windows stub. There is no abstraction a WASM
shim could slot into.

So every picture here is a **cell grid** — the grid the renderer produced — and
not a screenshot of anyone's terminal. That has one large limit: **a capture
cannot show interaction.** It cannot show a keypress, a selection moving, a pager
scrolling or a tree expanding. It also cannot show terminal fidelity, and Braille
and Block Elements may misalign in a web font — which is why the exact plain-text
capture sits beside every colour capture. See
[Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots).

## So how do I see a widget work?

**Run it.** Four programs exist today, and the three that matter are driven
by keyboard *and* mouse:

```
go run github.com/serkanalgur/termmosaic/examples/markets@v1.0.0   # live finance dashboard
go run github.com/serkanalgur/termmosaic/examples/hello@v1.0.0     # focus ring + ? help overlay
go run github.com/serkanalgur/termmosaic/examples/search@v1.0.0    # search + results, real Wikipedia data
```

`markets` runs on live data with no API key (ECB FX from Frankfurter, crypto
from CoinGecko) and takes `--offline` to run on bundled sample data instead.
`search` queries Wikipedia's own API — no key, no signup — and takes `--offline`
to run on a transcribed capture; it is **the first example with a focusable
widget in the focus ring**. Press `?` in any of them for its key list.

> **A fourth program, `examples/dashboard`, still exists and overlaps `markets`.**
> Whether to keep it or retire it is **undecided**, so this site points new
> readers at `markets` and does not recommend both. It has not been removed.

**As of v1.0.0 every one of the 24 widgets has a runnable example** — 74
`func Example` functions in the eight `widgets/*/example_test.go` files, each
rendered through `widgets/widgettest` so its `// Output` comment is the cell
grid the renderer produced. `CONTRIBUTING.md`'s "a widget without an example is
not done" requirement is now met; what does *not* exist is a runnable *program*
per widget, and there the count is still four.

## Do I get IME support?

**No, by deliberate deferral** — [ADR 0005 §7](/adr/0005-input-decoding/). And
the honest version of the cost is worse than "no support":

> Composing Japanese, Chinese or Korean in a `TextInput` produces **wrong**
> behaviour, not degraded behaviour. The committed text arrives as a burst of
> ordinary key events, so it inserts correctly but the undo stack gains one entry
> per character.

Three seams are reserved so this is a deferred feature rather than a deferred
rewrite: `EventCompose` is declared, `Event` carries a `Compose` payload, and the
parser's entry point is the byte stream. The trigger to revisit is stated in the
ADR.

## Why does tmux break it?

**DCS passthrough is not implemented.** Under tmux on a modern terminal, a
TermMosaic program can lose key and mouse reporting, because the sequences it
emits are not wrapped for the multiplexer. Deferred with a trigger: any tmux user
reporting broken keys or mouse, or v1.0, whichever comes first.

If you develop under tmux, **test in a plain terminal before concluding the library
is broken.** It might be.

## Why do I have to call `Invalidate()` when I change a field?

**Because `Invalidate()` now means two things:** mark `Bounds()` dirty, *and* drop
every value the widget has cached.

The second half is not a formality. A widget that caches column widths against
`Bounds()` and is then handed `Header = true` renders the old layout
**permanently** — no rect will ever change again, so nothing will produce the
different layout to repair it.

**So: any setter that writes a field `Draw` reads must invalidate.** That is the
sharpest edge in the framework, and it applies to your widgets as much as the
catalog's. See [Responsiveness](/concepts/responsiveness/).

## Why did my app freeze on v0.1.0?

**`Renderer.Post` never woke the frame pacer.** `Post` queued a callback and
returned; `NeedsFrame()` did not consider queued callbacks, while `Pacer.Run`
gates every frame on `NeedsFrame()`, and posted callbacks only run *inside*
`Render`. The chain deadlocked: `Post` queued work, `Render` would run it,
`Render` was gated on `NeedsFrame`, which cannot become true until the callback
runs.

An app that updates the screen from `Post` — which
[ADR 0003](/adr/0003-renderer-mode/) documents as the safe way to mutate widget
state, precisely so it is safe against a concurrent `Draw` — **painted one frame
and idled forever.** It was not a hang, a deadlock or a crash: it was a correctly
functioning render loop with nothing left to do.

**Fixed in v0.2.0**, with a regression test. Note the trap: `--offline` masked it
completely, because an instant fetch returns before the first frame runs, so the
callback was already queued and got drained inside that frame — and a test that
called `Render` directly could never catch it either.

## Do I get a redo stack?

**No.** Undo, yes; redo, no, in either text field. Adding one is a widget API
addition.

## Is `TextArea`'s selection visible?

**No.** In v0.3.0 `TextArea` tracks and moves a caret and supports editing, but
**the selected range is not drawn**. `TextInput` does render its selection. This
is a recorded gap, and it is one reason `TextArea` is the wrong widget for a
value the user needs to see part of.

## Can I test a widget without a terminal?

**Yes, and that is the reason the headless backend exists.** A `MemorySink`
maintains the cell grid the emitted bytes *would have produced*, so a test drives
the real encoder, the real diff and the real renderer and then asserts on cells.

The important part: the screen model **fails the test if the encoder emits a
sequence it does not implement**, because a screen reconstructed from an
incomplete model makes every assertion against it unsound. See
[Headless testing](/concepts/headless-testing/).

## Why does my widget flicker?

Three likely causes, in order:

1. **A wide glyph's continuation cell does not match its owning span's style.** It
   will then never compare equal across frames, and that row flickers forever.
   This is the rule most worth checking first.
2. **You are drawing the same region with different styles from two widgets**, or
   not repainting your whole rect before drawing into it — the renderer diffs and
   never clears, so a stale cell is a cell you left behind.
3. **You are rebuilding something in `Draw` that should be cached**, which
   allocates and may also reorder runs.

## Is it fast?

Measured, on darwin/arm64 — see
[Performance](/guides/performance/) for every number **and for the list of what is
not measured**:

| | |
|---|---|
| Diff vs full repaint, 200×60, 99% static | **141 vs 19,979 bytes** (~141×) at **~7,133 ns/op**, **0 allocs/op** |
| `List`, 10,000 → 100,000 items | **13,320 → 14,242 ns** |
| `Table`, 10,000 → 100,000 items | **16,801 → 17,885 ns** |
| Wide-glyph scene, 6,000 glyphs, v0.2.0 | **60 cursor moves, 19,443 bytes, 3.12×** — was 6,000 moves and 68,832 bytes (11×) before the fix |

## Can I use `tcell` under it, or Bubble Tea?

**No compatibility layer exists, by decision.** TermMosaic wraps no terminal
library — `tcell`'s flush costs 280,814 ns/op where the two-tier diff costs
7,133, and its headless backend cannot expose the cell buffer that widget tests
need.

From Bubble Tea, what carries over is the **layout vocabulary** — `Length`, `Min`,
`Max`, `Percentage`, `Ratio`, `Fill` were chosen to match it deliberately. What
does not is the Elm loop and the message algebra. See
[Migrating from another TUI](/guides/migration/).

## Is the widget count right? It was wrong once.

**It was, and that is worth stating rather than quietly fixing.** At v0.1.0 the
count was reported as 24 when it was 22, because `buffer.Buffer` had been listed
as a widget — and it is not one: it has no `Bounds`, `Draw` or `Handle`. The
correction to 22 was made in the framework's repository at v0.1.0.

**The count is now 24 again, and this time it is 24.** [`Menu`](/widgets/menu/)
and [`Dialog`](/widgets/dialog/) shipped in v0.2.0, and `buffer.Buffer` is still
not counted. The site states 24 because the site's entire value proposition is the
catalog, and a reader who counts 24 on the page and finds 24 in the repository is
the only reason to trust either.

## Is there a command palette?

**No — but the layer a palette needs shipped in v0.6.0, so the gap is now the
UI rather than the data.**
[ADR 0009](/adr/0009-command-and-keymap/) specifies a command and keymap layer —
a named action reachable by more than one key — and **the `keymap` package is
built**: `Dispatch` resolves by context specificity (focus, then screen, then
global, with no numeric priority) at 0 allocs/op, and `Describe` /
`DescribeGrouped` give you the rows a palette renders. `Widget`, `Event`, `Key`
and `Mouse` are unchanged, so adopting it is opt-in and breaks nothing.

**There is no `Ctrl+K` palette widget**, because ADR 0009 §9 puts it in scope and
explicitly not in that ADR. `examples/hello` and `examples/search` render hint
lines from the registry today, which is most of what a palette does at smaller
size. `examples/markets` and `examples/dashboard` still dispatch by their own
`switch`. See
[Limitations](/limitations/#there-is-still-no-command-palette).

## Does the mouse work?

**Yes, opt-in, and off by default.** Mouse capture is deliberately disabled by
default because enabling it takes text selection and scrollback copying away from
the user's shell. [ADR 0005](/adr/0005-input-decoding/)'s default stands.

**Who gets the event is a widget's own business.**
[ADR 0010](/adr/0010-mouse-routing/) settles it: a widget handles a pointer event
only when the pointer is inside its `Bounds()`, with two stated exemptions — a
release ends a drag wherever the pointer is, and a drag continues outside `Bounds`
once a press has claimed it. That is why a tab row no longer takes the wheel from
the panel under it, and it is also why **your application still writes the wheel
loop**: no widget can implement "the wheel never takes focus" on its own.

`examples/markets` is the one program that opts in, and it restores the previous
mode on exit. It supports wheel and click, with per-panel key routing. `hello` is
keyboard-driven. See [Limitations](/limitations/#input).

## Where do I go if this site is wrong?

**Report it.** An inaccuracy on this site is a bug in the site, not a matter of
opinion — <https://github.com/serkanalgur/termmosaic/issues>.

And **pkg.go.dev is never out of date**, because it is generated from the source.
If the two disagree, pkg.go.dev is right.

## Is this site generated?

**Partly.** The widget pages are generated by `scripts/gen_widgets.py`, which
merges three inputs: the framework's `manifest.json`, godoc extracted from its Go
source, and hand-written prose in `data/widget_prose.json`. The captures are
framework artefacts, copied unmodified. The ADRs are byte-identical to the
framework's.

**Two sections of every widget page cannot be generated** — the example and "when
not to use it" — and the second is written by hand per widget. A reviewer reading
a widget page knows exactly which parts to check. See
[the site README](https://github.com/serkanalgur/termmosaic.github.io).