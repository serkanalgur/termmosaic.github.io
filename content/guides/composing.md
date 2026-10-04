---
title: "Composing with Block"
description: "Borders, padding and solving a layout against Block.Interior() so content never has to know a border exists."
weight: 51
toc: true
---

# Composing with Block

The composition contract: who owns a border, who owns the padding, and what the
inner widget is told about the space it has.

## The rule

> **`Block` is the only thing in the catalog that draws a border or a title. And
> `Block.Interior()` is the rectangle your body draws into.**

Everything else either composes a `Block` or calls one. No widget in the catalog
contains a glyph table, a corner loop or a title threshold — and that is not a
convention, it is the collision [ADR 0008 §2](/adr/0008-style-and-text/) was
written to prevent.

## The pattern

```go
func (s *screen) Draw(buf *buffer.Buffer) {
    chrome := block.New(s.bounds)
    chrome.SetBorder(buffer.BorderRounded)
    chrome.SetPadding(1)
    chrome.SetTitleString("New project", stTitle)
    chrome.Draw(buf)

    // Solve against the interior, not against s.bounds. This one line is the
    // whole reason Block exists.
    r := chrome.Interior()

    xs := layout.Solve(layout.Horizontal,
        layout.Fill(1),    // the field takes the slack
        layout.Length(12), // the button is fixed
        2,                 // two cells of spacing
        r.W,
    )
    ys := layout.Solve(layout.Vertical,
        layout.Fill(1), layout.Length(1), 1, r.H,
    )

    s.name.SetBounds(layout.Rect(r, layout.Horizontal, xs, 2, 0))
    s.save.SetBounds(layout.Rect(r, layout.Horizontal, xs, 2, 1))
    s.hint.SetBounds(layout.Rect(r, layout.Vertical, ys, 1, 1))

    s.name.Draw(buf)
    s.save.Draw(buf)
    s.hint.Draw(buf)
}
```

Three things this gets right that hand-rolled chrome does not:

1. **`Interior()` knows about the border and the padding, so your layout does
   not.** No `+2` for a border, no `-2` for padding, and no arithmetic that
   breaks when you change `Padding` from 1 to 2.
2. **`Block.Draw` fills the rect in `Background` first**, which satisfies
   [ADR 0007 §1 rule 3](/adr/0007-responsive-screens/) — the repaint-your-rect
   rule — without you writing a fill loop.
3. **The title is truncated with a marker** and cached against the rect, so a
   narrow terminal is told what happened instead of losing the title silently.

## `Block` is chrome only

**A `Block` has no children.** It draws a border, a title and a background, and
that is the whole widget. What goes inside it is the application's business:
compose a widget into the interior, or use [`Split`](/widgets/split/) to place
several.

{{< widget-capture "block" >}}

## Two widgets that hand out rectangles

| Widget | What it owns | What it gives you |
|---|---|---|
| [`Block`](/widgets/block/) | border, title, background, padding | `Interior()` |
| [`Split`](/widgets/split/) | one solved constraint list, pane focus, a draggable divider | each pane's `Bounds()` |

`Split` **delegates** to `layout.Solve` rather than reimplementing it, and it
introduces exactly one interface of its own — `Bounded`, for a pane that wants to
state what it needs.

{{< widget-capture "split" >}}

## Nested composition

Nesting is **running `Solve` on a sub-rectangle**. There is no nesting engine and
no container widget with children, so a grid is a `Split` inside a `Split`:

```go
rows := split.New(layout.DirectionColumn,
    split.New(layout.DirectionRow, leftPane, rightPane),
    statusBar,
)
```

Each `Split` solves its own axis and hands each child a rectangle. If you find
yourself writing a third level of nesting, the constraint list is probably doing
more work than the pane model is.

## The five composition mistakes

**Sizing the inner widget from the outer rect.** `field.W = s.bounds.W - 4` is
hand-rolled knowledge of a border and a padding, and it is wrong the moment you
change either. Use `Interior()`.

**Drawing your own border.** The moment a second one exists you have two
implementations, and `examples/hello` had exactly that bug — its own border runes
with its own `W<4` and `W<16` guards. Composing a `Block` deleted it.

**Forgetting to repaint.** If you do not compose a `Block` in `Background`, your
widget must fill its own rect before drawing into it, or shrinking leaves stale
cells. This is [ADR 0007 §1 rule 3](/adr/0007-responsive-screens/) and it is
silent when you get it wrong.

**Solving against `s.bounds` and then adding padding yourself.** Same mistake as
the first one, in a different place.

**Setting `Block`'s bounds only at construction.** `Draw` must set them every
frame, because the application recomputes them on a resize and a `Block` whose
rectangle were stale would paint chrome in the wrong place. `examples/hello` does
it in `Draw` for that reason.

## Centring a panel

The idiom for "as big as I want, never bigger than the screen, centred":

```go
func centredOnAxis(n int) []layout.Constraint {
    return []layout.Constraint{layout.Fill(1), layout.Max(n), layout.Fill(1)}
}

xs := layout.Solve(layout.Horizontal, centredOnAxis(46), 0, sw)
ys := layout.Solve(layout.Vertical, centredOnAxis(9), 0, sh)
```

`Max` is bounded by the space it is measured against, so **the result cannot
overflow the screen** and needs no clipping afterwards. The two `Fill(1)` are the
centring — leftover space shared equally — and when there is none they get
nothing, which **is** the clamp, expressed rather than hand-written.

This replaces the `centred(sw, sh, 46, 9)` shape that ADR 0007 was written about:
hard-coded size, hand-rolled clamping, and centre-of-screen arithmetic that no
amount of shrinking made correct. At 20×8 the old code produced a block whose
body rows were silently cut off; at 10×4 it lost the title and the body. Nothing
crashed and nothing was useful.

**One consequence, recorded so nobody reads it as a bug:** leftover space is
distributed by largest remainder, which hands a leftover cell to the
**earliest-declared** `Fill`. On odd slack the panel sits one row **lower** than
dead centre.

## Reading next

- [Layout and constraints](/concepts/layout/) — the solver and its overflow rule.
- [Responsiveness](/concepts/responsiveness/) — what to do below `MinSize()`.
- [`Block`](/widgets/block/) and [`Split`](/widgets/split/) — the two widgets
  that hand out rectangles.