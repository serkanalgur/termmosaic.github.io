---
title: "Catalog and API"
weight: 61
description: "Generated from the framework's capture manifest: every widget, its constructor, its MinSize and its capture sizes."
toc: true
---

# Catalog and API

**This page is generated** by `scripts/gen_reference.py` from
`static/captures/manifest.json`, which is itself produced by
`cmd/capture` in the framework repository. It therefore cannot claim
anything the framework does not do: every row below is a fact about a
widget that was constructed and rendered.

**24 widgets.** Counted, not estimated — see
[the catalog index](/widgets/) for what is and is not included.

> **pkg.go.dev is the authority on signatures.**
> <https://pkg.go.dev/github.com/serkanalgur/termmosaic> is generated from the source and can
> never be out of date. This page is generated from a build artefact,
> which is a weaker guarantee, and it exists because it carries the
> things godoc does not: `MinSize()`, the capture widths, and which
> package each widget belongs to.

## Widgets by package

### Core — `widgets/block`

[pkg.go.dev/widgets/block](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/block)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`Block`](/widgets/block/) | `block.New(r buffer.Rect) *block.Block` | 5×5 | 40×9 × 80×9 × 120×9 |

### Core — `widgets/basic`

[pkg.go.dev/widgets/basic](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/basic)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`Text`](/widgets/text/) | `basic.NewText(r buffer.Rect, spans []buffer.Span) *basic.Text` | — | 40×3 × 80×3 × 120×3 |
| [`Paragraph`](/widgets/paragraph/) | `basic.NewParagraph(r buffer.Rect, spans []buffer.Span) *basic.Paragraph` | — | 40×10 × 80×9 × 120×7 |

### Core — `widgets/split`

[pkg.go.dev/widgets/split](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/split)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`Split`](/widgets/split/) | `split.New(d layout.Direction, panes ...termmosaic.Widget) *split.Split` | 3×1 | 40×11 × 80×11 × 120×11 |

### Forms — `widgets/form`

[pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`TextInput`](/widgets/textinput/) | `form.NewTextInput(r buffer.Rect) *form.TextInput` | 1×1 | 40×3 × 80×3 × 120×3 |
| [`TextArea`](/widgets/textarea/) | `form.NewTextArea(r buffer.Rect) *form.TextArea` | 1×1 | 40×7 × 80×7 × 120×7 |
| [`Select`](/widgets/select/) | `form.NewSelect(r buffer.Rect, labels []string) *form.Select` | 1×1 | 40×9 × 80×9 × 120×9 |
| [`Checkbox`](/widgets/checkbox/) | `form.NewCheckbox(r buffer.Rect, label string) *form.Checkbox` | 1×5 | 40×5 × 80×5 × 120×5 |
| [`Radio`](/widgets/radio/) | `form.NewRadio(r buffer.Rect, labels []string) *form.Radio` | 6×1 | 40×6 × 80×6 × 120×6 |
| [`Toggle`](/widgets/toggle/) | `form.NewToggle(r buffer.Rect, label string) *form.Toggle` | 6×1 | 40×3 × 80×3 × 120×3 |
| [`Tabs`](/widgets/tabs/) | `form.NewTabs(r buffer.Rect, labels []string) *form.Tabs` | 1×1 | 40×4 × 80×4 × 120×4 |
| [`Button`](/widgets/button/) | `form.NewButton(r buffer.Rect, label string) *form.Button` | 3×1 | 40×3 × 80×3 × 120×3 |
| [`KeyHint`](/widgets/keyhint/) | `form.NewKeyHint(r buffer.Rect, bindings []form.Binding) *form.KeyHint` | 1×1 | 40×3 × 80×3 × 120×3 |

### Data — `widgets/data`

[pkg.go.dev/widgets/data](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/data)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`List`](/widgets/list/) | `data.NewList(r buffer.Rect, items ...data.ListItem) *data.List` | 10×3 | 40×11 × 80×11 × 120×11 |
| [`Table`](/widgets/table/) | `data.NewTable(r buffer.Rect, cols ...data.Column) *data.Table` | 12×4 | 40×10 × 80×10 × 120×10 |
| [`Tree`](/widgets/tree/) | `data.NewTree(r buffer.Rect, nodes ...data.Node) *data.Tree` | 14×4 | 40×13 × 80×13 × 120×13 |
| [`Pager`](/widgets/pager/) | `data.NewPager(r buffer.Rect) *data.Pager` | 10×4 | 40×11 × 80×11 × 120×11 |

### Visualization — `widgets/viz`

[pkg.go.dev/widgets/viz](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/viz)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`ProgressBar`](/widgets/progressbar/) | `viz.NewProgressBar(r buffer.Rect) *viz.ProgressBar` | 14×3 | 40×4 × 80×4 × 120×4 |
| [`Gauge`](/widgets/gauge/) | `viz.NewGauge(r buffer.Rect) *viz.Gauge` | 11×7 | 40×11 × 80×9 × 120×9 |
| [`Meter`](/widgets/meter/) | `viz.NewMeter(r buffer.Rect) *viz.Meter` | 18×3 | 40×3 × 80×3 × 120×3 |
| [`Sparkline`](/widgets/sparkline/) | `viz.NewSparkline(r buffer.Rect) *viz.Sparkline` | 5×3 | 40×3 × 80×3 × 120×3 |
| [`BarChart`](/widgets/barchart/) | `viz.NewBarChart(r buffer.Rect) *viz.BarChart` | 8×6 | 40×11 × 80×11 × 120×11 |

