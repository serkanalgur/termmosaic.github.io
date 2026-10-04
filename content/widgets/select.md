---
title: "Select"
weight: 7
description: "A single-choice control that expands into a scrollable list."
widgetName: "Select"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewSelect(r buffer.Rect, labels []string) *form.Select"
capture: "select"
---

A single-choice control that expands into a scrollable list.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

Select is a closed list of options with one highlighted, scrollable when the options do not all fit.

## Rendered output

{{< widget-capture select >}}

> **About this capture.** A Select draws its options below the field rather than over the page, so the capture shows ten of the ten labels with the fifth highlighted.

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewSelect(r buffer.Rect, labels []string) *form.Select
```

`NewSelect` takes the labels up front as a `[]string`; the list is closed. `widgets/form/optionlist.go` is the unexported shared helper behind `Select`, `Tabs` and `KeyHint` — it is not a widget and has no page.

- `Marker` — `string` — the glyph drawn beside the highlighted option.
- `SelectedStyle` — `buffer.Style` — the highlighted option row. Unset means reverse video, so the selection survives `NO_COLOR`.
- `Ascii` — `bool` — force ASCII markers.

## Key contract

Keys are consumed only while focused. The wheel is consumed whether or not the widget is focused, because pointing at a list and scrolling it does not require taking focus away from whatever is being typed in.

| Keys | Effect |
| --- | --- |
| `up / down` | KeyUp / KeyDown highlight one option |
| `left / right` | KeyLeft / KeyRight highlight one option, so the widget works in a horizontal form layout too |
| `home / end` | KeyHome / KeyEnd highlight the first / last option |
| `page up/down` | KeyPageUp / KeyPageDown highlight one screenful |
| `activate` | KeyEnter or KeySpace accepts the highlighted option, which fires OnSelect without changing the highlight |
| `wheel` | MouseWheelUp / MouseWheelDown scroll without moving the highlight |

A closed list never changes what it contains, so there is no type-ahead and no Remove: a Select whose options change is a different widget.

## Accessibility

The highlighted option is marked by SelectDefaultMarker in its own marker column; every other option carries a space in that column. That is the non-colour signal, and it is deliberately a separate column rather than part of the label: a marker that moved with the text would shift every row's label one cell, which is exactly the misalignment a column exists to prevent.

## When not to use it

**Do not use it for a set the user can add to.** The label list is given at construction. An editable combobox would need text input, a filtered option list and a caret, and none of that is here — that is [`TextInput`](/widgets/textinput/) plus your own filtering.

**Do not use it when the option labels must wrap.** Options are truncated to the field width. A long option is marked as truncated rather than shown in full, so pick short labels.

**Do not use it in a `Block` whose width is driven by the label rather than by the layout.** `MinSize()` reports 1×1, which means *the widget is not asserting a minimum* — not that it renders well at one cell. The options are what need room, and the framework will not compute that for you.

**Do not confuse it with [`Tabs`](/widgets/tabs/) or [`Radio`](/widgets/radio/).** All three are one-of-N. `Select` draws the options below the field; `Radio` draws them all at once; `Tabs` is for switching between panes of content. Choosing wrong here is a layout decision you will regret.

**Instead:** [`Radio`](/widgets/radio/) to show every option at once, [`Tabs`](/widgets/tabs/) to switch panes, [`TextInput`](/widgets/textinput/) plus filtering for an open set.

## Related

- [`Radio`](/widgets/radio/) and [`Tabs`](/widgets/tabs/) — the other two one-of-N shapes.
- [Forms](/guides/forms/)
- `widgets/form/optionlist.go` on [GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form) — the unexported helper, for reading.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
