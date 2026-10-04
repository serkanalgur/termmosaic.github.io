---
title: "Text"
weight: 2
description: "A single line of styled spans, aligned within its rectangle."
widgetName: "Text"
widgetPackage: "widgets/basic"
widgetConstructor: "basic.NewText(r buffer.Rect, spans []buffer.Span) *basic.Text"
capture: "text"
---

A single line of styled spans, aligned within its rectangle.

Package `widgets/basic`. API reference: [pkg.go.dev/widgets/basic](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/basic).

Text renders styled spans on one line.

It is the smallest widget in the catalog and the one most often composed: a label in a form, a value beside it, a status line. It truncates rather than wraps, because wrapping is Paragraph's job and a widget that both wrapped and did not would be two widgets.

## Rendered output

{{< widget-capture text >}}

## Package context

Package basic provides the two text widgets: Text, which writes styled spans on one line, and Paragraph, which wraps them.

Both follow the same two rules, which are the rules every widget in the catalog follows:

- The available space is Bounds(), never buf.Size(). The buffer is the screen; the rect is the widget's space (ADR 0007 §1 rule 1).
- Nothing derived from the size is built in Draw. Wrap and Truncate both allocate, so Paragraph caches its Wrapped and Text caches its truncation against the rect they were computed for, and recompute only when Bounds() differs (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
basic.NewText(r buffer.Rect, spans []buffer.Span) *basic.Text
```

`NewText` takes the spans up front. Because the span list is parsed once rather than per frame, mutating the slice contents afterwards does not repaint — replace `Text.Spans` and call `Invalidate()`.

- `Spans` — `[]buffer.Span` — the styled runs on the line. Parsed once at construction, which is why `Draw` allocates nothing.
- `Align` — `geometry.Align` — start, centre or end within `Bounds()`.
- `Ascii` — `bool` — force ASCII for anything that would otherwise need a Unicode glyph.

## When not to use it

**Do not use it for text that must wrap.** `Text` is one line and truncates with a marker; it will not reflow. Reflowing is [`Paragraph`](/widgets/paragraph/), and the difference is a real one — reaching for `Text` with a long string produces a silently truncated label rather than an error.

**Do not use it for anything the user can edit.** There is no caret and no key contract; it is a display widget. Editing is [`TextInput`](/widgets/textinput/).

**Do not use it to show a value whose length changes per frame** without calling `Invalidate()`. `Text` caches its layout against its rect and its spans (ADR 0007 §3); a widget whose setter writes a field `Draw` reads must invalidate in that setter, or the old text stays on screen permanently. This is the caching bug ADR 0007's 2026-10-04 amendment is about, and `Text` is not exempt from it.

**Instead:** [`Paragraph`](/widgets/paragraph/) to wrap, [`TextInput`](/widgets/textinput/) to edit.

## Related

- [`Paragraph`](/widgets/paragraph/) — the same spans, wrapping.
- [Buffers and cells](/concepts/buffer/) — what `Span` writes into.
- [Responsiveness and the size budget](/concepts/responsiveness/) — why `Draw` re-derives from `Bounds()`.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/basic` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/basic)
