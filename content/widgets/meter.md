---
title: "Meter"
weight: 20
description: "A budget with named zones, a threshold marker and the active zone's name in words."
widgetName: "Meter"
widgetPackage: "widgets/viz"
widgetConstructor: "viz.NewMeter(r buffer.Rect) *viz.Meter"
capture: "meter"
---

A budget with named zones, a threshold marker and the active zone's name in words.

Package `widgets/viz`. API reference: [pkg.go.dev/widgets/viz](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/viz).

Meter is a bounded value with named zones and a threshold marker.

## Rendered output

{{< widget-capture meter >}}

> **About this capture.** Two non-colour signals: the zone boundaries are drawn as '+', the threshold as '|', and the active band is named in text.

## Package context

Package viz provides the catalog's measurement and display widgets: ProgressBar, Gauge, Meter, Sparkline and BarChart.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- It repaints its whole Bounds() before drawing content (rule 3), by composing widgets/block.Block, whose Draw fills the rect in Background before anything else. No widget here draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Everything derived from the size — which regions survived the budget, where the axis labels go, the glyph ramp for a sparkline — is computed in the size-change check, cached against the rect, and only read in Draw.

## Constructing it

```go
viz.NewMeter(r buffer.Rect) *viz.Meter
```

`NewMeter` takes a rect; `Zones` is a slice of named ranges and `Threshold` a single value.

- `Zones` — `[]Zone` — named ranges across the track. The zone boundaries are drawn as `+`.
- `Threshold` — `float64` — the marker, drawn as `|`. A separate value from the zones: a zone boundary is a range edge, a threshold is a limit.
- `ThresholdVisible` — `bool` — show the threshold marker at all.
- `ShowName` — `bool` — draw the active zone's **name in words**. This is the signal that makes the meter readable without colour.

## More on accessibility

Three non-colour signals, which is more than any other viz widget: zone boundaries are `+`, the threshold is `|`, and the active band is named in text. `ShowValue` adds the number. A meter is designed to be read correctly on a monochrome terminal, and this is why it is the one widget here whose meaning does not depend on the colour capture at all.

## When not to use it

**Do not use it for work in progress.** It reads a bounded value against zones; it does not track progress toward a completion. That is [`ProgressBar`](/widgets/progressbar/).

**Do not use it without setting `Zones`.** Without named zones the bar is a progress bar with a threshold, and the threshold marker alone will not tell a reader what "over" means.

**Do not use it where the value is unbounded.** The whole widget is the range. Clamp it yourself or use a [`Sparkline`](/widgets/sparkline/).

**Do not use it to compare several series.** One meter is one bounded value. For several, either several meters in a [`Split`](/widgets/split/) or a [`BarChart`](/widgets/barchart/).

**Do not turn `ShowName` off.** It is the accessibility affordance, and turning it off leaves a coloured band with no legend on screen.

**Instead:** [`ProgressBar`](/widgets/progressbar/) for progress, [`BarChart`](/widgets/barchart/) for comparison across categories.

## Related

- [`Gauge`](/widgets/gauge/) — one value, no zones.
- [`ProgressBar`](/widgets/progressbar/) — progress, not a bounded reading.
- [Accessibility](/concepts/accessibility/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/viz` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/viz)
