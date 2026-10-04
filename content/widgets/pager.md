---
title: "Pager"
weight: 17
description: "A scrollable long text with search, match highlighting and a position readout."
widgetName: "Pager"
widgetPackage: "widgets/data"
widgetConstructor: "data.NewPager(r buffer.Rect) *data.Pager"
capture: "pager"
---

A scrollable long text with search, match highlighting and a position readout.

Package `widgets/data`. API reference: [pkg.go.dev/widgets/data](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/data).

Pager is a read-only view over a large text, wrapped to its width, with search.

It is Focusable: keys are consumed only while it has focus. It cannot be edited — that is what TextArea in widgets/form is for, and a pager that accepted keystrokes would need a caret, a selection and an undo history to be worth having.

## Rendered output

{{< widget-capture pager >}}

## Package context

Package data provides the catalog's scrolling data widgets: List, Table, Tree and Pager.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1). The only place a screen dimension is read is inside a test.
- It repaints its whole Bounds() before drawing content (rule 3). Every widget here does that by composing widgets/block.Block, whose Draw fills the rect in Background before it draws anything else — the sanctioned way to express it (ADR 0008 §2). No widget in this package draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Anything derived from a widget's own size — which columns are visible, which chrome survives the budget, which rows map to which items — is computed in the size-change check, cached against the rect it was computed for, and only read in Draw.
- Draw is total. Every rect including 0x0 and 1x1 is defined, and a widget below its own MinSize draws its minimum layout clipped rather than blanking itself (ADR 0007 §4).
- Colour is never the only signal. Selection is carried by a marker column as well as by SelectedStyle, the tree's expansion state by a glyph, and the pager's matches by a rendition attribute rather than a hue.

## Constructing it

```go
data.NewPager(r buffer.Rect) *data.Pager
```

`NewPager` takes only a rect; the text arrives through `SetText`. It is read-only by construction.

- `Status` — `bool` — draw the status line: position readout and match count.
- `MatchStyle` — `buffer.Style` — a search match. The match is also counted and reported in the status line, so it is not colour-only.

## Key contract

Consumed only while focused.

| Keys | Effect |
| --- | --- |
| `up / down` | scroll one visual row |
| `page up/down` | scroll one screen |
| `home / end` | first / last screen |
| `n` | jump to the next match of the current query |
| `N (shift+n)` | jump to the previous match |
| `wheel up/down` | scroll WITHOUT moving anything else |
| `press` | move the caret to the pressed position — a pager has none, so a press is consumed and does nothing but take focus |

The QUERY ITSELF IS THE APPLICATION'S: SetQuery takes it, because a read-only widget has no way to receive typed text without becoming an editor. KeyTab is NOT consumed.

## What it costs

O(visible cells) per frame: the wrap of the visible lines is recomputed each frame into a scratch buffer the pager owns, so there is no cache to invalidate on a resize and nothing to allocate. Text can be any size; TestPagerScrollsAHugeDocument is the evidence.

## When not to use it

**Do not use it for text the user must edit.** It cannot be edited, deliberately — a pager that accepted keystrokes would need a caret, a selection and an undo history to be worth having. Editing long text is [`TextArea`](/widgets/textarea/), with the caveat that it has no rendered selection in v0.1.0.

**Do not use it for short text.** A paragraph that fits does not need a scrollbar, a search field and a status line.

**Do not use it as the only view of something the user needs to select from.** There is no pager selection in v0.1.0. It shows and searches; it does not hand back a line.

**Do not expect search to be interactive as you type.** Search is a key contract, not a live filter: you set the query, the pager highlights matches and reports the count, and moving between them is a key. Designing around a search-as-you-type expectation means building it yourself.

**Instead:** [`Paragraph`](/widgets/paragraph/) when it fits, [`TextArea`](/widgets/textarea/) to edit it.

## Related

- [`Paragraph`](/widgets/paragraph/) — the non-scrolling counterpart.
- [`TextArea`](/widgets/textarea/) — the editable counterpart, and its selection gap.
- [Data display](/guides/data-display/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/data` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/data)
