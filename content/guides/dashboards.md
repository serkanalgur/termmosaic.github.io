---
title: "Dashboards"
description: "Building the examples/dashboard screen — nine widgets, one constraint solve, a focus order, and a clock."
weight: 54
toc: true
---

# Dashboards

A widget catalog is evaluated by what an application can **build** with it, not
by what each widget does alone. So this page walks through
`examples/dashboard`, which is a real screen — a service dashboard — composed
from nine widgets.

```
go run github.com/serkanalgur/termmosaic/examples/dashboard@v0.1.0
```

The full file is
[`examples/dashboard/main.go`](https://github.com/serkanalgur/termmosaic/blob/main/examples/dashboard/main.go),
749 lines. This page is the shape of it.

## What is on the screen

- a **`List`** of 100,000 synthetic requests — the case a virtualized widget
  exists for, and the reason its per-frame cost does not depend on the count
- a **`Table`** of columns wider than the viewport — which is what makes the
  horizontal scrolling and the per-column width modes visible
- a **`Tree`** of services with expandable children
- a **`Pager`** over a 4,000-line log, wrapped to width and searchable
- and all five viz widgets: a determinate **`ProgressBar`**, a Braille
  **`Gauge`**, a zoned **`Meter`**, a Braille **`Sparkline`** and a
  **`BarChart`**

**Nine widgets from the catalog, and the application spells no border rune and
invents no title threshold** — the chrome belongs to `widgets/block`, per
[ADR 0008 §2](/adr/0008-style-and-text/).

## One constraint solve, once per resize

The layout is **two `layout.Solve` calls**, not arithmetic divided by hand:

```go
func (d *dashboard) layoutWidgets() {
    r := d.bounds
    if r.Empty() {
        return
    }
    rows := split(layout.Vertical, rowWeights, 0, r.H)
    head := layout.Rect(r, layout.Vertical, rows, 0, 0)
    body := layout.Rect(r, layout.Vertical, rows, 0, 1)
    foot := layout.Rect(r, layout.Vertical, rows, 0, 2)

    cols := split(layout.Horizontal, colWeights, 1, body.W)
    left := layout.Rect(body, layout.Horizontal, cols, 1, 0)
    mid := layout.Rect(body, layout.Horizontal, cols, 1, 1)
    right := layout.Rect(body, layout.Horizontal, cols, 1, 2)
    // ... sub-rectangles of left, mid and right ...
}
```

Two decisions worth copying:

- **`layout.Solve` rather than hand arithmetic**, because
  [ADR 0004](/adr/0004-layout-engine/) chose a closed constraint set precisely
  so that **exactly one solver exists**. A second arithmetic pass inside an
  application is how two solvers start to disagree about overflow.
- **The remainder goes to the last cell of each axis**, so the widgets fill the
  screen exactly. That is a consequence of the largest-remainder rule, not an
  extra pass — see [Layout and constraints](/concepts/layout/).

`split` is a small helper that turns a weight list into a constraint list, which
is the only piece of glue the example needs:

```go
func split(d layout.Direction, weights []int, spacing, available int) []int {
    cs := make([]layout.Constraint, len(weights))
    for i, w := range weights {
        if w > 0 {
            cs[i] = layout.Fill(w)
        } else {
            cs[i] = layout.Length(0)
        }
    }
    return layout.Solve(d, cs, spacing, available)
}
```

The zero-weight case is `Length(0)`, not `Fill(0)` — a zero-weight `Fill` is a
weightless share, and expressing "no space here" as a fixed zero is clearer than
as a share of nothing.

Two more helpers in the same file are worth stealing, because they are the
arithmetic people write by hand and then get wrong:

```go
// below returns the remainder of r under the first frac of its height, so a pair
// of stacked panes tiles exactly with no gap and no overlap — which is what a
// caller would otherwise get wrong by subtracting the wrong thing.
func below(r buffer.Rect, frac float64) buffer.Rect

// areaOf returns the first n hundredths of r vertically, which is how a pane gets
// "the top half" without a second solver.
func areaOf(r buffer.Rect, frac float64) buffer.Rect
```

Both clamp the fraction into `[0, 1]`, which is the degenerate-size discipline
applied to your own arithmetic rather than to a widget.

**This is not on the frame path.** `layoutWidgets` runs at startup and on resize.
`layout.Solve` allocates — it returns a newly allocated slice — so calling it
inside `Draw` would add an allocation per frame, which is exactly what
[ADR 0008 §4](/adr/0008-style-and-text/) forbids.

## Focus: a slice, and an index

```go
d.focusable = []termmosaic.Focusable{d.list, d.table, d.tree, d.pager}
```

Four entries, and the key handling is deliberately thin:

> **Tab moves focus between the focusable widgets because none of them consumes
> it, and `/` begins a search the `Pager`'s read-only API accepts rather than
> typing into it.**

That is the composition contract in miniature: **widgets own their keys, the
application owns the routing.** Note what that implies — the search query goes
*into* the `Pager` through its API, because `Pager` cannot be typed into. The
read-only design forced a routing decision rather than being an inconvenience.

## A clock, and the invalidation discipline

The dashboard shows live values, so something has to change them:

```go
func (d *dashboard) Tick() {
    // ... update the series, move the values ...
    d.Invalidate()
}
```

**`Tick` mutates fields and invalidates. `Draw` only reads.** That is the rule
from [Responsiveness](/concepts/responsiveness/): any setter that writes a field
`Draw` reads must invalidate, or the screen shows stale data with nothing
anywhere saying why.

The dashboard does **not** have a heartbeat goroutine calling `InvalidateAll`
every frame the way `examples/hello` does. `hello` needs one because a frame
counter has to keep ticking; a dashboard is invalidated by the data it is
displaying, which is both cheaper and the pattern a real application should use.

## The viz widgets

```go
d.meter.SetZones([]viz.Zone{
    {Name: "ok",   From: 0,  To: 60, Style: stTrack, FillStyle: stAccent},
    {Name: "warn", From: 60, To: 85, Style: stTrack, FillStyle: stWarn},
    {Name: "crit", From: 85,          Style: stTrack, FillStyle: stCrit},
})
d.meter.Threshold = 85
```

Three zones and a threshold, and the zones are **named** — which is the point.
`Meter` carries three non-colour signals: zone boundaries are `+`, the threshold
is `|`, and the active band is named **in text**.

{{< widget-capture "meter" >}}

{{< widget-capture "gauge" >}}

{{< widget-capture "sparkline" >}}

{{< widget-capture "progressbar" >}}

{{< widget-capture "barchart" >}}

### Read those two captures carefully

**`Gauge` and `Sparkline` are Braille.** In a web font those glyphs can take a
different advance width than a terminal gives them, and that destroys the
alignment the whole widget depends on. **That is why every widget page on this
site shows the exact plain-text capture beside the colour one.** The text is the
truth; the colour is the persuasion.

And neither of these can show you the dial *moving* or the series *growing*, which
is the other thing a still frame cannot do.

## The palette, and monochrome

The example keeps its palette to **five colours, so that what remains on screen
in monochrome is still readable**:

> Every widget here carries a non-colour signal too, **which is the accessibility
> requirement, not a bonus.**

That is a design constraint on the example, not an accident of it. If you build a
dashboard whose distinctions are only hues, it is unreadable on a monochrome
terminal and to a colour-blind reader — see
[Accessibility](/concepts/accessibility/).

## What this screen does not show

- **Interaction, resize or animation.** It is a program, so it does — but a
  *capture* of it would not. Every picture on this page is a settled frame.
- **Performance under your data.** The flat-cost numbers in
  [Virtualization](/concepts/virtualization/) are the catalog's own benchmarks on
  the catalog's own scenes.
- **A resize against a real terminal.** See
  [Limitations](/limitations/#layout-and-responsiveness).

## Building your own

The order that works:

1. **Solve the layout first**, against `Block.Interior()` — see
   [Composing with Block](/guides/composing/). Get one constraint list per axis and
   `layout.Rect` for each child.
2. **Decide the focus order**, as a slice. It is a list, not a tree walk, and it
   makes "Tab moves here" a statement.
3. **Wire invalidation to the data**, not to a timer. A ticker-driven
   `InvalidateAll` is a placeholder for not having done this step.
4. **Check the monochrome case.** `NO_COLOR=1 go run ./examples/dashboard`. If
   anything becomes unreadable, add a non-colour signal.
5. **Test it headlessly** — see
   [Headless testing](/concepts/headless-testing/). A dashboard is exactly the
   kind of screen that should have a golden file, because a layout regression
   shows up as a diff in a string rather than as an exception.

## Reading next

- [Data display](/guides/data-display/) — choosing the data widgets.
- [Composing with Block](/guides/composing/) — the chrome and the layout.
- [Performance](/guides/performance/) — what is measured and what is not.