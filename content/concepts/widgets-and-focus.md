---
title: "Widgets and focus"
description: "The four-method Widget contract, what Draw may and may not do, Focusable, and Minimizable."
weight: 29
toc: true
---

# Widgets and focus

The whole widget contract. It is four methods and it has not changed across all
ten architecture decisions — which is the single most stable thing in the
project, and the reason a widget written today still compiles: v1.0.0 freezes
the interface under the stability promise.

## The four methods

```go
type Widget interface {
    // Bounds returns the widget's rectangle in screen cells. It must be safe to
    // call before the widget has ever been drawn.
    Bounds() Rect
    // Draw writes the widget's cells into buf, which is clipped to Bounds.
    // It is called every frame for every widget and is expected to be cheap
    // and idempotent: writing the same state twice must produce the same cells.
    Draw(buf *buffer.Buffer)
    // Invalidate marks Bounds dirty. It must be safe to call from any
    // goroutine, which the buffer's dirty accumulator provides.
    Invalidate()
    // Handle offers the event to the widget and reports whether it consumed it.
    // Events are offered to the focused widget first, then to the tree.
    Handle(Event) bool
}
```

Four methods, and the smallness is the point: **no reconciler, no virtual tree,
no incremental-draw interface, no message algebra.**

## What `Draw` may do

**May:**

- Read its own fields and its `Bounds()`.
- Write cells through `buf`, **clipped to `Bounds()`**.
- Read a cache it filled in a size-change check.
- Be called with any rect, including 0×0.

**May not:**

- **Allocate.** `Draw` is 0 allocs/op on the frame path.
  `buffer.Wrap`, `buffer.Truncate` and `layout.Solve` all allocate and are
  therefore **banned from `Draw`**. Cache against the rect; rebuild on change.
- **Call `buf.Size()` and treat it as its own size.** The buffer is the screen.
  Your space is `Bounds()`.
- **Panic, ever, for any rect.** Including 0×0, 1×1, and anything below
  `MinSize()`.
- **Assume it has been drawn before.** `Bounds()` must be safe before the first
  `Draw`.
- **Depend on frame-to-frame state that is not in its fields.** `Draw` is called
  for every widget every frame; there is no "first frame" you can detect.

## What `Draw` must do

**Repaint its whole `Bounds()` before drawing content into it.** The renderer
diffs and **never clears**, so a widget that skips this leaves stale cells behind
when it shrinks.

The easy way to comply is to compose a [`Block`](/widgets/block/) in its
`Background` and let that fill the rect first. That is what
`widgets/viz` does for all five of its widgets, and it is the reason the
catalog has no second border implementation.

## The two optional interfaces

Both are **optional and discoverable by type assertion**, which is the same
pattern the framework uses throughout: adding one costs no widget anything, and a
widget that does not implement one is fully supported.

### `Focusable`

```go
type Focusable interface {
    Widget
    Focused() bool
    SetFocused(bool)
}
```

**Implementations invalidate themselves.** You do not have to.

`List`, `Table`, `Tree`, `Pager`, `TextInput`, `TextArea`, `Select`, `Checkbox`,
`Radio`, `Toggle`, `Tabs`, `Button` and `Split`'s panes are focusable.
`ProgressBar`, `Gauge`, `Meter`, `Sparkline`, `BarChart`, `Text`, `Paragraph` and
`Block` are not — and that is not an oversight:

> A widget that claimed focus would **swallow the keys its neighbours needed**.

`Gauge`'s godoc says this about charts, and it is the reason the five
visualization widgets are plain `Widget`s. There is nothing about a bar to
select.

### `Minimizable`

```go
type Minimizable interface {
    Widget
    // MinSize returns the widget's smallest meaningful size in cells. It must be
    // pure, must not depend on the current Bounds, and must be safe to call before
    // the widget has ever been drawn.
    MinSize() Size
}
```

**`MinSize()` includes the widget's own chrome**, and it must be **pure**. The
framework does nothing with the value — see
[Responsiveness](/concepts/responsiveness/) for why, and every widget page for
the actual numbers.

## Focus: who decides

**You do. The framework does not.**

> **Events are offered to the focused widget first, then to the tree.**

So the pattern is: an application owns a focus order, calls `SetFocused` on the
old and the new widget, and its own root's `Handle` sees whatever the focused
widget did not consume. A slice of `Focusable` with an index is enough, and it
makes "Tab moves here" a statement rather than an accident.

Two consequences that bite:

- **A widget that consumes `Tab` while focused will trap the user.** That is why
  none of the catalog's widgets do. `List`'s godoc is explicit: *"`KeyTab` is NOT
  consumed, so a form can move focus out of a list with the keyboard exactly as
  it moves out of a text input."*
- **A disabled widget consumes nothing** — not a click, not a key. `Button`
  deliberately does this so a form can disable an action without removing the
  widget from the tree.

## Composition: two widgets that hand out rectangles

Only two widgets give other widgets space, and they are both deliberately thin:

- [`Split`](/widgets/split/) — solves one constraint list and hands each pane a
  rectangle. It delegates to `layout` rather than reimplementing it, and it
  introduces exactly one interface of its own (`Bounded`, for a pane that wants
  to state what it needs).
- [`Block`](/widgets/block/) — owns the border, the title and the background, and
  reports `Interior()`, the rectangle its body draws into. Composing one is how a
  widget stops needing to know that a border and a padding exist.

Everything else either draws itself into the rect it was given or is given a
rect. See [Composing with Block](/guides/composing/).

## Widget values are not concurrency-safe

`Block` is explicit about it: **it is a plain value, not safe for concurrent use,
because `SetBounds` and `Draw` race by design** — the renderer owns `Bounds`
between frames ([ADR 0003](/adr/0003-renderer-mode/)). Keep widgets on one
goroutine, or behind your own lock. `Invalidate()` is the exception: it is safe
from any goroutine.

## Reading next

- [Responsiveness](/concepts/responsiveness/) — `MinSize` and the degenerate-size
  contract.
- [Virtualization](/concepts/virtualization/) — `List`, `Table` and `Tree`.
- [Headless testing](/concepts/headless-testing/) — how to assert on all this
  without a terminal.
- [ADR 0003](/adr/0003-renderer-mode/) — why `Widget` is this small.