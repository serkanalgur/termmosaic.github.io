---
title: "Table"
weight: 15
description: "Rows in columns, with a header, a selection and horizontal scrolling."
widgetName: "Table"
widgetPackage: "widgets/data"
widgetConstructor: "data.NewTable(r buffer.Rect, cols ...data.Column) *data.Table"
capture: "table"
---

Rows in columns, with a header, a selection and horizontal scrolling.

Package `widgets/data`. API reference: [pkg.go.dev/widgets/data](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/data).

Table shows rows in columns, with a header, a selection and horizontal scrolling.

It is Focusable on the same terms as List: keys are consumed only while it has focus, and a press inside it selects a row and takes focus.

## Rendered output

{{< widget-capture table >}}

## Package context

Package data provides the catalog's scrolling data widgets: List, Table, Tree and Pager.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1). The only place a screen dimension is read is inside a test.
- It repaints its whole Bounds() before drawing content (rule 3). Every widget here does that by composing widgets/block.Block, whose Draw fills the rect in Background before it draws anything else — the sanctioned way to express it (ADR 0008 §2). No widget in this package draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Anything derived from a widget's own size — which columns are visible, which chrome survives the budget, which rows map to which items — is computed in the size-change check, cached against the rect it was computed for, and only read in Draw.
- Draw is total. Every rect including 0x0 and 1x1 is defined, and a widget below its own MinSize draws its minimum layout clipped rather than blanking itself (ADR 0007 §4).
- Colour is never the only signal. Selection is carried by a marker column as well as by SelectedStyle, the tree's expansion state by a glyph, and the pager's matches by a rendition attribute rather than a hue.

## Constructing it

```go
data.NewTable(r buffer.Rect, cols ...data.Column) *data.Table
```

`NewTable` takes a variadic of `data.Column`. A column is a header, a width and an accessor; the column definitions are where most of the thinking goes.

- `Header` — `bool` — draw the header row. Toggling this invalidates, and ADR 0007's amendment is about exactly this class of bug: a widget that caches column widths on `Bounds()` and is handed a new flag renders the old layout permanently.
- `Marker` — `string` — the gutter glyph beside the selected row.
- `Scrollbar` — `bool` — draw the vertical scrollbar.

## Key contract

Consumed only while focused.

| Keys | Effect |
| --- | --- |
| `up / down` | move the selection by one row |
| `page up/down` | move it by a screen, less one row of overlap |
| `home / end` | first / last row |
| `shift+home/end` | first / last column |
| `left / right` | scroll one column horizontally |
| `enter, space` | activate the selection, calling OnActivate |
| `wheel up/down` | scroll vertically WITHOUT moving the selection |
| `wheel + shift` | scroll horizontally |
| `press` | select the pressed row and take focus |

KeyTab is NOT consumed, for the same reason List does not consume it.

## What it costs

O(visible rows × visible columns) per frame, and the same on a resize. It is the horizontal axis, the header, the gutter and the scrollbar that are each O(1) or O(columns), never O(rows).

## When not to use it

**Do not use it for a hierarchy.** It is flat. Nesting is [`Tree`](/widgets/tree/), and a `Table` with a manually indented first column loses the twisties, the expand keys and the lazy row rendering that make a `Tree` usable at depth.

**Do not use it when a column's content must be laid out, not measured.** Column widths are computed from content and from the space available. A column holding a widget, a multi-line cell or anything with its own alignment is a composition problem — render that cell yourself and pass a string.

**Do not use it and then fight the horizontal scrollbar.** When the columns do not fit, `Table` scrolls horizontally and keeps both offsets — a column index and a cell position. Scrolling to the end clamps onto the right-hand edge of the content, which is generally not a column start, so the last column can be partly visible. That is deliberate and tested; it is not a bug to work around by shrinking your columns.

**Do not use it for one field per row.** [`List`](/widgets/list/) is the smaller widget and does not compute column widths.

**Do not expect column selection.** There is none in v0.1.0. Selection is one row.

**Instead:** [`List`](/widgets/list/) for one field, [`Tree`](/widgets/tree/) for nesting, [`Split`](/widgets/split/) plus a `List` for a master/detail pane.

## Related

- [`List`](/widgets/list/) — the single-column sibling, and the comparison the benchmarks use.
- [Virtualization](/concepts/virtualization/)
- [Data display](/guides/data-display/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/data` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/data)
