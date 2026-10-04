---
title: "Toggle"
weight: 10
description: "A two-state switch with an on and an off rendering."
widgetName: "Toggle"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewToggle(r buffer.Rect, label string) *form.Toggle"
capture: "toggle"
---

A two-state switch with an on and an off rendering.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

Toggle is an on/off switch with an optional label.

It is not a Checkbox with a different marker: a toggle means "this is running right now" and a checkbox means "include this in the operation", and users read them differently. The difference is spelled in the marker — the words "on" and "off" — because a bare "[x]" would be ambiguous between the two.

## Rendered output

{{< widget-capture toggle >}}

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewToggle(r buffer.Rect, label string) *form.Toggle
```

`NewToggle` takes the label; the state is a field.

- `Label` — `string` — drawn after the switch.
- `OnStyle` — `buffer.Style` — the on rendering. The on and off states are different **marks**; `OnStyle` is decoration on top of that, not the signal.
- `Ascii` — `bool` — `[on]`/`[off]` rather than the Unicode switch set.

## Key contract

Keys are consumed only while focused. Every binding toggles; there is no "set to on" key, because a toggle has two states and reaching either is the same action.

| Keys | Effect |
| --- | --- |
| `toggle` | KeySpace, KeyEnter, KeyLeft, KeyRight |

## Accessibility

The state is the WORD: "[on]" or "[off]", both five cells wide so the label never moves when the state changes. Nothing about the state depends on colour.

## When not to use it

**Do not use it as a checkbox.** It is not a `Checkbox` with a different marker, and the difference is semantic: a toggle says *this is running right now*, a checkbox says *include this in the operation*. Use whichever claim you actually mean.

**Do not use it to trigger an action.** Toggling changes state; it does not do the thing. If pressing it should start something, that is a [`Button`](/widgets/button/).

**Do not expect the framework to make the change.** `Handle` flips the widget's own field and invalidates it. If flipping it should start a job, stop a service or write a setting, the application observes that and does it — there is no callback and no event.

**Do not use it in a form where the label must be a separate field.** The label is drawn inline after the switch, and a two-column form of "label" / "control" is a layout job — see [Forms](/guides/forms/).

**Instead:** [`Checkbox`](/widgets/checkbox/) for an operation setting, [`Button`](/widgets/button/) for an action.

## Related

- [`Checkbox`](/widgets/checkbox/) — the same two states with a different meaning.
- [Forms](/guides/forms/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
