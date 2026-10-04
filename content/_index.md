---
title: "TermMosaic"
description: "A terminal UI framework for Go: a cell-buffer renderer with two-tier diffing and 22 ready-to-use widgets. Pre-alpha."
toc: true
---

# A terminal UI framework for Go

**TermMosaic is a cell-buffer renderer plus a catalog of 22 widgets.** The
renderer double-buffers cells, diffs at two tiers, and tracks dirty rectangles;
the catalog is the part that is the point — including the five measurement
widgets that comparable Go TUIs do not ship.

> **TermMosaic is pre-alpha. The public API is not stable and will break
> without notice until v1.0.0.** Everything on this site is accurate as of
> **v0.1.0**. Read [Limitations](/limitations/) before you rely on any of it —
> the honest list is short, specific, and load-bearing.

```go
go get github.com/serkanalgur/termmosaic@v0.1.0
```

Then read the [quickstart](/getting-started/quickstart/), or run the example:

```
go run github.com/serkanalgur/termmosaic/examples/dashboard@v0.1.0
```

## What is measured, and what is not

These are the only performance figures on this site. They come from the
framework's own benchmarks and its `docs/STATUS.md`, and nothing here is an
estimate.

| Property | Measured | Source |
|---|---|---|
| Two-tier diff vs a full repaint, 200×60 scene that is 99% static chrome | **141 bytes** written where a full repaint writes **19,979** — about **141× fewer**, at **~7,133 ns/op**, **0 allocs/op** | [ADR 0001](/adr/0001-backend-strategy/), [ADR 0002](/adr/0002-buffer-representation/) |
| Allocations on the frame path | **0 per frame**, asserted by a test rather than benchmarked | [ADR 0008](/adr/0008-style-and-text/) |
| `List` render cost, 10,000 items → 100,000 items | **13,320 ns → 14,242 ns** — 7% for ten times the data, both at zero allocations | `widgets/data` benchmarks |
| `Table` render cost, 10,000 items → 100,000 items | **16,801 ns → 17,885 ns**, same shape | `widgets/data` benchmarks |
| The key-decoding path | **0 allocations**, pinned by test | [ADR 0005](/adr/0005-input-decoding/) |
| `tcell`'s flush, same one-row-dirty workload | **280,814 ns/op** against our **7,133 ns/op** — the measurement that settled [ADR 0001](/adr/0001-backend-strategy/) | [ADR 0001](/adr/0001-backend-strategy/) |

**There are no benchmarks on this site for the widgets' visual output, for
frame pacing under load, or for drag-resize.** The resize costs in
[ADR 0007](/adr/0007-responsive-screens/) are *derived* from existing code and
from ADR 0002/0003's numbers; no resize has ever been observed against a real
terminal being dragged. `docs/STATUS.md` says so itself and this site does not
paper over it.

{{< widget-capture "barchart" >}}

That is a `BarChart` at three widths, rendered by the framework's own capture
tool from the cells the renderer produced.

## About the pictures on this site — read this once

Every capture on this site is a **cell grid**, not a screenshot of anyone's
terminal. It is produced by `cmd/capture` in the framework repo, which runs each
widget through `widgettest.Capture` — the same path the 650+ tests assert on —
and converts `MemorySink.Cells()` to HTML. That is what makes it trustworthy: the
docs cannot show something no test pins.

It is also what it is, and the limits are not closable:

- **No interaction.** A capture is one settled frame after N frames of settling.
  It cannot show a keypress, a selection moving, a cell flickering, a pager
  scrolling or a tree expanding. Every widget page says so.
- **No animation, no timing, no frame pacing.** `render.Pacer` and the 30–60 fps
  budget are invisible in a picture.
- **No live resize.** Instead, every widget page shows three **fixed** widths —
  40, 80 and 120 columns — side by side. That is more informative than a resize
  demo, because each frame is exact and the widths are named.
- **No terminal fidelity.** You are not seeing your font, your colour scheme,
  your background, your terminal's cell aspect ratio, or its wide-glyph and
  ligature behaviour.
- **Braille and Block Elements may misalign in a web font.** `Gauge` and
  `Sparkline` are Braille (U+2800–28FF); `ProgressBar`, `Meter`, `Gauge` and
  `BarChart` use Block Elements (U+2580–259F). If those glyphs take a different
  advance width in your browser than in a terminal, the alignment those five
  widgets depend on is destroyed. **That is exactly why the plain-text capture
  sits beside every colour capture on every widget page.** The plain-text form is
  exact; the colour form is the persuasive one.

