---
title: "Performance"
description: "Every measured number on this site, and an explicit list of what is not measured."
weight: 55
toc: true
---

# Performance

**This page contains every performance claim on this site, and a list of what is
not measured.** That second list is the point. A docs page that lists six
benchmarks and no caveats is a page you should distrust on the other five things
it says.

All figures come from the framework's own benchmarks and `docs/STATUS.md` at
v0.1.0, measured on **darwin/arm64 (Apple M1)**. They were taken by decisions 1
and 2, which were made **empirically** — a scratch benchmark module built outside
the repository.

## Measured: the renderer

On a **200×60 scene that is 99% static chrome**:

| | |
|---|---|
| Diff output | **141 bytes** |
| Full repaint | **19,979 bytes** |
| Reduction | **~141×** |
| Cost | **~7,133 ns/op** |
| Allocations | **0 allocs/op** |

**The claim is the ratio, not the absolute number.** ADR 0002 originally recorded
a byte count of "107 bytes"; that figure was an artefact of a single-byte-glyph
benchmark scene, and the 2026-10-04 amendment corrected it to state the ratio.

**A frame in which nothing is dirty writes zero bytes and does not call the sink
at all** — so an idle application costs nothing rather than burning CPU at the
frame rate.

## Measured: buffer representation

The comparison that **overturned** a prior leaning toward struct-of-arrays:

| Workload | Packed AoS | SoA |
|---|---|---|
| Row skip, mostly-clean rows | 5,373 ns/op | 5,128 ns/op |
| Row skip, **every** row dirty | **147.2 ns/op** | 636.7 ns/op |

**OpenTUI's SoA advantage is a Zig `mem.eql` advantage and does not transfer to
Go.** AoS ties where SoA was supposed to win and is 4.4× faster when every row is
dirty, because comparing a row is one wide `memcmp` rather than four.

The dirty-heavy case is the one a TUI actually hits: a dashboard's data region
changes while its chrome does not.

## Measured: versus `tcell`

| | |
|---|---|
| `tcell` flush, one-row-dirty workload | **280,814 ns/op** |
| TermMosaic two-tier diff, same workload | **7,133 ns/op** |

This, plus the fact that `tcell`'s headless backend cannot expose the cell buffer
that widget tests need, is what settled
[ADR 0001](/adr/0001-backend-strategy/).

## Measured: the catalog's flat cost

| Items | `List` | `Table` |
|---|---|---|
| 10,000 | 13,320 ns | 16,801 ns |
| 100,000 | 14,242 ns | 17,885 ns |

**Ten times the data for seven percent more time, both at zero allocations.**

## Measured: wide glyphs

Benchmarked for the first time in v0.1.0, on a 200×60 scene:

| Scene | Full repaint |
|---|---|
| ASCII | 74,078 ns/op |
| Wide glyphs | 74,139 ns/op |

The row-skip tier is indistinguishable, and all paths are 0 allocs/op. **The wide
paths did not regress.**

## Specified-and-tested, not measured

These are properties a test pins. They are real, and they are **not**
benchmarks — ADR 0005 and ADR 0008 are explicit about the difference.

| Property | Why it is not a benchmark |
|---|---|
| **0 allocs per frame** on the frame path | Asserted rather than benchmarked. The allocator's behaviour under a real workload is not what the assertion is about; the assertion is that no code path allocates. |
| **0 allocs on the key path** | ADR 0005 says input decoding is **I/O-bound** — a benchmark would measure the operating system. The number that matters is specified and pinned by a test. |
| **`Draw` allocates nothing in steady state** (`TextInput`) | Same reasoning. The visible runs are rebuilt only when the text, caret, styles or rect change — a structural property, not a timing one. |
| **The degenerate-size contract** | A contract, not a cost: no panic, clip never blank, 0×0 writes zero bytes. |

## Derived, not observed

> **No resize has ever been observed against a real terminal being dragged.**

[ADR 0007](/adr/0007-responsive-screens/)'s drag-resize costs are **derived from
existing code and from ADR 0002/0003's measurements.** The ADR says so itself, in
those terms, and this site does not paper over it.

What *does* exist for resize is scripted: the degenerate-size sweep in
`render/responsive_contract_test.go`, and `examples/hello`'s `TestResizeGolden`
walking grow → shrink → degenerate → recover with a golden file per step. **That
is the scripted resize sweep ADR 0007 risk 6 asks for, and it is not the same
thing as a human dragging a window.**

Writing those four tests also **found a real defect**: `Renderer.Render` called
`Sink.Flush` even when it wrote zero bytes, breaking ADR 0007 §4's contract.

## Not measured, and listed

Each of these is a gap, not an omission:

- **Per-widget cost for the five viz widgets.** There is no benchmark for
  `Gauge`, `Meter`, `Sparkline`, `BarChart` or `ProgressBar`. `Gauge` and
  `Sparkline` are the Braille ones, so they are the ones where a benchmark would
  be most interesting.
- **Frame pacing under load.** `render.Pacer` has a 30–60 fps budget and no
  benchmark.
- **Mutation cost.** The flat-cost numbers are per-**frame**. Changing an item
  list invalidates; doing that every frame is a different cost, unmeasured.
- **Resize cost against a real terminal.** See above.
- **Memory.** Flat per-frame cost does not mean the data is free to hold, and
  nothing here measures a 100,000-row widget's footprint.
- **The capture tool.** Nothing measures how long `cmd/capture` takes.

## One known defect the benchmark found and v0.1.0 does not fix

**The diff's cursor-run suppression assumes one cell per rune**, so every wide
glyph is preceded by a cursor-position escape:

| Scene | Bytes |
|---|---|
| 6,000 ASCII runes | 6,233 |
| The same 6,000 runes, dense and wide | 68,832 |

**Correct output, about 11× the bytes.** The fix is one line and is specified in
[ADR 0008](/adr/0008-style-and-text/)'s 2026-10-04 amendment. It is not in v0.1.0
because `internal/diff` is the most load-bearing code in the project and ADR
0002's headline numbers are quoted from it.

It is recorded here because a performance page that omits the known regression in
its own hot path is not telling you the truth.

## How to reproduce

```
git clone https://github.com/serkanalgur/termmosaic
cd termmosaic
go test ./... -bench=. -benchmem
```

The relevant benchmarks are in `widgets/data/bench_test.go`,
`internal/diff/`, `buffer/wideglyph_test.go` and `render/wideglyph_bench_test.go`.
Raw benchmark output is quoted inline in
[ADR 0001](/adr/0001-backend-strategy/) and
[ADR 0002](/adr/0002-buffer-representation/), **including the workloads that did
not produce a clean result** — which is the more useful half of a benchmark
record.

Your numbers on your scene will differ. These are the framework's, on an M1, at
v0.1.0.

## Reading next

- [Renderer and diff](/concepts/renderer/) — where the numbers come from.
- [Virtualization](/concepts/virtualization/) — what "flat cost" claims.
- [The ADRs](/adr/) — the full reasoning, verbatim, with the rejected
  alternatives and what could not be measured.