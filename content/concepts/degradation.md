---
title: "Degradation and NO_COLOR"
description: "Truecolor to 256 to 16, the unvalidated quantiser, NO_COLOR as an encode-time concern, and the ASCII fallback."
weight: 32
toc: true
---

# Degradation and NO_COLOR

How TermMosaic meets a terminal that cannot do what it was asked to do, and — as
much — how it refuses to.

## The ladder

Truecolor → 256 → 16, negotiated from the terminal's capabilities and selected by
`render.Config`:

```go
r := render.New(sink, render.Config{
    Width:   w,
    Height:  h,
    Caps:    caps,
    NoColor: render.NoColorFromEnv(os.Getenv),
})
```

A `Colour` is truecolor, a named 16, or a 256-index, plus a `ColourDepth` rung
and a default. `Colour.Hex()` renders it.

There is a second, orthogonal ladder for glyphs: **Unicode → ASCII**. Borders are
`BorderPlain`, `BorderRounded`, `BorderDouble`, `BorderThick` or `BorderASCII`,
and every widget exposes an `Ascii bool` that forces the ASCII set regardless of
what the terminal claims to support.

## NO_COLOR is an encode-time concern

This is the single most important sentence on the page:

> **`NO_COLOR` is honoured at encode time, so no widget path consults the
> environment.**

What that buys:

- **A widget's rendering does not change when the environment does.** No widget
  has an `if noColor` branch, so there is no way for one to get it wrong.
- **The decision is testable.** `render.NoColorFromEnv` is a function, and
  `examples/hello` has `hello_nocolor.sgr` as a golden file — so the behaviour is
  pinned rather than asserted.
- **It composes with attributes.** `NO_COLOR` suppresses **colour**. It does not
  suppress `AttrReverse`, `AttrBold` or `AttrDim`. That is why selection, focus
  and a `Meter`'s threshold marker all survive a `NO_COLOR` terminal — see
  [Accessibility](/concepts/accessibility/).

## The quantiser is unvalidated

**Say this plainly: the redmean mapping from truecolor to the 256- and 16-colour
rungs is implemented and works, and nobody has checked that its output is
perceptually acceptable.**

So:

- **Treat the 256 and 16 rungs as provisional.** The colour model is **PROPOSED**,
  not DECIDED, in the project's decision table.
- **`buffer.Quantiser` is the escape hatch.** It exists so a Lab-space mapping can
  replace the redmean one **without touching anything else** — which is what makes
  replacing it a non-event rather than a rewrite.

This is a real limitation, not a caveat: a colour-blind user, or a user whose
terminal is in 256-colour mode, will get a mapping nobody has looked at.

## `Caps.Unicode` is a proxy, not a probe

It is the honest answer available **without querying the terminal out of band**,
and **a terminal configured out of band will disagree with it.**

The alternative — asking the terminal what it supports, via a query on the
response channel — needs a timeout, needs to not be confused with a keypress,
and breaks when the query is unanswered. The project took the proxy and recorded
what it costs.

## Where else things degrade

**Widget-internal.** Degradation is not only about colour:

- [`Gauge`](/widgets/gauge/) degrades to a **bar** when the rect or the terminal
  cannot hold a Braille dial. It never draws nonsense.
- [`KeyHint`](/widgets/keyhint/) **truncates with a marker** rather than
  reflowing or silently cutting — the trailing `…` is the widget telling you there
  were more keys.
- [`Text`](/widgets/text/) and [`Paragraph`](/widgets/paragraph/) **truncate with
  a marker**, never clip.
- [`Table`](/widgets/table/) and [`List`](/widgets/list/) **truncate or mark** a
  value too wide for its column rather than letting it bleed into the frame.
- [`Block`](/widgets/block/) **truncates an over-long title** with a marker, and
  caches the truncated form against the rect so truncation never happens inside
  `Draw`.

**The pattern is consistent**: a widget that cannot fit something says so, with a
glyph, rather than silently dropping it. The reason is accessibility — a silent
truncation and a marked one are very different to the person reading the screen.

## What a capture shows of this

The widget pages show each widget at 40, 80 and 120 columns, so **the degradation
across widths is visible** rather than asserted. Two examples worth opening:

- [`KeyHint`](/widgets/keyhint/) at 40 columns — the truncation marker.
- [`Paragraph`](/widgets/paragraph/) — the frame is 10 rows at 40 columns, 9 at
  80 and 7 at 120, because wrapping is a function of width. Compare the three.

What the captures **cannot** show is the terminal-side ladder, because that is a
property of the reader's terminal rather than of the cell grid. And they **may
misalign the glyphs** — Braille and Block Elements can take a different advance
width in a web font than in a terminal, which is why every widget page also shows
the exact plain-text capture. See
[Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots).

## Reading next

- [Accessibility](/concepts/accessibility/) — why attributes rather than colour.
- [No theme, and why](/concepts/no-theme/) — why unset styles resolve to the
  terminal's own colours.
- [ADR 0008](/adr/0008-style-and-text/) — style and text, verbatim.
- [Limitations](/limitations/#colour) — the colour gaps, stated as gaps.