Full statement: [Captures are cell grids, not terminal
screenshots](/limitations/#captures-are-cell-grids-not-terminal-screenshots).

## The 22 widgets

| Group | Widgets |
|---|---|
| **Core** | [`Block`](/widgets/block/) [`Text`](/widgets/text/) [`Paragraph`](/widgets/paragraph/) [`Split`](/widgets/split/) |
| **Forms** | [`TextInput`](/widgets/textinput/) [`TextArea`](/widgets/textarea/) [`Select`](/widgets/select/) [`Checkbox`](/widgets/checkbox/) [`Radio`](/widgets/radio/) [`Toggle`](/widgets/toggle/) [`Tabs`](/widgets/tabs/) [`Button`](/widgets/button/) [`KeyHint`](/widgets/keyhint/) |
| **Data** | [`List`](/widgets/list/) [`Table`](/widgets/table/) [`Tree`](/widgets/tree/) [`Pager`](/widgets/pager/) |
| **Visualization** | [`ProgressBar`](/widgets/progressbar/) [`Gauge`](/widgets/gauge/) [`Meter`](/widgets/meter/) [`Sparkline`](/widgets/sparkline/) [`BarChart`](/widgets/barchart/) |

That is **22**, counted: every exported type with a `New…` constructor that
satisfies `termmosaic.Widget`. `buffer.Buffer` is deliberately not on the list —
it has `Invalidate()` but no `Bounds`, `Draw` or `Handle`, so it is not a widget,
it is what widgets draw *into*. `widgets/form/optionlist.go` is an unexported
helper behind `Select`, `Tabs` and `KeyHint`, not a twenty-third widget.

**There is no `Form` container widget, on purpose.** A `Form` type would be a
second way to do what [ADR 0004](/adr/0004-layout-engine/)'s constraint solver and
the `layout` package already do. See [Forms](/guides/forms/).

## Start here

- **[Install](/getting-started/install/)** — Go 1.23+, `CGO_ENABLED=0`, what is
  and is not released.
- **[Quickstart](/getting-started/quickstart/)** — a working program in one file.
- **[Your first app](/getting-started/your-first-app/)** — terminal, renderer,
  input and loop, end to end.
- **[Concepts](/concepts/)** — the twelve ideas the framework is built from.
  Start with [Renderer and diff](/concepts/renderer/) and [Widgets and
  focus](/concepts/widgets-and-focus/).
- **[Widgets](/widgets/)** — the catalog, one page per widget, with captures.
- **[Architecture decisions](/adr/)** — the eight ADRs, verbatim, with the
  rejected alternatives and the risks.

## Why it exists

The Go TUI ecosystem has one dominant framework and it leaves room:

- **OpenTUI** is a strong engineering artifact with a deliberately unfinished
  surface. At 13.4k stars and running in production, it ships **no
  progressbar, gauge, meter, sparkline or bar chart**, and **no list, tree,
  pager or virtual scroll**.
- **Ink** clears and repaints the whole screen on each update, which shows up as
  input lag once the application gets large.

The bet is narrow: **the widget catalog is the product.** A framework nobody can
build a real dashboard on is a toy, however elegant its renderer.

## Honest status, in one paragraph

The renderer, the input layer, the layout solver and the full 22-widget catalog
are built and tested: 19 packages, 650+ tests, a zero-allocation frame path.
Alongside that: **Windows is a stub that returns a loud error from every console
operation**, there is **no IME or preedit**, **tmux DCS passthrough is missing**,
**`TextArea` has no rendered selection**, the **colour quantiser is unvalidated**,
and **there is no theme** — by decision, argued in
[ADR 0008](/adr/0008-style-and-text/), not by omission. Everything in that list
is on [Limitations](/limitations/) with the reason.

## Elsewhere

- Source: [github.com/serkanalgur/termmosaic](https://github.com/serkanalgur/termmosaic)
- API reference: [pkg.go.dev/github.com/serkanalgur/termmosaic](https://pkg.go.dev/github.com/serkanalgur/termmosaic) —
  which is never out of date, because it is generated from the source
- The eight [architecture decision records](/adr/), verbatim
- [`CHANGELOG.md`](https://github.com/serkanalgur/termmosaic/blob/main/CHANGELOG.md),
  hand-maintained, with a Known Limitations section

MIT licensed. Informed by [Ratatui](https://github.com/ratatui/ratatui),
[Bubble Tea](https://github.com/charmbracelet/bubbletea),
[Textual](https://github.com/Textualize/textual) and
[OpenTUI](https://github.com/anomalyco/opentui).