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
> **v0.5.2**. Read [Limitations](/limitations/) before you rely on any of it —
> the honest list is short, specific, and load-bearing.

```go
go get github.com/serkanalgur/termmosaic@v0.5.2
```

Then read the [quickstart](/getting-started/quickstart/), or run the example:

```
go run github.com/serkanalgur/termmosaic/examples/markets@v0.5.2
```

## What's new in v0.5.2

A minor bump, and the reason is a decision with a number attached:
**[ADR 0010](/adr/0010-mouse-routing.md) settles who receives a mouse event** —
and the answer exposed three widgets that were getting it wrong.

- **`form.Tabs`, `form.Select` and `form.Radio` consumed a wheel notch regardless
  of where the pointer was.** `Tabs.Handle` tested the wheel before the
  `switch ev.Kind`, so a notch never reached the bounds check its click path
  already used; `Select` and `Radio` reached the same place through the shared
  `optionlist` helper. A tab row, a select or a radio group took the wheel from
  whatever sat beneath it. **Per ADR 0010, a widget handles a pointer event only
  when the pointer is inside its `Bounds()`** — with two stated exemptions: a
  *release* ends a drag wherever the pointer is, and a *drag* continues outside
  `Bounds` once a press has claimed it.
- **`examples/markets` behaviour changes.** Its tab row is first in the focus
  ring, so it swallowed **every** notch in the app. A notch over a KPI tile, which
  no widget in the ring owns, is now consumed by nobody rather than scrolling the
  tab row by three.

The ADR also states which widgets decline a wheel outright: `Button`, `Checkbox`,
`Toggle` and `Split` have nothing to scroll, and `TextInput`/`TextArea` decline
**by decision** — `TextArea` wheel-to-scroll is plausible, but adding it under a
routing ADR would answer a different question.

## What's new in v0.5.1

A minor bump, and the reason is seven defects: **the style a widget computes for
one cell was stopping where two code paths diverged, and never reaching the text
beside it.** Three of the five releases before this existed because of this one
class.

- **`Dialog`: `ChoiceFocusStyle` never reached the choice label** — the row was
  filled and marked in the focus style while its *text* was written in the
  unfocused style. With default styles the focused choice rendered `attr=none` on
  an `attr=reverse` row: unreadable dark-on-dark, on exactly the row the reader
  is meant to look at.
- **`Button`: `FocusStyle` and `DisabledStyle` reached the ring and the fill but
  not the label**, so a disabled button rendered blue brackets around
  default-coloured text. The field's own documentation already promised otherwise.
- **`Table`: `SelectedStyle` and `ItemStyle` filled the row but never reached the
  cell text**, and `HeaderStyle` was documented as "patched with `ItemStyle`" and
  never was. Both now do what their docs said. **The trade, stated plainly:** on
  the selected row a cell's own `Style` and its column's `CellStyle` no longer
  show, because the row style now overrides a single-span cell — a multi-span
  cell keeps its own. And the header now carries `ItemStyle`'s **foreground** as
  well as its background, because `Patch` takes both.
- **`Menu`: the check glyph and the submenu arrow were drawn in `ItemStyle` on
  the selected row**, where the row is reversed — the one unreadable thing on it.
- **`Radio`: the focus gutter was styled as a focus mark on every row**, so an
  unfocused group painted a reverse-video stripe down its left edge. The column
  still exists on every row so labels align; only the rendition was wrong.
- **`BarChart`: axis labels overran their column** — a computed centring offset
  was discarded with `_ = lx`, so a label wider than its column overwrote the next
  category's.

Every one of these renders differently from v0.4.x **because it now renders
correctly**. If your app looks different after upgrading, that is this release
working. The full detail is on the [Limitations](/limitations/) page.

## What's new in v0.5.0

A minor bump, and the reason is the first item: **five exported fields are now
private, so a program that assigns them will not compile.** Start here if you are
arriving at v0.5.x from v0.4.x.

**Breaking — `Pager.Status`, `Split.Spacing`, `Meter.ShowValue`,
`ProgressBar.Label` and `ProgressBar.Percentage` are no longer exported fields.**
Each already had a working setter, so migration is mechanical:

| Before | After |
|---|---|
| `p.Status = on` | `p.SetStatus(on)` |
| `s.Spacing = n` | `s.SetSpacing(n)` |
| `m.ShowValue = on` | `m.SetShowValue(on)` |
| `p.Label = s` | `p.SetLabel(s, st)` |
| `p.Percentage = on` | `p.SetPercentage(on)` |

