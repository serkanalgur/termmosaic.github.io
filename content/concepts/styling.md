---
title: "Styling and spans"
description: "One Style value, one Span type, the wide-glyph rule, and why Wrap and Truncate are banned from Draw."
weight: 25
toc: true
---

# Styling and spans

How a cell gets a colour and an attribute, and the one rule that will bite you.
From [ADR 0008](/adr/0008-style-and-text/).

## One `Style` value

```go
type Style struct {
    FG Colour
    BG Colour
    Attr Attr
}
```

**Twelve bytes, passed by value.** Not a pointer, not an interface. Twelve bytes
is three registers, so passing a `Style` costs exactly what the three loose
arguments it replaced cost — which is what keeps
[ADR 0002](/adr/0002-buffer-representation/)'s 0-allocs frame path intact.
`ansi.Style` is an alias of it.

`Style` lives in `buffer` rather than in `geometry` because of an import cycle:
`buffer` imports `geometry`, and `Style` needs `Colour`. The same
cycle-exclusion reasoning that put [ADR 0007](/adr/0007-responsive-screens/)'s
vocabulary in the leaf.

### The footgun: build styles with `buffer.NewStyle`

A composite literal leaves an unset colour channel at **opaque black**, silently.
`buffer.NewStyle` is the constructor that cannot do that. The framework's own
examples all use it, for this reason.

## One `Span` type

```go
type Span struct {
    Text  string
    Style Style
}
```

Styled text goes through `Span` plus `Buffer.SetSpans`, and the spans are **parsed
once** — at construction, not per frame. That is what keeps `Draw` free of
span-building, and span construction allocates.

Range-clipped writers exist so a widget can draw text that ends before the screen
edge without pre-truncating:

- `SetSpansIn`, `SetStringIn` — clipped to a rect
- `SetSpansCappedIn` — capped, for a value that must fit
- `SetSpansWindowIn` — a window onto a wider logical row, for horizontal scrolling

The last one is why `widgets/data` did not grow its own copy of the wide-glyph
rules: **two widget packages each grew their own forty-line copy before the
writers were factored out.**

## The wide-glyph rule

> **A wide glyph's continuation cell takes its *owning span's* style.**

A double-width glyph occupies two cells. If the continuation cell's style does
not match the cell that owned it, the two never compare equal across frames and
**that row flickers forever.** This is not a rendering nicety; it is the
difference between a stable screen and a permanently shimmering one, and it is
the single most expensive thing to debug in a TUI.

This is also why wide-glyph paths were benchmarked at all in v0.1.0 — see
[Buffers and cells](/concepts/buffer/) for the numbers and for the one defect the
benchmark surfaced and deliberately did not fix.

## `Wrap` and `Truncate` are banned from `Draw`

**They allocate.** `Wrap` allocates twice over: once for the wrapped lines, once
for whatever it builds internally. Calling either from `Draw` adds an allocation
to every frame, which is precisely the failure ADR 0008 §4 exists to prevent.

The pattern:

```go
if r != p.cachedFor {
    p.lines = buffer.Wrap(p.spans, r.W)
    p.cachedFor = r
}
```

`TextArea` does exactly this and it is worth reading, because it is the case
where the temptation is strongest — a multi-line editor that re-wrapped every
frame would be visibly janky on a slow terminal. The first `Draw` after a width
change wraps; every `Draw` after that reads the cache.

**And `Invalidate()` means "drop what you have cached" as well as "mark dirty".**
A widget that caches on `Bounds()` and is handed a new field value renders the
old layout permanently — see [Renderer and diff](/concepts/renderer/) and
[Responsiveness](/concepts/responsiveness/).

## Borders and titles: one vocabulary

Five border styles, with the glyph tables in `buffer`:

`BorderNone` · `BorderPlain` · `BorderRounded` · `BorderDouble` · `BorderThick` ·
`BorderASCII`

**And exactly one widget draws one: [`Block`](/widgets/block/).** List, Table,
Tree, Pager, Tabs and everything else chrome-bearing either compose a `Block` or
call one. None of them contains a glyph table, a corner loop or a title threshold.

That is the collision ADR 0008 §2 was written to prevent: thirty widgets that
each style text and draw a border would produce thirty slightly different
borders. `examples/hello` had this bug itself — it drew its own border with its
own `W<4` and `W<16` guards — and composing a `Block` deleted the second
implementation.

`Block` truncates an over-long title with a marker rather than clipping it, and
the truncated form is cached against the rect, so truncation never happens inside
`Draw`.

## What the framework ships as a default

**No colours.** The defaults are **the terminal's own colours** plus
**named attribute styles** — reverse video, bold, dim and so on. That is why an
unset `Style` on a zero-value widget renders as ordinary terminal text rather
than as black-on-black.

This is the [no theme](/concepts/no-theme/) decision, and the next page explains
why it is the right one.

## Reading next

- [No theme, and why](/concepts/no-theme/) — the decision this page's defaults
  follow from.
- [Accessibility](/concepts/accessibility/) — why the defaults being the
  terminal's own colours is an accessibility decision and not a neutral one.
- [Degradation and NO_COLOR](/concepts/degradation/) — `NO_COLOR` is an
  encode-time concern, so no widget path consults it.
- [ADR 0008](/adr/0008-style-and-text/) — verbatim, with the 2026-10-04
  amendment on wide glyphs.