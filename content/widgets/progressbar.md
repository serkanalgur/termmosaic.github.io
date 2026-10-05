---
title: "ProgressBar"
weight: 18
description: "A ratio from 0 to 1 drawn as a filled block-element bar."
widgetName: "ProgressBar"
widgetPackage: "widgets/viz"
widgetConstructor: "viz.NewProgressBar(r buffer.Rect) *viz.ProgressBar"
capture: "progressbar"
---

A ratio from 0 to 1 drawn as a filled block-element bar.

Package `widgets/viz`. API reference: [pkg.go.dev/widgets/viz](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/viz).

ProgressBar is a determinate bar with a label, a percentage and a fill character.

It is a plain termmosaic.Widget: nothing about a bar is selectable, and a widget that claimed focus would swallow the keys its neighbours needed.

## Rendered output

{{< widget-capture progressbar >}}

> **About this capture.** Filled with U+2588 FULL BLOCK. The difference between FillStyle and TrackStyle carries an attribute as well as a colour, so the bar is readable without either.

## Package context

Package viz provides the catalog's measurement and display widgets: ProgressBar, Gauge, Meter, Sparkline and BarChart.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- It repaints its whole Bounds() before drawing content (rule 3), by composing widgets/block.Block, whose Draw fills the rect in Background before anything else. No widget here draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Everything derived from the size — which regions survived the budget, where the axis labels go, the glyph ramp for a sparkline — is computed in the size-change check, cached against the rect, and only read in Draw.

## Constructing it

```go
viz.NewProgressBar(r buffer.Rect) *viz.ProgressBar
```

`NewProgressBar` takes a rect; the ratio is the `Ratio` field.

- `Ratio` — `float64` — 0 to 1. Values outside the range are clamped, not an error.
- `Label` — `[]buffer.Span`, via `SetLabel(s, st)` for the common single-run case or `SetLabelSpans(spans)` for several styled runs. It was an exported field until v0.5.0. A label is a **measured** region, so a longer one shortens the bar at the same rect — which is why the setters drop the cached budget rather than merely repainting. Read it back with `Label()`, whose returned slice is the widget's own and must not be modified.
- `Percentage` — `bool`, via `SetPercentage(on)` — show the percentage. The number is the reading; the bar is the shape. It was an exported field until v0.5.0; the setter drops the cached budget so the bar re-solves at the same rect. Read it back with `Percentage()`.
- `FillRune` — `rune` — the fill glyph, `U+2588 FULL BLOCK` by default.
- `FillStyle` — `buffer.Style` — the filled part. The difference from `TrackStyle` carries an attribute as well as a colour, so the bar is readable with either suppressed.

## More on accessibility

Two non-colour signals: the fill character differs from the track character, and the fill and track styles differ by attribute as well as colour. With `NO_COLOR` set, or on a monochrome terminal, the bar still reads.

## When not to use it

**Do not use it for work whose completion is unknown.** There is no indeterminate mode. A bar that fills toward a target it cannot compute is a lie that resolves to 100% and then stops; if you do not know the denominator, show a [`Sparkline`](/widgets/sparkline/) or a [`Meter`](/widgets/meter/) of what you do know, or say nothing.

**Do not use it for a bounded measurement.** A `ProgressBar` answers "how far along"; it has no zones, no threshold and no named range. That is [`Meter`](/widgets/meter/), and a progress bar used for a bounded value loses the threshold — the one thing a reader scanning the screen wants.

**Do not use it for a value that is not 0-to-1.** A percentage that climbs to 400% reads as a bug even when it is correct. Normalise it yourself.

**Do not use it as a spinner.** It does not animate, and nothing in the catalog does. A busy indicator is yours to draw, and on reflection it is usually better as a label that says what is happening.

**Instead:** [`Meter`](/widgets/meter/) for a bounded reading with zones, [`Sparkline`](/widgets/sparkline/) for a rate over time.

## Related

- [`Meter`](/widgets/meter/) — bounded, zoned, with a threshold.
- [`Gauge`](/widgets/gauge/) — a single value on a dial.
- [`Sparkline`](/widgets/sparkline/) — a series rather than a point.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/viz` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/viz)
