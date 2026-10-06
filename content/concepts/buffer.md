---
title: "Buffers and cells"
description: "The 16-byte Cell, Buffer, SubBuffer, Row(y) and why Cells() was removed."
weight: 22
toc: true
---

# Buffers and cells

The cell is the atom of the whole framework: the renderer's diff, the layout
solver's output unit, and every widget's drawing surface. Two ADRs own this page
— [ADR 0002](/adr/0002-buffer-representation/) for the representation and
[ADR 0006](/adr/0006-subbuffer-cell-access/) for how you are allowed to read it.

## `Cell` is exactly 16 bytes

```go
type Cell struct {
    Ch    rune
    FG    Colour
    BG    Colour
    Attr  Attr
    flags uint8
}
```

**Padding-free, and a test asserts it** with `unsafe.Sizeof`. It is not an
optimisation detail — it is a precondition of the byte-wise row comparison in the
diff, which is where the ~141× reduction comes from. A padding byte would double
the memory traffic of tier 1 for nothing.

### The wide-glyph rule

A double-width glyph occupies **two cells**. The continuation cell must:

1. compare **equal** across frames, or the row flickers forever, and
2. take the style of its **owning span**, not its own.

Both are load-bearing and both are easy to get wrong. ADR 0008's amendment
benchmarked these paths for the first time in v0.1.0: on a 200×60 scene a full
repaint costs 74,139 ns/op against the ASCII scene's 74,078, and the row-skip
tier is indistinguishable. All paths are 0 allocs/op. **The wide paths did not
regress.**

What is *not* done: the cell-width table is hand-written from East Asian Width
ranges rather than generated from Unicode data, and **grapheme clusters are not
composed** — a flag emoji renders as two cells' worth of junk. See
[Limitations](/limitations/#text-and-internationalization).

## AoS, and why it overturned the leaning

ADR 0002 **overturned a prior leaning toward struct-of-arrays.** The finding is
the interesting part, because it contradicts an assumption that came from
another language:

> **OpenTUI's SoA row-skip advantage is a Zig `mem.eql` advantage and does not
> transfer to Go.**

Measured:

| Workload | Packed AoS | SoA |
|---|---|---|
| Row skip, mostly-clean rows | 5,373 ns/op | 5,128 ns/op |
| Row skip, **every** row dirty | **147.2 ns/op** | 636.7 ns/op |

AoS **ties** where SoA was supposed to win, and is **4.4× faster** when every
row is dirty — because comparing a row is *one wide `memcmp`* rather than four.
The dirty-heavy case is the one a TUI actually hits: a dashboard's data region
changes while its chrome does not, and every row of the data region is dirty.

## The byte-count figure, corrected

ADR 0002 originally recorded a byte count of "107 bytes". That number was an
artefact of a single-byte-glyph benchmark scene. **The claim is the ratio
(~141×), not the absolute number**, and the ADR now says so.

## `Row(y) []Cell`, and why `Cells()` is gone

**ADR 0006 removed `Buffer.Cells()`.** It returned the flat backing slice, whose
index `y*Width()+x` is **silently wrong for a sub-buffer** — and that is the same
unsoundness ADR 0002 had already fixed once, in `SubBuffer`, left open at a
different door. A method that is wrong only for views is the hardest kind of API
to use correctly, because the tests that pass on a top-level buffer give you no
warning.

The replacements:

```go
func (b *Buffer) Row(y int) []Cell   // correct on top-level buffers and views alike
func (b *Buffer) RowBytes(y, x0, n int) []byte  // panics on a view
```

**`Row` is correct everywhere because the stride never leaves the `buffer`
package.** It cannot be wrong for a view, because the view does not know the
stride.

**`RowBytes` is a `*Buffer` method and panics on a sub-buffer.** That is
deliberate: ADR 0002's v1.0 risk item 1b asked whether to make this
structurally refuse non-top-level buffers by moving it behind a pointer receiver,
and the answer was yes. `diff.Frame` now carries `*buffer.Buffer` instead of
`[]buffer.Cell`, so **"the diff only takes top-level buffers" is enforced by a
type rather than by a doc comment.**

`Stride()` is deliberately **not** exported. There is no reason for a caller to
know it, and every reason not to.

## The two preconditions for byte-wise comparison

ADR 0002's 2026-10-04 amendment states them as two, not one:

1. **`Cell` is padding-free**, and
2. **the compared range is contiguous.**

The second is a property of the **call site**, not of `Cell`. The original ADR
only stated the first, which is why the `SubBuffer` case survived a careful
review. `Buffer.stride` is the structural fix.

## Writing into a buffer

Widgets write through range-clipped writers so they can draw text that ends
before the screen's edge without pre-truncating (which allocates) or re-deriving
the wide-glyph rules (which is how two widget packages each grew their own
forty-line copy):

- `SetSpansIn` — styled spans, clipped to a rect
- `SetStringIn` — plain text, clipped to a rect
- `SetSpansCappedIn` — capped, for a value that must fit
- `SetSpansWindowIn` — a window onto a wider logical row, for horizontal
  scrolling

`SetSpansWindowIn` has a `skip` parameter that ADR 0006's risk list recorded as
unreachable. **It is reachable**, via `clampColOffset`'s ceiling rather than via
`scrollCols`: `Table` keeps a column index *and* a cell position, the cell
position is only set to a column start when a caller asks for one, and the ceiling
is `totalW - contentW` — the content's right-hand edge, generally not a column
start. So scrolling to the end leaves the column before it partially visible, and
any resize that changes `contentW` or `totalW` re-clamps onto it. `Table`'s
behaviour is unchanged; the comment claiming `skip` was dead code was wrong and
has been corrected. [`table_window_test.go`](https://github.com/serkanalgur/termmosaic/blob/main/widgets/data/table_window_test.go)
proves it.

## Colours

A `Colour` is truecolor, a named 16, or a 256-index, plus a `ColourDepth` rung
and a default. `Colour.Hex()` renders it.

**The quantiser selects in Lab space (CIEDE2000), decided on measurement at
v1.0.0.** Truecolor maps down to the 256 and 16 rungs through an exhaustive
CIEDE2000 search behind a per-colour memo, via the `buffer.Quantiser` hook;
selection error is 0.000 on both rungs. This replaced a "redmean" mapping whose
weights were inert (`uint8` division made both identically 2) — the audit that
found it and the numbers that rejected it are kept in the framework's test
source rather than erased. This is a **behaviour change at v1.0.0**: the bytes
emitted at those rungs differ from v0.7.x. See
[Degradation and NO_COLOR](/concepts/degradation/).

## Reading next

- [Renderer and diff](/concepts/renderer/) — where the byte-wise comparison is
  used, and the measurement.
- [Styling and spans](/concepts/styling/) — `Span`, and the wide-glyph rule.
- [Headless testing](/concepts/headless-testing/) — `MemorySink.Cells()` is how a
  widget test asserts on any of this.
- [ADR 0002](/adr/0002-buffer-representation/) and
  [ADR 0006](/adr/0006-subbuffer-cell-access/) — verbatim.