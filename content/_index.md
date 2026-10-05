---
title: "TermMosaic"
description: "A terminal UI framework for Go: a cell-buffer renderer with two-tier diffing and 24 ready-to-use widgets. Pre-alpha."
toc: true
---

# A terminal UI framework for Go

**TermMosaic is a cell-buffer renderer plus a catalog of 24 widgets.** The
renderer double-buffers cells, diffs at two tiers, and tracks dirty rectangles;
the catalog is the part that is the point — including the five measurement
widgets that comparable Go TUIs do not ship.

> **TermMosaic is pre-alpha. The public API is not stable and will break
> without notice until v1.0.0.** Everything on this site is accurate as of
> **v0.3.0**. Read [Limitations](/limitations/) before you rely on any of it —
> the honest list is short, specific, and load-bearing.

```go
go get github.com/serkanalgur/termmosaic@v0.3.0
```

Then read the [quickstart](/getting-started/quickstart/), or run the example:

```
go run github.com/serkanalgur/termmosaic/examples/markets@v0.3.0
```

## What's new in v0.3.0

A minor bump, and the reason is the two fixes below: **styling you set on a
[`List`](/widgets/list/) or a [`Table`](/widgets/table/) used to be silently
discarded, and is now honoured.** That *is* a behavioural change, so it is a minor
bump and not a patch.

**If your widgets look different after upgrading, this is why** — and if you had
worked around the old behaviour by compensating in your own styles, remove that
compensation now, because it is double-counting.

- **`List` ignored per-item and selected-row styling.** The style computed for
  each row was never passed to the paint call, so it was computed and thrown
  away. `SelectedStyle`, documented as the selected row's rendition, reached only
  the background fill and never the glyphs. `ItemStyle` and `SelectedStyle` now
  both apply, with the selected style winning on the selected row. A deliberately
  multi-span row keeps its per-span styles — flattening one would mean allocating
  on the frame path.
- **`Table` discarded every cell style.** The sentinel meaning "write these spans
  verbatim" was a *resolved* style rather than an unset one, so the guard never
  fired and each cell's own `Style` was overwritten with the terminal default,
  along with every column's `CellStyle`. Both now render as given.
  `HeadingStyle` was never affected and still works.

Both were documented as taking effect already, so these are fixes to behaviour
that contradicted the documentation. The full rationale is on the
[Limitations](/limitations/) page, and the captures on this site have been
regenerated to show the corrected rendering.

## What's new in v0.2.0

A minor bump, and the reason is the framework fix below: **`Renderer.Post` now
wakes the frame pacer**, which *is* a behavioural change. If you are on v0.1.0 and
your app updated the screen from `Post`, it was almost certainly frozen.

**Fixed**

- **`Renderer.Post` never woke the pacer, so async apps froze.** `Post` queued
  work, callbacks only ran *inside* `Render`, and `Render` was gated on
  `NeedsFrame()` — which cannot become true until the callback runs. An app that
  updates the screen from `Post`, which [ADR 0003](/adr/0003-renderer-mode/)
  documents as the safe way to mutate widget state, painted one frame and idled
  forever. `examples/markets` hit it: live runs painted one empty frame and
  stopped. A regression test now covers it.
- **The diff emitted a cursor move before every wide glyph.** Run suppression
  assumed one cell per rune, but a wide glyph advances the cursor by two. On
  6,000 wide glyphs that was 6,000 cursor moves against the narrow scene's 30, and
  68,832 bytes against 6,233 — about **11×** — for identical output. It now
  advances by the glyph's cell width: **60 moves, 19,443 bytes, 3.12×**. The ASCII
  path is unchanged at **~7,200 ns/op, 0 allocs**.
- **`BarChart` drew every horizontal category label at absolute column 0** — a
  widget writing outside its own rectangle.

**Added**

- **[`Menu`](/widgets/menu/)** — a navigable tree with submenus to arbitrary
  depth.
- **[`Dialog`](/widgets/dialog/)** — a modal with info, confirm and choice
  variants that traps keys and restores focus on close.
- **[`examples/markets`](/guides/dashboards/)** —
  a live Grafana-style finance dashboard: ECB FX from Frankfurter and crypto from
  CoinGecko, **no API key**, and `--offline` for bundled sample data.
