---
title: "Concepts"
description: "The twelve ideas TermMosaic is built from, and why each one was decided rather than defaulted into."
weight: 20
toc: true
---

# Concepts

Twelve pages. Each one exists because a decision was made, and the reasoning is
recorded — usually in an ADR, always linked. If you only read three, read
[Renderer and diff](/concepts/renderer/),
[Widgets and focus](/concepts/widgets-and-focus/) and
[Responsiveness](/concepts/responsiveness/): those three explain most of the API
surface you will meet.

## The rendering path

How a cell gets from your `Draw` to the screen, and why each hop exists.

1. **[Renderer and diff](/concepts/renderer/)** — hybrid mode, dirty rectangles,
   the two-tier diff, frame pacing. [ADR 0003](/adr/0003-renderer-mode/)
2. **[Buffers and cells](/concepts/buffer/)** — the 16-byte `Cell`, `Buffer`,
   `SubBuffer`, `Row(y)` and why `Cells()` was removed. [ADR 0002](/adr/0002-buffer-representation/),
   [ADR 0006](/adr/0006-subbuffer-cell-access/)
3. **[Layout and constraints](/concepts/layout/)** — `Length`, `Min`, `Max`,
   `Percentage`, `Ratio`, `Fill`, `Solve`, and why `Fill` is order-insensitive.
   [ADR 0004](/adr/0004-layout-engine/)

## Input and output

4. **[Input](/concepts/input/)** — `Decode`, `Parser`, `Source`, the event model,
   why paste is one event, and what is deliberately out of scope.
   [ADR 0005](/adr/0005-input-decoding/)
5. **[Styling and spans](/concepts/styling/)** — `Style`, `Span`, the wide-glyph
   rule, and the `Draw`-must-not-allocate constraint. [ADR 0008](/adr/0008-style-and-text/)
6. **[No theme, and why](/concepts/no-theme/)** — the decision that shaped the
   whole styling surface. [ADR 0008](/adr/0008-style-and-text/)
7. **[Degradation and NO_COLOR](/concepts/degradation/)** — truecolor → 256 → 16,
   the Lab/CIEDE2000 quantiser decided on measurement, and `NO_COLOR` as an
   encode-time concern.

## Composition and responsiveness

8. **[Responsiveness](/concepts/responsiveness/)** — `ClampCount`, `Budget`,
   `Priority`, `MinSize()`, the degenerate-size contract, and why there are no
   breakpoints. [ADR 0007](/adr/0007-responsive-screens/)
9. **[Virtualization](/concepts/virtualization/)** — the `virtual/` engine behind
   `List`, `Table` and `Tree`, and what "flat cost" actually means.
10. **[Widgets and focus](/concepts/widgets-and-focus/)** — the four-method
    `Widget` contract, `Focusable`, `Minimizable`, and what `Draw` may not do.
    [ADR 0003](/adr/0003-renderer-mode/)

## Quality

11. **[Accessibility](/concepts/accessibility/)** — colour is never the only
    signal, what the catalog provides, and what it cannot provide.
12. **[Headless testing](/concepts/headless-testing/)** — `MemorySink`,
    `widgettest`, golden files, and why a screen reconstructed from an incomplete
    model makes every assertion against it unsound. [ADR 0001](/adr/0001-backend-strategy/)

## Two things worth knowing before you read any of them

**A widget's space is `Bounds()`, never `buf.Size()`.** The buffer is the screen;
the rect is the widget's space. This is rule 1 of
[ADR 0007 §1](/adr/0007-responsive-screens/) and every widget in the catalog
obeys it.

**Nothing size-derived is built inside `Draw`.** `Draw` must be
allocation-free; `buffer.Wrap` and `buffer.Truncate` allocate and are banned
from it, so results are cached against the rect and rebuilt on change. And
`Invalidate()` means *both* "mark dirty" and **"drop everything you have
cached"** — see [Responsiveness](/concepts/responsiveness/) for why that
amendment exists.