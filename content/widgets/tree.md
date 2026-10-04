---
title: "Tree"
weight: 16
description: "A hierarchy with expandable nodes, keyboard navigation and lazy row rendering."
widgetName: "Tree"
widgetPackage: "widgets/data"
widgetConstructor: "data.NewTree(r buffer.Rect, nodes ...data.Node) *data.Tree"
capture: "tree"
---

A hierarchy with expandable nodes, keyboard navigation and lazy row rendering.

Package `widgets/data`. API reference: [pkg.go.dev/widgets/data](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/data).

Tree shows a hierarchy with expandable nodes, keyboard navigation and lazy rendering of the visible rows.

It is Focusable on the same terms as List and Table.

## Rendered output

{{< widget-capture tree >}}

> **About this capture.** Expansion is state, and a still frame shows it only by the twisties and the indent. The example program is where a reader sees a node open.

## Package context

Package data provides the catalog's scrolling data widgets: List, Table, Tree and Pager.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1). The only place a screen dimension is read is inside a test.
- It repaints its whole Bounds() before drawing content (rule 3). Every widget here does that by composing widgets/block.Block, whose Draw fills the rect in Background before it draws anything else — the sanctioned way to express it (ADR 0008 §2). No widget in this package draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Anything derived from a widget's own size — which columns are visible, which chrome survives the budget, which rows map to which items — is computed in the size-change check, cached against the rect it was computed for, and only read in Draw.
- Draw is total. Every rect including 0x0 and 1x1 is defined, and a widget below its own MinSize draws its minimum layout clipped rather than blanking itself (ADR 0007 §4).
- Colour is never the only signal. Selection is carried by a marker column as well as by SelectedStyle, the tree's expansion state by a glyph, and the pager's matches by a rendition attribute rather than a hue.

## Constructing it

```go
data.NewTree(r buffer.Rect, nodes ...data.Node) *data.Tree
```

`NewTree` takes a variadic of `data.Node`. Only the roots: children hang off their parents, and a subtree is only rendered when expanded.

- `CollapsedRune` — `rune` — the twisty on a closed node.
- `ExpandedRune` — `rune` — the twisty on an open node.
- `LeafRune` — `rune` — the marker on a node with no children. Open and closed are different glyphs, so the state is visible without colour.
- `Scrollbar` — `bool` — draw the scrollbar.

## Key contract

Consumed only while focused. Selection is a ROW, so it follows expansion: with a node collapsed, the rows below it are simply gone.

| Keys | Effect |
| --- | --- |
| `up / down` | move the selection by one visible row |
| `page up/down` | move it by a screen, less one row of overlap |
| `home / end` | first / last visible row |
| `right` | expand the selected node, or step into it if it is open |
| `left` | collapse the selected node, or step out to its parent |
| `enter, space` | toggle the selected node |
| `wheel up/down` | scroll WITHOUT moving the selection |
| `press` | select the pressed row and take focus |

KeyTab is NOT consumed, as in List and Table.

## When not to use it

**Do not use it for a shallow list.** A one-level set of options with no nesting is [`List`](/widgets/list/) or [`Select`](/widgets/select/), and a tree spends an indent and a twisty per row on structure the data does not have.

**Do not use it when the hierarchy is wide and shallow.** Expansion state is per node and the twisty column costs cells on every row. A thousand siblings under one parent is a list.

**Do not use it expecting the whole tree to be materialised lazily for free.** Laziness is real — only the visible rows are rendered — but the **nodes** are yours to provide, and expansion state is yours to hold. A tree over a filesystem you have not walked is a tree over nothing.

**Do not use it where a capture or a screenshot will be your documentation.** Expansion is state, and a still frame shows it only as twisties and indentation. If you are trying to show a reader what expanding a node looks like, you need the program.

**Instead:** [`List`](/widgets/list/) when the data is flat, [`Table`](/widgets/table/) when it is tabular.

## Related

- [`List`](/widgets/list/) and [`Table`](/widgets/table/) — the other two data widgets.
- [Virtualization](/concepts/virtualization/)
- [Data display](/guides/data-display/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/data` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/data)
