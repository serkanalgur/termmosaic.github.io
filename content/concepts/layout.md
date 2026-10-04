---
title: "Layout and constraints"
description: "Length, Min, Max, Percentage, Ratio, Fill, Solve — and why Fill is order-insensitive."
weight: 23
toc: true
---

# Layout and constraints

A constraint solver of TermMosaic's own, in the `layout` package. The reasoning
is [ADR 0004](/adr/0004-layout-engine/).

## Why not flexbox

**Yoga was rejected because cgo breaks `CGO_ENABLED=0` cross-compilation**, and
that contradicts the single-static-binary goal the whole project rests on. That
is the whole reason; there is no performance argument and there is not one about
API taste either. The constraint vocabulary TermMosaic ended up with is
deliberately the one Bubble Tea users already know, so that vocabulary is not a
migration cost.

## The vocabulary

Six constraints, all of them pure arithmetic against the space available:

| Constraint | Means |
|---|---|
| `layout.Length(n)` | exactly `n` cells |
| `layout.Min(n)` | at least `n` cells |
| `layout.Max(n)` | at most `n` cells |
| `layout.Percentage(p)` | `p`% of what is available |
| `layout.Ratio(n, d)` | `n/d` of what is available |
| `layout.Fill(w)` | share what is left, in proportion to `w` |

Two axes, `layout.Horizontal` and `layout.Vertical`, and a spacing value applied
between the resolved children.

```go
// n cells if they fit, and whatever is left over shared evenly either side if
// they do not.
[]layout.Constraint{layout.Fill(1), layout.Max(n), layout.Fill(1)}
```

That single line is the centring-and-clamping idiom, and it is the
documented replacement for hand-rolled `centred(sw, sh, 46, 9)` arithmetic. `Max`
is bounded by the space it is measured against, so **the result cannot overflow
the screen** — which is what makes `ADR 0007 §1 rule 2` ("clip, never blank")
unnecessary for `Max`-bounded layouts.

## `Fill` is order-insensitive

**This is a deliberate divergence from tmux, and it is pinned by a test.**

tmux resolves `Fill` in priority order: the first one declared gets the leftover
space and later ones get nothing. TermMosaic's solver resolves **all fixed
constraints first**, then distributes whatever is left among the `Fill`s by
weight. So this:

```go
layout.Solve(layout.Horizontal, cs, spacing, available)
```

gives the same answer whatever order `cs` is in. ADR 0004 originally recorded
order-sensitivity as the design's top usability sharp edge; the committed solver
does not have it, and the ADR now documents the divergence rather than the
problem.

**One visible consequence**, recorded so nobody reads it as a bug: leftover space
is distributed by **largest remainder**, which is deterministic and hands a
leftover cell to the **earliest-declared** `Fill`. So when the slack above and
below a centred panel is odd, the panel sits one row **lower** than dead centre.
On a 14-row screen that is three rows above and two below. That is why the
`examples/hello` golden files changed when the clamp-and-centre pattern was
replaced with two `Solve` calls.

## Overflow and underflow are both defined

Neither panics, and both are covered by tests. This is worth stating because
"the solver shrinks my pane to fit" is the behaviour that hides bugs.

- **Overflow**: the fixed constraints exceed the available space. `Fill`
  constraints receive **0**, the fixed constraints keep their sizes, and **the
  resulting sizes sum to MORE than the available space.** `Solve` does not clip.
  **The caller decides whether to clip**, because silently shrinking a pane
  would hide a layout bug the author needs to see.
- **Underflow**: space is left over and there is no `Fill` to take it. **The
  leftover is simply not assigned.** `Solve` does not distribute it, because
  every rule for doing so would be a surprise to someone.
- A **negative** available size is treated as **zero**.

So a layout built from `Length` constraints alone can overflow, and the clip rule
in ADR 0007 §1 is not optional — it is the documented response to `Solve`'s
documented behaviour. `render`'s `TestRootBoundsClippedToScreen` pins it.

## Composition is just `Solve` on a sub-rectangle

There is no nesting engine. Nesting is running `Solve` on a sub-rectangle, which
is why `layout.Rect` exists:

```go
xs := layout.Solve(layout.Horizontal, cs, spacing, r.W)
child := layout.Rect(r, layout.Horizontal, xs, spacing, i)
```

`Solve` returns the **size** of each constraint. `layout.Offset(sizes, spacing, i)`
turns that into a **position**, and `layout.Rect` does both.

One property of `Offset` that matters: **sizes that overflow the axis are still
positioned, so the overflow stays visible instead of being clipped away.** That
is deliberate — it is the overflow rule above, expressed in the position
calculation.

[`Split`](/widgets/split/) is the one widget that uses this for you, and it
delegates to `Solve` rather than reimplementing it.

## `Solve` is not on the frame path

**`Solve` allocates** — it returns a newly allocated slice. It is called when the
tree changes, not every frame, and ADR 0003's dirty-rectangle model is what makes
that affordable. If you are solving a layout inside `Draw`, you have a bug: either
cache the result against the rect, or solve it when the size changes.

This is the same constraint as `buffer.Wrap` and `buffer.Truncate` being banned
from `Draw` — see [Styling and spans](/concepts/styling/).

## Reading next

- [Responsiveness](/concepts/responsiveness/) — `MinSize`, and what to do when
  the solved layout is below it.
- [Composing with Block](/guides/composing/) — borders, padding and solving
  against `Block.Interior()`.
- [`Split`](/widgets/split/) — the pane composer.
- [ADR 0004](/adr/0004-layout-engine/) — verbatim, including the rejected
  alternatives.