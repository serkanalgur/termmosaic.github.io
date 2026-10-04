---
title: "Widgets"
weight: 40
description: "All 22 widgets, with a captured frame at three widths for each."
---

TermMosaic ships **22 widgets**. That number is the whole claim and it is counted, not estimated: it is every exported type with a `New…` constructor that satisfies `termmosaic.Widget`, and `buffer.Buffer` is deliberately not on the list because it is what widgets draw *into*, not a widget.

`widgets/form/optionlist.go` is an unexported shared helper behind `Select`, `Tabs` and `KeyHint`; it is not a twenty-third widget.

> There is no `Form` container widget. A `Form` type would have been a second way to do what [ADR 0004](/adr/0004-layout-engine/)'s constraint solver and the `layout` package already do, so it was not built. See [Forms](/guides/forms/) for how the form widgets compose.

Every page below carries the widget's captured frame at 40, 80 and 120 columns. Read [what a capture can and cannot show](/limitations/#captures-are-cell-grids-not-terminal-screenshots) before you read one as a promise about your own terminal.

## Core — `widgets/block`

| Widget | Summary | MinSize |
| --- | --- | --- |
| [`Block`](/widgets/block/) | A bordered, titled, padded rectangle that other widgets draw inside. | 5×5 |

## Core — `widgets/basic`

| Widget | Summary | MinSize |
| --- | --- | --- |
| [`Text`](/widgets/text/) | A single line of styled spans, aligned within its rectangle. | — |
| [`Paragraph`](/widgets/paragraph/) | Wrapped, styled prose that reflows to the width it is given. | — |

## Core — `widgets/split`

| Widget | Summary | MinSize |
| --- | --- | --- |
| [`Split`](/widgets/split/) | A container that divides its rectangle among focusable panes. | 3×1 |

## Forms — `widgets/form`

| Widget | Summary | MinSize |
| --- | --- | --- |
| [`TextInput`](/widgets/textinput/) | A single-line editable field with a cursor, a selection and undo. | 1×1 |
| [`TextArea`](/widgets/textarea/) | A multi-line editable field with wrapping, selection and undo. | 1×1 |
| [`Select`](/widgets/select/) | A single-choice control that expands into a scrollable list. | 1×1 |
| [`Checkbox`](/widgets/checkbox/) | A tri-state box: unchecked, checked, or indeterminate. | 1×5 |
| [`Radio`](/widgets/radio/) | A single-choice group of labels, navigated with the arrow keys. | 6×1 |
| [`Toggle`](/widgets/toggle/) | A two-state switch with an on and an off rendering. | 6×1 |
| [`Tabs`](/widgets/tabs/) | A horizontal strip of labels, one of which is the active pane. | 1×1 |
| [`Button`](/widgets/button/) | A labelled, activatable control with a default and a disabled state. | 3×1 |
| [`KeyHint`](/widgets/keyhint/) | A one-line bar of key names and their meanings. | 1×1 |

## Data — `widgets/data`

| Widget | Summary | MinSize |
| --- | --- | --- |
| [`List`](/widgets/list/) | A scrollable, selectable list with a marker gutter and a scrollbar. | 10×3 |
| [`Table`](/widgets/table/) | Rows in columns, with a header, a selection and horizontal scrolling. | 12×4 |
| [`Tree`](/widgets/tree/) | A hierarchy with expandable nodes, keyboard navigation and lazy row rendering. | 14×4 |
| [`Pager`](/widgets/pager/) | A scrollable long text with search, match highlighting and a position readout. | 10×4 |

## Visualization — `widgets/viz`

| Widget | Summary | MinSize |
| --- | --- | --- |
| [`ProgressBar`](/widgets/progressbar/) | A ratio from 0 to 1 drawn as a filled block-element bar. | 14×3 |
| [`Gauge`](/widgets/gauge/) | A bounded reading drawn as a Braille dial or a fallback bar. | 11×7 |
| [`Meter`](/widgets/meter/) | A budget with named zones, a threshold marker and the active zone's name in words. | 18×3 |
| [`Sparkline`](/widgets/sparkline/) | A series of numbers drawn as Braille or block elements, scaled to its own range. | 5×3 |
| [`BarChart`](/widgets/barchart/) | Categorical magnitudes as horizontal or vertical bars, with an axis and per-bar values. | 8×6 |
