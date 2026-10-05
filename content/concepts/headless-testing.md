---
title: "Headless testing"
description: "MemorySink, widgettest, golden files — and why a screen reconstructed from an incomplete model makes every assertion unsound."
weight: 31
toc: true
---

# Headless testing

The reason a widget test can assert on cells without a terminal being involved
at any point. From [ADR 0001](/adr/0001-backend-strategy/).

## The problem it solves

**`tcell`'s headless backend cannot expose the cell buffer.** Widget tests need
it, because a test that asserts on escape sequences is testing the encoder rather
than the widget, and a test that asserts on a rendered string is testing the
model rather than the pixels.

That gap is part of what settled ADR 0001: `tcell`'s flush costs **280,814 ns/op**
on a one-row-dirty workload where TermMosaic's two-tier diff costs
**7,133 ns/op**, *and* its headless backend cannot expose the buffer that widget
tests need. Two independent reasons, both measured or verified by reading the
source.

## `MemorySink`

A `Sink` that maintains **the cell grid the emitted bytes *would have produced**.
So the test drives the real encoder, the real diff, the real renderer — and then
inspects the screen those bytes describe, with no terminal anywhere.

```go
sink := headless.NewMemorySink(80, 24)
// ... render into it ...
cells := sink.Cells()
```

## The rule that makes assertions sound

> **The `MemorySink` screen model refuses to produce a misleading picture: it
> fails the test if the encoder emits a sequence it does not implement.**

This is the important part, and it is worth being explicit about why. If the
encoder emits something the screen model does not implement, the reconstructed
screen is **incomplete** — and:

> **A screen reconstructed from an incomplete model makes every assertion against
> it unsound.**

An incomplete model does not fail loudly by being wrong. It fails *quietly* by
looking plausible. Every assertion written against it is a coin flip that happens
to land on "pass" most of the time, which is worse than a test that does not
exist because it looks like coverage.

So the model is required to be complete, and completeness is checked
mechanically. **This is the whole capture mechanism for this documentation site**
— see below.

## `widgettest`

`widgets/widgettest` exists so that **every widget test renders through `Render`
rather than through `Draw`, and asserts on cells.** That routes each test through
the full stack:

```
widget → buffer → renderer → two-tier diff → ANSI encoder → MemorySink
```

and then asserts on the cells. A test that called `Draw` directly would skip the
diff and the encoder and could not catch a bug in either.

```go
sink, err := widgettest.Render(80, 24, frames, root)
if err != nil {
    t.Fatal(err)
}
// assert on sink.Cells() or sink.String()
```

`Render` takes a `testing.TB`. A documentation generator is not a test, so
`widgettest.Capture` exposes the same path without one — which is what makes the
captures on this site trustworthy rather than illustrative.

## Golden files

`MemorySink.String()` is the exact cell grid, and comparing it against a
checked-in file is a golden test. `examples/hello` has golden files covering both
the rendered screen **and** the exact byte stream at each rung of the colour
ladder — `hello_truecolor.sgr`, `hello_256.sgr`, `hello_16.sgr` and
`hello_nocolor.sgr`.

Two things golden tests are good for here that they are usually not used for:

- **The colour ladder is testable.** The four `.sgr` files pin what
  `render.Config`'s depth and `NoColor` settings actually emit.
- **Resize is testable.** `examples/hello`'s `TestResizeGolden` walks
  grow → shrink → degenerate → recover with a golden file per step. That is the
  scripted resize sweep [ADR 0007](/adr/0007-responsive-screens/) risk 6 asks
  for, and it is not the same thing as a human dragging a window — see
  [Limitations](/limitations/#layout-and-responsiveness).

## Why the captures on this site are trustworthy

The chain is short and there is no step that can flatter the result:

1. `cmd/capture` constructs each widget and calls `widgettest.Capture` — the same
   code path the tests use.
2. That path runs the **whole stack**, and **fails** if the encoder emits a
   sequence the screen model does not implement.
3. `MemorySink.Cells()` returns the flat row-major `Cell` slice, and `Colour.Hex()`
   and `Attr.Has()` render it.

**A capture cannot show something no test pins**, because the capture is a test's
output. That is the claim the whole capture strategy rests on, and it is worth
being clear that it is a claim about *fidelity to the renderer*, not about *fidelity
to a terminal* — which is exactly what [Limitations](/limitations/) says a capture
cannot show.

## Writing a widget test

```go
func TestGaugeShowsItsValue(t *testing.T) {
    g := viz.NewGauge(buffer.Rect{W: 20, H: 10})
    g.Value = 0.75
    g.ShowValue = true

    sink, err := widgettest.Render(20, 10, 2, g)
    if err != nil {
        t.Fatal(err)
    }
    if !strings.Contains(sink.String(), "75") {
        t.Errorf("value not shown:\n%s", sink.String())
    }
}
```

Two frames rather than one: the first `Render` establishes the previous buffer,
and the second is the one that exercises the diff. A test that renders one frame
asserts against a full repaint and tests nothing about the diff.

## What is still open

ADR 0001 makes the headless memory sink a v1 deliverable because the whole
testability pillar depends on it. The remaining open sub-question is its
**assertion surface**: it must expose the cell buffer, not just recorded bytes —
which it now does — but whether that surface is *complete* is still being scoped.

**The cache-poisoning debug mode shipped in v0.5.0**, and it is the strongest
argument on this page for why mechanical checks beat review. A rect-keyed cache is
only half the contract; the audit mode corrupts a widget's cached derivation after
a `Draw` and asserts the next frame is **byte-identical**, and
`widgets/cacheaudit` fails the build on a finding. On its first run it found
**eight** widgets keeping a stale cache after a setter their own documentation
promised would invalidate. Two mechanisms are needed because one provably does not
catch the class: the poison check in `render`, and a cold-twin comparison in
`widgettest`. It is opt-in via `render.Config.CacheAudit` and **zero-allocation
when disabled**, so the frame-path claim survives it.

**What it does not cover** is every exported raw field — the gate audits the
transitions it names, and several same-shaped fields are named by none.

## Reading next

- [Performance](/guides/performance/) — which numbers are measured and which are
  specified-and-tested.
- [Buffers and cells](/concepts/buffer/) — what `Cells()` gives you.
- [ADR 0001](/adr/0001-backend-strategy/) — verbatim, including the benchmark
  output and what could not be measured.