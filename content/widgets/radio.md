---
title: "Radio"
weight: 9
description: "A single-choice group of labels, navigated with the arrow keys."
widgetName: "Radio"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewRadio(r buffer.Rect, labels []string) *form.Radio"
capture: "radio"
---

A single-choice group of labels, navigated with the arrow keys.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

Radio is a one-of-N group of options: exactly one is chosen, and the choice is visible without colour.

## Rendered output

{{< widget-capture radio >}}

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewRadio(r buffer.Rect, labels []string) *form.Radio
```

`NewRadio` takes the labels; the selection is a field.

- `FocusStyle` — `buffer.Style` — the whole group while focused. Unset means reverse video on the selected label.
- `OptionStyle` — `buffer.Style` — unselected labels.
- `Ascii` — `bool` — `(`/`)` rather than the Unicode radio set.

## Key contract

Keys are consumed only while focused. Moving with an arrow CHOOSES, which is how every radio group behaves: there is no separate "commit" step, because a radio group has no unselected state to commit from.

| Keys | Effect |
| --- | --- |
| `up / down` | KeyUp / KeyDown choose the previous / next option and fire |
| `left / right` | KeyLeft / KeyRight, so the group works in a horizontal form |
| `home / end` | KeyHome / KeyEnd choose the first / last option |
| `page up/down` | KeyPageUp / KeyPageDown choose one screenful away |
| `activate` | KeyEnter or KeySpace re-fires OnSelect for the chosen option, which is what a user pressing it to confirm expects |
| `wheel` | MouseWheelUp / MouseWheelDown scroll without choosing |

## Accessibility

Two independent non-colour signals, which is what a radio group needs and one checkbox is not enough of:

- the chosen option's marker is "(o)" and every other option's is "( )", so the choice is a SHAPE difference;
- the focused option carries a ">" in its own focus column, so focus is not signalled by the same thing that signals selection.

## When not to use it

**Do not use it when the options do not all fit.** `MinSize()` is 6×1, which is one row — the widget will show what fits and you are responsible for noticing. If the option count is dynamic and unbounded, [`Select`](/widgets/select/) scrolls; `Radio` does not.

**Do not use it for a set the user adds to at runtime** without rebuilding the widget, and do not expect the selection to survive that rebuild unless you hold it.

**Do not use it to mean "pick several".** A radio group is exactly one. If the user needs any combination, use [`Checkbox`](/widgets/checkbox/) per option.

**Do not use it when vertical space is the scarce resource and the options are long.** Every option is a row. One column of options that could have been a one-row [`Select`](/widgets/select/) is usually the wrong trade.

**Instead:** [`Select`](/widgets/select/) when the options overflow, [`Checkbox`](/widgets/checkbox/) when several may be chosen.

## Related

- [`Select`](/widgets/select/) and [`Checkbox`](/widgets/checkbox/) — the other one-of-N and many-of-N shapes.
- [Forms](/guides/forms/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
