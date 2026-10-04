---
title: "Split"
weight: 4
description: "A container that divides its rectangle among focusable panes."
widgetName: "Split"
widgetPackage: "widgets/split"
widgetConstructor: "split.New(d layout.Direction, panes ...termmosaic.Widget) *split.Split"
capture: "split"
---

A container that divides its rectangle among focusable panes.

Package `widgets/split`. API reference: [pkg.go.dev/widgets/split](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/split).

Split arranges panes along one axis.

## Rendered output

{{< widget-capture split >}}

> **About this capture.** Focus moves between panes with Tab and the focused pane is the one that takes keys. A still frame cannot show that; the marker in the second pane's title is where the capture has to stop.

## Package context

Package split provides Split, the pane composer: it solves one layout and hands each pane a rectangle.

It exists because a terminal application that wants two panes needs three things and none of them is interesting: solve a constraint list, hand the results out as rectangles, and let the user move the divider. The first is layout's job and Split calls it rather than reimplementing it — ADR 0004 chose a closed, predictable constraint set precisely so that exactly one solver exists, and a second arithmetic pass inside a widget is how two solvers start to disagree about overflow.

A widget receives its rectangle through Bounds, and nothing in the framework hands it one: there is no Resize method to push down the tree (ADR 0007 rejects it), so a container must be able to SET bounds. Hence Bounded, which a pane implements by having a SetBounds method — block.Block, basic.Text and basic.Paragraph all do. A pane that does not implement it is still drawn, with whatever rectangle the application gave it; Split never invents one.

## Constructing it

```go
split.New(d layout.Direction, panes ...termmosaic.Widget) *split.Split
```

`Split` solves one constraint list and hands each pane a rectangle. It is the only widget that introduces an interface of its own — `Bounded` — for a pane that wants to say what it needs.

- `Direction` — `layout.Direction` — `DirectionRow` or `DirectionColumn`. One axis only; nesting a `Split` inside a `Split` is how you get a grid.
- `Spacing` — `int` — cells between panes, removed from the pane rects rather than overlapped.
- `Background` — `buffer.Style` — the gap colour. Visible wherever `Spacing` is non-zero.

## When not to use it

**Do not use it for a grid.** `Split` arranges panes along **one** axis. Two or three panes is the shape it solves; a grid is a `Split` inside a `Split`, and if you find yourself writing that, the constraint list is doing more work than the pane model is.

**Do not use it as a border.** It draws no frame. Each pane that needs one composes a [`Block`](/widgets/block/); `Split` will not do it for you, and it deliberately does not know about `Block`.

**Do not use it to get equal panes for free.** `Split` calls the `layout` solver, and `layout.Fill` is **order-insensitive** — a deliberate divergence from tmux, pinned by a test. If you want fixed ratios, say so with `layout.Ratio` or `layout.Percentage`; do not rely on declaration order to break a tie.

**Do not use it when one pane should be able to vanish.** Panes are given at construction as a variadic. Hiding a pane means rebuilding the `Split`, which loses the pane's state unless the application holds it — which is a fine design, but it is the application's job, not the framework's.

**Do not expect it to solve a focus problem you have not described.** Tab moves between focusable panes and the focused pane is the one that takes keys. That is the whole focus behaviour; a `Split` does not know which of your panes is a form and will not validate it.

**Instead:** [`layout.Solve`](/concepts/layout/) directly for a fixed arrangement, [Composition](/guides/composing/) for the patterns that come up.

## Related

- [Layout and constraints](/concepts/layout/) — the solver `Split` delegates to, including why `Fill` is order-insensitive.
- [`Block`](/widgets/block/) — the border each pane composes for itself.
- [Widgets and focus](/concepts/widgets-and-focus/) — what `Focusable` means and who maintains focus order.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/split` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/split)
