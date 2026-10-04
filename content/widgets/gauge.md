---
title: "Gauge"
weight: 19
description: "A bounded reading drawn as a Braille dial or a fallback bar."
widgetName: "Gauge"
widgetPackage: "widgets/viz"
widgetConstructor: "viz.NewGauge(r buffer.Rect) *viz.Gauge"
capture: "gauge"
---

A bounded reading drawn as a Braille dial or a fallback bar.

Package `widgets/viz`. API reference: [pkg.go.dev/widgets/viz](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/viz).

Gauge is a single bounded value on a dial, with a bar fallback.

## Rendered output

{{< widget-capture gauge >}}

> **About this capture.** The dial is Braille, U+2800..28FF: eight levels of vertical resolution in each cell, two samples per cell. A web font that gives those glyphs a different advance width destroys the arc, which is why the plain-text capture beside it is mandatory rather than a nicety.

## Package context

Package viz provides the catalog's measurement and display widgets: ProgressBar, Gauge, Meter, Sparkline and BarChart.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- It repaints its whole Bounds() before drawing content (rule 3), by composing widgets/block.Block, whose Draw fills the rect in Background before anything else. No widget here draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Everything derived from the size — which regions survived the budget, where the axis labels go, the glyph ramp for a sparkline — is computed in the size-change check, cached against the rect, and only read in Draw.

## Constructing it

```go
viz.NewGauge(r buffer.Rect) *viz.Gauge
```

`NewGauge` takes a rect; `Value` is a field in the widget's own range.

- `Value` — `float64` — the reading, in the units `Min`/`Max` define.
- `Min` — `float64` — the bottom of the dial.
- `Max` — `float64` — the top. A zero range is handled, not a divide-by-zero.
- `Dial` — unexported `dialParts` — the arc geometry, chosen by the rect. Exported as whole parts so the fallback and the dial cannot disagree.
- `ShowLabel` — `bool` — draw the label. `ShowValue` draws the number, which is the reading independent of the dial.

## More on accessibility

The dial is Braille, U+2800..28FF: eight levels of vertical resolution per cell, two samples per cell. A web font that gives those glyphs a different advance width destroys the arc, which is why the plain-text capture sits beside every colour capture on this site and why `ShowValue` exists. Read the number, not the shape.

## When not to use it

**Do not use it where the exact value matters and the dial is the only reading.** Braille gives roughly eight levels per cell; the arc tells a reader *roughly where*, and only `ShowValue` tells them *how much*. A gauge with `ShowValue` off is a decoration. If the number is the point, show the number.

**Do not use it in a rect too small to hold a dial.** It degrades to a bar — deliberately, so it never draws nonsense — but then you have a [`ProgressBar`](/widgets/progressbar/) with extra steps. Check `MinSize()` before you assume you got a dial.

**Do not use it for a series.** One bounded value is what a dial encodes. History is [`Sparkline`](/widgets/sparkline/).

**Do not use it for a bounded value with meaningful zones.** A dial has no threshold. That is [`Meter`](/widgets/meter/), and if the reader's question is "am I over the line", a dial cannot answer it.

**Do not screenshot it and expect the screenshot to survive.** This is the widget most exposed to the capture problem on this site. See [Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots).

**Instead:** [`Meter`](/widgets/meter/) for zones and a threshold, [`ProgressBar`](/widgets/progressbar/) for a plain ratio, [`Sparkline`](/widgets/sparkline/) for history.

## Related

- [`Meter`](/widgets/meter/) — the zoned, thresholded reading.
- [`ProgressBar`](/widgets/progressbar/) — the bar fallback this degrades to.
- [Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/viz` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/viz)
