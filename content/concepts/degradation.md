---
title: "Degradation and NO_COLOR"
description: "Truecolor to 256 to 16, the Lab/CIEDE2000 quantiser decided on measurement, NO_COLOR as an encode-time concern, and the ASCII fallback."
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

## The quantiser selects in Lab space (CIEDE2000)

**The 256 and 16 colour rungs select their nearest palette entry with an
exhaustive CIEDE2000 search in Lab space, behind a per-colour memo.** This is
**DECIDED** in the project's decision table — moved from PROPOSED on
measurement, 2026-10-06, at v1.0.0. Selection error is **0.000 on both rungs**,
and every threshold in the audit is pinned at 0, so a non-zero measurement
means the metric, the palettes or the wiring changed without a re-audit.

How it got there, because the history is the argument:

- Through v0.7.0 the rungs used a **"redmean"** mapping — a weighted RGB
  distance with weights that adapt to the mean red of the two colours. It was
  implemented, it worked, and **nobody had checked that its output was
  perceptually acceptable.** The project's own docs said so: treat the rungs as
  provisional, the colour model was PROPOSED, and `buffer.Quantiser` existed as
  the escape hatch for a Lab-space replacement.
- The check was then performed (PR #18, a CIEDE2000 audit) and it **failed**.
  The "redmean" weights were inert: `rmean/256` and `(255-rmean)/256` divide to
  zero in `uint8` arithmetic, so both weights were identically 2 and the
  formula was in practice the fixed `2*dr²+4*dg²+2*db²` in gamma-space RGB —
  a distance that flips the hue of plausible UI colours. Measured selection
  error: **256 rung max 21.201, 19.35% of the lattice above the just-noticeable
  difference; 16 rung max 36.821, 37.50% above**, with `markets.down`
  collapsing to grey at the 16 rung and colliding with `markets.flat`.
- The quantiser was then **replaced** (PR #19) through the
  `buffer.Quantiser` hook — the seam the docs had pointed at all along — so
  the diff and the encoder are untouched. After: selection error **0.000 on
  both rungs, 0 of 281,216 colour-rungs regressed**, frame path 224.8 → 6.6
  ns/op at 0 allocs. Only the first use of a colour pays for the exhaustive
  search; steady state is a memo lookup.

**This is a behaviour change at v1.0.0**: the bytes a program emits at the 256
and 16 rungs differ from v0.7.x. Visible in `examples/markets`, where
`markets.down` is red again rather than collapsing to grey.

**What is still true of the ladder:** a terminal in 256-colour mode, or a user
who cannot distinguish two colours, sees a *mapped* palette — the rungs are
perceptually nearest, not identical. That is what a quantiser is.

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