---
title: "Paragraph"
weight: 3
description: "Wrapped, styled prose that reflows to the width it is given."
widgetName: "Paragraph"
widgetPackage: "widgets/basic"
widgetConstructor: "basic.NewParagraph(r buffer.Rect, spans []buffer.Span) *basic.Paragraph"
capture: "paragraph"
---

Wrapped, styled prose that reflows to the width it is given.

Package `widgets/basic`. API reference: [pkg.go.dev/widgets/basic](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/basic).

Paragraph renders wrapped, aligned, styled text over as many lines as fit.

It shows the TOP of its content: there is no scrolling here, because scrolling a block of text is Pager's job and a Paragraph that scrolled by itself would be a second scroll model. The paragraph that does not fit is the one that gets dropped content, which is ADR 0007's "information budget" case stated for text: show what fits, clip the rest, never blank.

## Rendered output

{{< widget-capture paragraph >}}

## Package context

Package basic provides the two text widgets: Text, which writes styled spans on one line, and Paragraph, which wraps them.

Both follow the same two rules, which are the rules every widget in the catalog follows:

- The available space is Bounds(), never buf.Size(). The buffer is the screen; the rect is the widget's space (ADR 0007 §1 rule 1).
- Nothing derived from the size is built in Draw. Wrap and Truncate both allocate, so Paragraph caches its Wrapped and Text caches its truncation against the rect they were computed for, and recompute only when Bounds() differs (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
basic.NewParagraph(r buffer.Rect, spans []buffer.Span) *basic.Paragraph
```

Same shape as [`Text`](/widgets/text/): spans in, wrapping out. The wrapping is `buffer.Wrap`'s work, not the widget's, and it allocates — which is why it happens on the first `Draw` after a width change rather than every frame.

- `Spans` — `[]buffer.Span` — the styled content, wrapped to the width it is given.
- `Align` — `geometry.Align` — applied per line.
- `Ascii` — `bool` — force ASCII wrapping rules.

## When not to use it

**Do not use it for text the user must scroll.** A `Paragraph` shows the **top** of its content and stops; it has no scroll position and no key contract, so a paragraph longer than its rect silently loses the rest. Scrolling a body of text is [`Pager`](/widgets/pager/), deliberately.

**Do not use it for a single line.** [`Text`](/widgets/text/) is the smaller widget and does not pay for the wrap cache. `Paragraph` on a one-line string works but buys nothing.

**Do not use it to lay out a form or anything with per-element state.** It wraps prose, not widgets. A field label next to an input is two widgets in a solved rect, which is a layout problem — see [Composing with Block and Split](/guides/composing/).

**Do not expect it to keep its wrapped cache across a resize for free.** A width change re-wraps, and `Wrap` allocates. That is correct and it is once per width change, but it does mean a drag-resize re-wraps on every step.

**Instead:** [`Pager`](/widgets/pager/) to scroll it, [`Text`](/widgets/text/) for one line, [composition](/guides/composing/) for anything with state.

## Related

- [`Pager`](/widgets/pager/) — the scrollable counterpart.
- [`Text`](/widgets/text/) — the one-line form of this widget.
- [Styling and spans](/concepts/styling/) — the rule that a wide glyph's continuation cell takes its span's style.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/basic` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/basic)
