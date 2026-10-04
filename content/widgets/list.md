---
title: "List"
weight: 14
description: "A scrollable, selectable list with a marker gutter and a scrollbar."
widgetName: "List"
widgetPackage: "widgets/data"
widgetConstructor: "data.NewList(r buffer.Rect, items ...data.ListItem) *data.List"
capture: "list"
---

A scrollable, selectable list with a marker gutter and a scrollbar.

Package `widgets/data`. API reference: [pkg.go.dev/widgets/data](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/data).

List is a selectable, scrollable list of items.

It is Focusable: keys are consumed only while it has focus, and a press inside its rectangle takes focus as well as selecting, so a click is a complete interaction without the application writing a click handler.

## Rendered output

{{< widget-capture list >}}

> **About this capture.** The scrollbar thumb's POSITION is the signal; its colour is not.

## Package context

Package data provides the catalog's scrolling data widgets: List, Table, Tree and Pager.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1). The only place a screen dimension is read is inside a test.
- It repaints its whole Bounds() before drawing content (rule 3). Every widget here does that by composing widgets/block.Block, whose Draw fills the rect in Background before it draws anything else — the sanctioned way to express it (ADR 0008 §2). No widget in this package draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Anything derived from a widget's own size — which columns are visible, which chrome survives the budget, which rows map to which items — is computed in the size-change check, cached against the rect it was computed for, and only read in Draw.
- Draw is total. Every rect including 0x0 and 1x1 is defined, and a widget below its own MinSize draws its minimum layout clipped rather than blanking itself (ADR 0007 §4).
- Colour is never the only signal. Selection is carried by a marker column as well as by SelectedStyle, the tree's expansion state by a glyph, and the pager's matches by a rendition attribute rather than a hue.

## Constructing it

```go
data.NewList(r buffer.Rect, items ...data.ListItem) *data.List
```

`NewList` takes a variadic of `data.ListItem` — a concrete type, which is one of the reasons the catalogue's per-widget pages are generated from a registry rather than by reflection.

- `Marker` — `string` — the gutter glyph beside the selected row.
- `Scrollbar` — `bool` — draw the scrollbar. Its **position** is the signal; its colour is not.
- `SelectedStyle` — `buffer.Style` — the selected row. Unset means reverse video, so selection survives `NO_COLOR`.

## Key contract

Consumed only while focused. Every key also scrolls the selection into view, which is virtual's ScrollIntoView rather than a per-widget re-centring rule (ADR 0007 §6 rule 2: clamp, do not recentre).

| Keys | Effect |
| --- | --- |
| `up / down` | move the selection by one row |
| `page up/down` | move it by a screen, less one row of overlap |
| `home / end` | first / last row |
| `enter, space` | activate the selection, calling OnActivate |
| `wheel up/down` | scroll WITHOUT moving the selection |
| `press` | select the pressed row and take focus |

KeyTab is NOT consumed, so a form can move focus out of a list with the keyboard exactly as it moves out of a text input.

## What it costs

O(visible rows) per frame, whatever the item count. The scroll arithmetic is virtual.Model's and the row count is derived from the interior height with geometry.ClampCount; nothing in Draw or Handle touches the items slice beyond the rows it is painting. BenchmarkList100K and TestListHundredThousandItems are the evidence.

## When not to use it

**Do not use it for data with more than one field per row.** A `List` item is one string. Two or more columns is [`Table`](/widgets/table/), and bolting a fixed-width formatter onto `List` items is how you end up with a table that cannot scroll horizontally and misaligns on a wide glyph.

**Do not use it above roughly 10,000 items if you are also updating per frame.** The claim is *flat* cost, not free: 10,000 items render in 13,320 ns and 100,000 in 14,242 — seven percent for ten times the data, at zero allocations — and those figures are for the render. Mutating the item list invalidates; doing that every frame is your choice, not the widget's.

**Do not use it where the rows have a natural grouping or hierarchy.** That is [`Tree`](/widgets/tree/), and the indentation and twisties are part of what makes a hierarchy legible.

**Do not use it for a long body of text.** A list scrolls; it does not wrap, and each item is truncated to the width. Prose you need to read is [`Pager`](/widgets/pager/).

**Do not expect it to handle keys when it does not have focus.** It is `Focusable`: keys are consumed only while focused, and a press inside its rect takes focus as well as selecting. Move focus deliberately.

**Instead:** [`Table`](/widgets/table/) for columns, [`Tree`](/widgets/tree/) for hierarchy, [`Pager`](/widgets/pager/) for prose.

## Related

- [`Table`](/widgets/tree/)-style multi-column data — [`Table`](/widgets/table/), same package, same focus contract.
- [Virtualization](/concepts/virtualization/) — the engine behind the flat-cost claim.
- [Data display](/guides/data-display/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/data` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/data)
