---
title: "Sparkline"
weight: 21
description: "A series of numbers drawn as Braille or block elements, scaled to its own range."
widgetName: "Sparkline"
widgetPackage: "widgets/viz"
widgetConstructor: "viz.NewSparkline(r buffer.Rect) *viz.Sparkline"
capture: "sparkline"
---

A series of numbers drawn as Braille or block elements, scaled to its own range.

Package `widgets/viz`. API reference: [pkg.go.dev/widgets/viz](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/viz).

Sparkline is a series of values drawn in one row — or one column — with sub-cell resolution.

## Rendered output

{{< widget-capture sparkline >}}

> **About this capture.** Braille encoding, two samples per cell, so the series holds twice the values the width can show. The threshold defaults to reverse video, which is an attribute rather than a colour.

## Package context

Package viz provides the catalog's measurement and display widgets: ProgressBar, Gauge, Meter, Sparkline and BarChart.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- It repaints its whole Bounds() before drawing content (rule 3), by composing widgets/block.Block, whose Draw fills the rect in Background before anything else. No widget here draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Everything derived from the size — which regions survived the budget, where the axis labels go, the glyph ramp for a sparkline — is computed in the size-change check, cached against the rect, and only read in Draw.

## Constructing it

```go
viz.NewSparkline(r buffer.Rect) *viz.Sparkline
```

`NewSparkline` takes a rect; `Values` is the series.

- `Values` — `[]float64` — the series. Braille encodes two samples per cell, so the series holds twice the values the width can show.
- `Braille` — `bool` — on by default. Off gives block elements, which is the degradation path for a terminal or font that cannot hold Braille.
- `Vertical` — `bool` — draw the series as a column rather than a row.
- `Auto` — `bool` — scale to the series' own range. Off means you set `Min`/`Max`, which is what you want when several sparklines must be comparable.
- `LastStyle` — `buffer.Style` — the most recent sample, which is what a reader looks for first.

## More on accessibility

The threshold defaults to reverse video, which is an **attribute** rather than a colour, and the last sample is marked distinctly. Colour is never the only signal, and for a terminal with `NO_COLOR` set the distinction survives.

## When not to use it

**Do not use it to read exact values.** Braille gives sub-cell resolution, not numeric precision. A sparkline answers "did it go up, and by roughly how much"; if the answer needs to be a number, print the number.

**Do not use it when the series is shorter than about eight samples.** Sub-cell encoding needs samples to spend. Three points render as three nearly identical columns and the shape is noise.

**Do not use it with `Auto` on when two sparklines sit next to each other.** Auto-scales to each series' own range, so two sparklines of very different magnitudes look identical. Set `Min`/`Max` explicitly for anything meant to be compared.

**Do not use it for a single current value.** That is [`Gauge`](/widgets/gauge/) or [`Meter`](/widgets/meter/).

**Do not use it expecting a legible result in a web font.** Braille in a browser is exactly the case the plain-text capture on this site exists for.

**Instead:** [`Gauge`](/widgets/gauge/) for one value, [`BarChart`](/widgets/barchart/) for categories rather than time.

## Related

- [`Gauge`](/widgets/gauge/) — the point, rather than the series.
- [`BarChart`](/widgets/barchart/) — categories, rather than a series.
- [Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/viz` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/viz)
