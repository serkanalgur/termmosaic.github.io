---
title: "BarChart"
weight: 22
description: "Categorical magnitudes as horizontal or vertical bars, with an axis and per-bar values."
widgetName: "BarChart"
widgetPackage: "widgets/viz"
widgetConstructor: "viz.NewBarChart(r buffer.Rect) *viz.BarChart"
capture: "barchart"
---

Categorical magnitudes as horizontal or vertical bars, with an axis and per-bar values.

Package `widgets/viz`. API reference: [pkg.go.dev/widgets/viz](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/viz).

BarChart is a categorical bar chart, vertical or horizontal, with an axis and value labels.

It is a plain termmosaic.Widget: a chart is not selectable.

## Rendered output

{{< widget-capture barchart >}}

> **About this capture.** Bars are Block Elements. The value beside each bar is the colour-independent reading and the capture keeps it.

## Package context

Package viz provides the catalog's measurement and display widgets: ProgressBar, Gauge, Meter, Sparkline and BarChart.

- Its space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- It repaints its whole Bounds() before drawing content (rule 3), by composing widgets/block.Block, whose Draw fills the rect in Background before anything else. No widget here draws a border, a corner or a title itself.
- Its Draw is allocation-free (ADR 0008 §4). Everything derived from the size — which regions survived the budget, where the axis labels go, the glyph ramp for a sparkline — is computed in the size-change check, cached against the rect, and only read in Draw.

## Constructing it

```go
viz.NewBarChart(r buffer.Rect) *viz.BarChart
```

`NewBarChart` takes a rect; `Data` is a slice of `Datum`, each a label and a magnitude.

- `Data` — `[]Datum` — label plus value per bar.
- `Vertical` — `bool` — bars grow upward. Horizontal is the default and the better fit for a narrow terminal.
- `Max` — `float64` — the scale ceiling. It defaults to the data's own maximum, which means the tallest bar always fills the plot; set it when the bars must be comparable to something else.
- `ShowValue` — `bool` — print the value beside each bar. That number is the colour-independent reading.
- `Axis` — `bool` — draw the axis line.

## More on accessibility

Each bar carries its **value as text** beside it, and the label is drawn regardless of colour. A reader who cannot distinguish two bar colours can still read every number.

## When not to use it

**Do not use it for a series over time.** Time is ordered and a bar chart is not; consecutive bars invite reading a trend that the data does not contain. A series is a [`Sparkline`](/widgets/sparkline/).

**Do not use it when the values are close together and the differences matter.** Bars encode magnitude by length from a common baseline, and that is exactly the encoding that hides small differences. Print the numbers, or use a different question.

**Do not use it vertically in a short terminal.** Vertical bars spend height on the plot and put the labels in the worst place. Horizontal is the default for a reason.

**Do not use it with dozens of categories.** A bar needs horizontal room for its label. Past roughly a dozen, a [`Table`](/widgets/table/) of names and numbers is both more readable and sortable, and it is what a user will want to do next.

**Do not use it to show one value.** That is [`Gauge`](/widgets/gauge/) or [`ProgressBar`](/widgets/progressbar/).

**Instead:** [`Sparkline`](/widgets/sparkline/) for time, [`Table`](/widgets/table/) for many categories, [`Meter`](/widgets/meter/) for one bounded reading.

## Related

- [`Sparkline`](/widgets/sparkline/) — series over time.
- [`Table`](/widgets/table/) — the honest answer for many rows.
- [Dashboards](/guides/dashboards/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/viz` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/viz)
