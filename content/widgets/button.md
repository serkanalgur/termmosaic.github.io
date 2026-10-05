---
title: "Button"
weight: 12
description: "A labelled, activatable control with a default and a disabled state."
widgetName: "Button"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewButton(r buffer.Rect, label string) *form.Button"
capture: "button"
---

A labelled, activatable control with a default and a disabled state.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

Button is a focusable label that activates on Enter, Space or a click.

## Rendered output

{{< widget-capture button >}}

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewButton(r buffer.Rect, label string) *form.Button
```

`NewButton` takes the label. Disabled is a field, and a disabled button consumes nothing — not a click, not a key — so a form can disable an action without removing the widget from the tree.

- `Label` — `string` — truncated with a marker rather than clipped, so a button too narrow for its label says so.
- `FocusStyle` — `buffer.Style` — the whole button while focused. Unset means the label style with `AttrReverse`, so focus is visible with no configuration and under `NO_COLOR`.
- `Disabled` — `bool` — disabled state. A disabled button consumes no events at all.
- `DisabledStyle` — `buffer.Style` — unset means `MutedStyle`, because "you cannot do this" should not look available.

## Key contract

Keys are consumed only while focused, and a disabled button consumes nothing — not a click and not a key — so a form can disable an action without having to remove the widget from the tree.

| Keys | Effect |
| --- | --- |
| `activate` | KeyEnter, KeySpace |
| `focus` | a left click inside Bounds, which also activates |

## Accessibility

Focus is a SHAPE: the label is ringed with brackets — "[Save]" — while focused and padded with spaces — " Save " — while not. Brackets rather than colour, because the one thing a user must be able to see on a form full of buttons is which button Enter is about to press.

The two rings are the same width, so a button's size does not depend on its focus state. A form whose buttons reflow every time the user tabs between them is worse than one whose focus is a little less obvious.

## More on accessibility

Focus is a **shape**: the label is ringed — `[Save]` — while focused and padded with spaces — ` Save ` — while not. Both rings are the same width, so selecting focus cannot reflow a form, which matters more than it sounds: a row of buttons that reflows on every Tab is worse than one whose focus is a little less obvious. `FocusStyle` and `DisabledStyle` are the style of the **whole** button — label included. That is what their documentation has always said; until v0.5.1 they reached the ring and the fill but not the label, so a disabled button rendered brackets around default-coloured text.

## When not to use it

**Do not use it as a toggle.** A button presses; it does not hold a state. If pressing it should switch something on and pressing it again should switch it off, that is [`Toggle`](/widgets/toggle/). Getting this wrong means the screen cannot show the current state, which is the one thing a control is for.

**Do not use it to trigger something on a keystroke without checking focus.** `Handle` consumes keys only while the button is focused. Your loop has to move focus — the framework offers events to the focused widget and then to the tree, and it does not decide which of your buttons should be focused.

**Do not use it to disable an action that must remain discoverable** and then assume the user learns why. A disabled button is inert: no key, no click, no message. If the user needs to know *why* it is unavailable, leave it enabled and say so in a message, or put the reason in the label.

**Do not pack many of them into a narrow row and hope.** Labels truncate with a marker and the focus ring adds two cells. A row of buttons is a layout decision: measure, or use short labels.

**Instead:** [`Toggle`](/widgets/toggle/) for held state, [`Checkbox`](/widgets/checkbox/) for a setting in a form.

## Related

- [`KeyHint`](/widgets/keyhint/) — telling the user the button exists and how to press it.
- [Widgets and focus](/concepts/widgets-and-focus/) — who moves focus, and why the framework does not.
- [Forms](/guides/forms/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