- **Keyboard and mouse in both examples.** `hello` gains a focus ring and a `?`
  help overlay; `markets` gains a two-entry focus ring, per-panel key routing,
  wheel and click, pause, and a help overlay.
- **[ADR 0009](/adr/0009-command-and-keymap/)** — the command and keymap layer.
  **Specified, not implemented**: there is no `keymap` package and no command
  palette yet, and widgets still dispatch their own keys.

**Changed**

- **`examples/hello` is genuinely responsive.** It used `Max(46)` inside two
  `Fill(1)`s, so it shrank but never grew — a 200×60 terminal still drew a 46×9
  block floating in the middle. It now spans the terminal, re-arranges across four
  bands, and below 38×8 says so in one line rather than clipping.
- **The catalog is 24 widgets**, up from 22.

Full detail, including the Known Limitations section, is in the framework's
[CHANGELOG.md](https://github.com/serkanalgur/termmosaic/blob/main/CHANGELOG.md).

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
widget through `widgettest.Capture` — the same path the 969 top-level test functions assert
on — and converts `MemorySink.Cells()` to HTML. That is what makes it trustworthy: the
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

## The 24 widgets

| Group | Widgets |
|---|---|
| **Core** | [`Block`](/widgets/block/) [`Text`](/widgets/text/) [`Paragraph`](/widgets/paragraph/) [`Split`](/widgets/split/) |
| **Forms** | [`TextInput`](/widgets/textinput/) [`TextArea`](/widgets/textarea/) [`Select`](/widgets/select/) [`Checkbox`](/widgets/checkbox/) [`Radio`](/widgets/radio/) [`Toggle`](/widgets/toggle/) [`Tabs`](/widgets/tabs/) [`Button`](/widgets/button/) [`KeyHint`](/widgets/keyhint/) |
| **Data** | [`List`](/widgets/list/) [`Table`](/widgets/table/) [`Tree`](/widgets/tree/) [`Pager`](/widgets/pager/) |
| **Visualization** | [`ProgressBar`](/widgets/progressbar/) [`Gauge`](/widgets/gauge/) [`Meter`](/widgets/meter/) [`Sparkline`](/widgets/sparkline/) [`BarChart`](/widgets/barchart/) |
| **Navigation & modality** | [`Menu`](/widgets/menu/) [`Dialog`](/widgets/dialog/) |

That is **24**, counted: every exported type with a `New…` constructor that
satisfies `termmosaic.Widget`. `buffer.Buffer` is deliberately not on the list —
it has `Invalidate()` but no `Bounds`, `Draw` or `Handle`, so it is not a widget,
it is what widgets draw *into*. `widgets/form/optionlist.go` is an unexported
helper behind `Select`, `Tabs` and `KeyHint`, not a widget of its own.

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
- **[Architecture decisions](/adr/)** — the nine ADRs, verbatim, with the
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

The renderer, the input layer, the layout solver and the full 24-widget catalog
are built and tested: 25 packages, 969 top-level test functions, a zero-allocation frame
path. Alongside that: **Windows is a stub that returns a loud error from every
console operation**, **the `keymap` layer is specified but not built — there is no
command palette**, there is **no IME or preedit**, **tmux DCS passthrough is
missing**, **`TextArea` has no rendered selection**, the **colour quantiser is
unvalidated**, and **there is no theme** — by decision, argued in
[ADR 0008](/adr/0008-style-and-text/), not by omission. Everything in that list
is on [Limitations](/limitations/) with the reason.

## Elsewhere

- Source: [github.com/serkanalgur/termmosaic](https://github.com/serkanalgur/termmosaic)
- API reference: [pkg.go.dev/github.com/serkanalgur/termmosaic](https://pkg.go.dev/github.com/serkanalgur/termmosaic) —
  which is never out of date, because it is generated from the source
- The nine [architecture decision records](/adr/), verbatim
- [`CHANGELOG.md`](https://github.com/serkanalgur/termmosaic/blob/main/CHANGELOG.md),
  hand-maintained, with a Known Limitations section

MIT licensed. Informed by [Ratatui](https://github.com/ratatui/ratatui),
[Bubble Tea](https://github.com/charmbracelet/bubbletea),
[Textual](https://github.com/Textualize/textual) and
[OpenTUI](https://github.com/anomalyco/opentui).