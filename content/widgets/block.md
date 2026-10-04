---
title: "Block"
weight: 1
description: "A bordered, titled, padded rectangle that other widgets draw inside."
widgetName: "Block"
widgetPackage: "widgets/block"
widgetConstructor: "block.New(r buffer.Rect) *block.Block"
capture: "block"
---

A bordered, titled, padded rectangle that other widgets draw inside.

Package `widgets/block`. API reference: [pkg.go.dev/widgets/block](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/block).

Block is a bordered region with an optional title. It draws chrome only: it has no content of its own beyond the background and the border.

The zero Block draws no border (Border is BorderNone) with the terminal's own colours, which is a legal and unremarkable block. It is usable as constructed.

A Block is a plain value in every respect that matters: it is not safe for concurrent use, because SetBounds and Draw race by design — the renderer owns Bounds between frames (ADR 0003).

## Rendered output

{{< widget-capture block >}}

> **About this capture.** A Block draws chrome only — it has no children. What goes inside it is the application's business: wrap a widget, or use a Split to place several. The capture shows the padding and the interior band, which is the part of the widget that is actually drawn.

## Package context

Package block provides Block, the catalog's only owner of borders and titles.

ADR 0008 §2 fixes Block's contract for the whole catalog, and this file is that contract rather than a widget's opinion of it. List, Table, Tree, Pager, Tabs and everything else chrome-bearing compose a Block or call one; none of them contains a glyph table, a corner loop or a title threshold. If a second border appears anywhere in TermMosaic, that is a bug of exactly the kind this package exists to make impossible — the same collision that two copies of internal/ansi.Style had already produced in this repository.

Everything visible here comes from buffer: every rune from buffer.BorderStyle.Glyphs, every style from a buffer.Style read through Resolved, every title run from a buffer.Span. Block spells no border rune and invents no styling vocabulary.

## Constructing it

```go
block.New(r buffer.Rect) *block.Block
```

The zero value is a usable `Block`: `Border` is `BorderNone` and the colours are the terminal's own. Set a border and you get a bordered region; that is the whole widget.

- `Border` — `buffer.BorderStyle` — one of `BorderNone`, `BorderPlain`, `BorderRounded`, `BorderDouble`, `BorderThick`, `BorderASCII`. The catalog's only border vocabulary; the glyph tables live in `buffer` (ADR 0008).
- `BorderStyle` — `buffer.Style` — foreground/background/attributes for the border and title. Unset resolves to the terminal's own colours.
- `Background` — `buffer.Style` — the interior fill. Drawn across the whole rect, so a widget drawn inside it must not assume the default background survives.
- `TitleAlign` — `geometry.Align` — where the title sits: start, centre or end.
- `Ascii` — `bool` — force the ASCII glyph table even on a terminal that supports Unicode. This is the degradation lever, not a style choice.

## When not to use it

**Do not use `Block` as a container that holds other widgets.** It does not. `Block` draws a border, a title and a background; it has no children and no idea what goes inside it. If you need the border to move with the content, put the border `Block` and the content widget in the same solved rect yourself, or use [`Split`](/widgets/split/), which owns that arrangement for panes.

**Do not reach for it to group visually when nothing needs a border.** ADR 0008 fixes `Block` as the single owner of borders and titles across the whole catalog so there is exactly one place a corner glyph is decided. Adding a second, differently-shaped outline — an underline, a `─` rule drawn by hand, a highlighted band — is how that collapses. Most grouping is better served by spacing from [`layout.Solve`](/concepts/layout/).

**Do not use it where a widget needs to draw to the screen edge.** A `Block` with `Padding: 1` shrinks the usable interior by two cells on each axis and the widget inside will report a `Bounds()` that does not match the space you thought you gave it. Size the inner widget from the block's rect, not from the outer one.

**Do not use it as a window that can be moved, resized or closed.** `Block` is a value, not a surface: it has no z-order, no drag, no hit testing and no relationship to anything but the rectangle you handed it.

**Instead:** [`Split`](/widgets/split/) for panes, [`layout.Solve`](/concepts/layout/) for grouping, and [`Text`](/widgets/text/) or [`Paragraph`](/widgets/paragraph/) for the content itself.

## Related

- [`Split`](/widgets/split/) — the only other widget that hands rectangles to other widgets.
- [`Paragraph`](/widgets/paragraph/) — the widget most often drawn inside one.
- [Styling and spans](/concepts/styling/) — why there is no theme and where `Style` values come from.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/block` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/block)
