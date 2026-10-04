---
title: "No theme, and why"
description: "There is no theme system in v1, on purpose. Here is the trigger that would reverse the decision."
weight: 26
toc: true
---

# No theme, and why

**TermMosaic has no theme system.** Not "not yet" — **by decision**, recorded in
[ADR 0008](/adr/0008-style-and-text/), with a stated trigger that would reverse
it. This page is that decision, because "there is no theme" without the reasoning
reads as an omission, and a reader is entitled to know which it is.

## What you get instead

- **Widgets carry `Style` fields.** Every exported field of type `buffer.Style`
  is yours to set. There is no global style sheet and no key to look anything up
  by.
- **The framework ships no colours.** The defaults are **the terminal's own
  colours** — whatever the user's terminal is configured with — plus **named
  attribute styles** (`AttrReverse`, `AttrBold`, `AttrDim`, and so on).
- **One `Style` value**, twelve bytes, passed by value. See
  [Styling and spans](/concepts/styling/).

That last point is not neutral, and it is the accessibility argument in one line:
**an unset style means the user's terminal colours, not the framework's.** A
framework that shipped a palette would override the user's contrast settings,
their colour scheme, and their dark-mode preference by default. Not shipping one
means the user's terminal keeps them unless the application chooses otherwise.

## The trigger

> **A theme is triggered by the first style *role* that two widgets must share.**

Read that carefully, because the wording is doing real work.

**Not** "when styling gets complicated". **Not** "when there are enough
widgets". **Not** "when an application asks for one".

A *role* is a semantic name for a thing that appears in more than one place: an
"error" colour, a "muted" colour, a "border" style, an "accent". The trigger is
the moment two widgets genuinely have to agree that something means the same
thing.

Before that moment, a theme layer would be **an abstraction over a concept the
catalog does not have** — it would give you a place to put a value that has no
meaning yet, and every widget would still need its own `Style` field because the
role would not line up.

## Why this is a real decision rather than a deferral

The obvious objection is that themes are table stakes and the project is at
v0.1.0 with no users, so the cost of adding one later is low. Two things answer
it.

**One: the collision is already visible and has already been paid for.** Every
widget styles text, and every chrome-bearing widget draws a border. Thirty
widgets each inventing their own idea of "muted" and their own corner glyph is
the failure ADR 0008 was written about — and `examples/hello` had it, with a
second hand-rolled border implementation and its own width thresholds. That class
of bug is real, it happened, and ADR 0008 §2 fixed it with `Block` rather than
with a theme. **A theme does not fix a second border implementation. One owner
does.**

**Two: the alternative designs were considered and rejected**, and they are
worse for this codebase specifically:

| Design | Why not |
|---|---|
| A global mutable style registry | Every widget's rendering would depend on when it was constructed relative to the registry being set. That is the coupling ADR 0003 already rejected, in a different place. |
| Widgets taking a `*Theme` parameter | A fourth mandatory constructor parameter, for a concept that does not exist yet, threaded through 22 constructors — and it would have to be threaded again on every API change, which is exactly what pre-alpha already makes expensive. |
| A style **role** enum, set per widget | This is the shape the decision converges on when the trigger fires. It costs one field per widget and no constructor change, because a role resolves to a `Style` at draw time. |

That third row is the point: **the trigger is reachable without a breaking change
to any constructor.** Deciding now would be premature, and deciding never would
be dishonest.

## What this means for you

**Your application's palette is your business, and it belongs in your code.** The
framework's own example does this at the top of the file:

```go
var (
    bg      = buffer.NewColour(0x10, 0x14, 0x1c)
    fg      = buffer.NewColour(0xd8, 0xdc, 0xe4)
    titleFg = buffer.NewColour(0x30, 0xc0, 0x80)
)

var (
    stBody   = buffer.NewStyle(fg, bg, 0)
    stTitle  = buffer.NewStyle(titleFg, bg, buffer.AttrBold)
    stMuted  = buffer.NewStyle(dim, bg, 0)
)
```

Four colours, built with `buffer.NewStyle` rather than composite literals
because a partial literal silently leaves a channel at opaque black.

**And it means switching palettes is rewriting your own variables**, which at
v0.1.0 is exactly as much work as it sounds. That is a real cost of this decision
and it is the cost of the alternative being worse.

## What is not affected

- **`NO_COLOR` still works.** It is honoured at **encode time**, so no widget path
  consults the environment — see
  [Degradation and NO_COLOR](/concepts/degradation/).
- **Attributes still work.** `AttrReverse` and friends are part of `Style` and are
  not colour, which is why focus and selection survive `NO_COLOR` and a
  monochrome terminal. See [Accessibility](/concepts/accessibility/).
- **Borders still have one owner.** [`Block`](/widgets/block/), with five border
  styles and the glyph tables in `buffer`.

## Reading next

- [Styling and spans](/concepts/styling/) — the `Style` value itself.
- [Accessibility](/concepts/accessibility/) — why "no default colours" is an
  accessibility decision.
- [ADR 0008](/adr/0008-style-and-text/) — verbatim, including the theme
  decision and the rejected alternatives.