### Navigation — `widgets/menu`

[pkg.go.dev/widgets/menu](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/menu)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`Menu`](/widgets/menu/) | `menu.New(r buffer.Rect, items ...menu.Item) *menu.Menu` | 16×4 | 40×14 × 80×14 × 120×14 |

### Modality — `widgets/dialog`

[pkg.go.dev/widgets/dialog](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/dialog)

| Widget | Constructor | `MinSize()` | Captures |
| --- | --- | --- | --- |
| [`Dialog`](/widgets/dialog/) | `dialog.New(r buffer.Rect, v dialog.Variant) *dialog.Dialog` | 28×4 | 40×11 × 80×11 × 120×11 |

**`MinSize()` includes the widget's own chrome**, and every value above
was **called**, not parsed — `NewTable(rect, cols).MinSize()` returns the
real answer even though the thresholds are private constants. The
framework does nothing with it; what to do when the available space is
below it is the application's decision.

## Packages

| Package | What it holds |
| --- | --- |
| *(root)* | The root package: the `Widget`, `Focusable` and `Minimizable` interfaces, plus the event types. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic) |
| `buffer` | The 16-byte `Cell`, `Buffer`, `SubBuffer`, `Span`, `Style`, `Colour`, borders and the span writers. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/buffer) |
| `geometry` | Rectangles, `Align`, `ClampCount`, `Budget`, `Region` and `Priority` — the shared responsive arithmetic. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/geometry) |
| `layout` | The constraint solver: `Length`, `Min`, `Max`, `Percentage`, `Ratio`, `Fill`, `Solve`, `Rect`. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/layout) |
| `input` | `Decode`, `Parser`, `Source`, `Config` — the input layer. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/input) |
| `render` | `Renderer`, `Config`, `Pacer`, the cursor, and the encode-time colour and NO_COLOR decisions. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/render) |
| `term` | `Terminal` and `Sink` — the two narrow interfaces, with the `x/sys` implementation and the headless sink. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/term) |
| `headless` | The in-memory `Sink` and its cell-grid screen model, for tests without a terminal. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/headless) |
| `virtual` | The row-virtualization engine shared by `List`, `Table` and `Tree`. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/virtual) |
| `keymap` | Named commands and chords: `Command`, `CommandID`, `Binding`, `Entry`, `Ctx`, a 16-byte comparable `Chord`, and resolution by context specificity at 0 allocs. Shipped in v0.6.0. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/keymap) |
| `widgets/block` | `Block` — the catalog's only owner of borders and titles. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/block) |
| `widgets/basic` | `Text` and `Paragraph`. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/basic) |
| `widgets/split` | `Split` — the pane composer. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/split) |
| `widgets/form` | `TextInput`, `TextArea`, `Select`, `Checkbox`, `Radio`, `Toggle`, `Tabs`, `Button`, `KeyHint`. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form) |
| `widgets/data` | `List`, `Table`, `Tree`, `Pager`. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/data) |
| `widgets/viz` | `ProgressBar`, `Gauge`, `Meter`, `Sparkline`, `BarChart`. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/viz) |
| `widgets/menu` | `Menu` — a navigable tree with submenus to arbitrary depth. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/menu) |
| `widgets/dialog` | `Dialog` — a modal with info, confirm and choice variants. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/dialog) |
| `widgets/cacheaudit` | The catalog-wide cache-audit gate (ADR 0007 §3): every finding fails the build. [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/cacheaudit) |
| `widgets/widgettest` | The headless widget-test harness: `Capture`, the cache-audit helpers, and the screen model the examples assert against. **Public, and therefore frozen at v1.0 by default — whether that surface should be frozen is undecided.** [pkg.go.dev](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/widgettest) |

## The one interface that is held fixed

```go
type Widget interface {
    Bounds() Rect
    Draw(buf *buffer.Buffer)
    Invalidate()
    Handle(Event) bool
}
```

**Four methods, unchanged across all ten architecture decisions, and
frozen at v1.0.0** under the stability promise. That is the most stable
thing in the project: a widget written against it today is the part most
likely to still compile at v1.1.0. The two optional interfaces are
`Focusable` and `Minimizable` — both discoverable by a type assertion,
both costing nothing to omit.

See [Widgets and focus](/concepts/widgets-and-focus/) for what `Draw` may
and may not do, and [ADR 0003](/adr/0003-renderer-mode/) for why the
interface is this small.

## Related

- [The catalog](/widgets/) — the same 24, one page each, with captures.
- [Architecture decisions](/adr/) — the reasoning behind every row above.
- [Limitations](/limitations/) — what the framework does not do.