Read-only accessors exist too: `Status()`, `Spacing()`, `ShowValue()`,
`Percentage()`, `Label()`. The reason is in
[ADR 0007 §3](/adr/0007-responsive-screens/): a widget caches its derived layout
keyed on `Bounds()`, so a field that changes without an `Invalidate()` produces a
stale layout that **nothing ever repairs**. A doc comment saying "call `Invalidate`
after assigning" is a rule with no enforcement, no compile error and no reminder.

- **Eight widgets kept a stale layout cache after a documented setter** — found by
  the new cache-audit mode, not by review: `Pager.SetStatus`, `Select.SetMarker`,
  `BarChart.SetData`, `Meter.SetShowValue`,
  `ProgressBar.SetLabel`/`SetLabelSpans`/`SetPercentage`, `Sparkline.SetValues`,
  and `Split.Spacing` via direct assignment. Each now drops the cached derivation.
- **A cache-audit mode**, specified as ADR 0007 §3's deferred "expensive half": it
  corrupts a widget's cached derivation after a `Draw` and asserts the next frame
  is byte-identical, so this defect class is caught mechanically. Opt-in via
  `render.Config.CacheAudit`, and **zero-allocation when disabled**.
- **`widgets/cacheaudit` now fails the build** when a widget in the catalog is
  flagged, on all three platforms via the existing `go test ./... -race` job.

The gate covers the transitions it names, so the exported raw fields that remain —
`Select.Marker`, `Gauge.ShowValue`, `BarChart.ShowValue`/`Vertical`/`Data`,
`Sparkline.Values`/`Braille`, `TextInput.Placeholder`, `Checkbox.TriState` — are
the same shape but produce no finding today. See
[Limitations](/limitations/#the-v050-field-to-setter-migration-breaks-compilation--read-this-before-upgrading).

## What's new in v0.4.1

A **patch**, and a dependency-only one: `golang.org/x/term` v0.27.0 → v0.29.0 and
`golang.org/x/sys` v0.28.0 → v0.30.0. **No library code changed**, so there is
nothing to adapt to, and the **Go 1.23 floor is preserved** — the pin still keeps
`x/term` off the releases that would raise it. That is the whole release; it
answers [framework issue #4](https://github.com/serkanalgur/termmosaic/issues/4).

## What's new in v0.4.0

A minor bump, and the reason is one fix: **styling you set on a
[`Tree`](/widgets/tree/) used to be silently discarded, and is now honoured.**
That *is* a behavioural change, so it is a minor bump and not a patch.

**If your tree looks different after upgrading, this is why** — and if you had
worked around the old behaviour by compensating in your own styles, remove that
compensation now, because it is double-counting.

- **`Tree` ignored per-node and selected-row styling on the label.** The row
  painter computed the right style for each node — the node's `Style`, falling
  back to `ItemStyle`, and `SelectedStyle` outright when the row was selected —
  and then applied it only to the expander glyph, writing the label through a
  call that took no style at all. So the label was drawn with whatever the
  terminal default happened to be, and only the little marker beside it was
  styled. All three now apply to the label, and the selected style wins on the
  selected row. A deliberately multi-span label keeps its per-span styles, and
  the fill covers the label region only — it cannot reach the marker or the
  indent.

This closes the defect class rather than opening one. v0.3.0 fixed `List` and
`Table`; `Tree` was missed because its row painter computed the style for one
cell and then took a different call for the text beside it, so the computed
style stopped exactly where the two code paths diverged.

The rest of this release is CI and tooling, not the library: **every GitHub
Actions action moved to a Node 24 major** (`checkout` v4→v7, `setup-go` v5→v7,
`golangci-lint-action` v7→v9, `github-script` v7→v9) and **every runner image is
pinned by name** instead of tracking `-latest` (`ubuntu-24.04`, `macos-15`,
`windows-2025`). **All twelve checks then ran green on the v0.4.0 pull request**,
and the post-merge run on `main` was green as well. What that run still does not
cover is recorded on the [Limitations](/limitations/) page rather than glossed.

No capture on this site moved, and that is expected: the generator's tree entry
sets no styles, so the fix is inert there. The full rationale is on the
[Limitations](/limitations/) page.

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
widget through `widgettest.Capture` — the same path the 1,041 top-level test functions assert
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
- **[Architecture decisions](/adr/)** — the ten ADRs, verbatim, with the
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
are built and tested: 26 packages, 1,041 top-level test functions, a zero-allocation frame
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
- The ten [architecture decision records](/adr/), verbatim
- [`CHANGELOG.md`](https://github.com/serkanalgur/termmosaic/blob/main/CHANGELOG.md),
  hand-maintained, with a Known Limitations section

MIT licensed. Informed by [Ratatui](https://github.com/ratatui/ratatui),
[Bubble Tea](https://github.com/charmbracelet/bubbletea),
[Textual](https://github.com/Textualize/textual) and
[OpenTUI](https://github.com/anomalyco/opentui).