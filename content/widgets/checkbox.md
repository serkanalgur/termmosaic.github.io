---
title: "Checkbox"
weight: 8
description: "A tri-state box: unchecked, checked, or indeterminate."
widgetName: "Checkbox"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewCheckbox(r buffer.Rect, label string) *form.Checkbox"
capture: "checkbox"
---

A tri-state box: unchecked, checked, or indeterminate.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

Checkbox is a toggleable box with an optional label, in one of three states.

## Rendered output

{{< widget-capture checkbox >}}

> **About this capture.** Indeterminate is never produced by toggling. Only an application that has computed it from its children can set it, so the capture sets it directly.

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewCheckbox(r buffer.Rect, label string) *form.Checkbox
```

`NewCheckbox` takes the label as a string; the state is the widget's `State` field, not the constructor.

- `TriState` — `bool` — enable the third, indeterminate state. It exists because real forms have partial parents.
- `Label` — `string` — drawn after the box. Truncated with a marker if the rect is too narrow.
- `CheckedStyle` — `buffer.Style` — the filled box. The mark inside it is a glyph, not a colour.
- `Ascii` — `bool` — `[ ]`/`[x]` rather than the Unicode box set.

## Key contract

Keys are consumed only while focused.

| Keys | Effect |
| --- | --- |
| `toggle` | KeySpace or KeyEnter |
| `cycle left` | KeyLeft, but only when TriState is set cycle right KeyRight, but only when TriState is set |

Toggling moves Unchecked → Checked → Unchecked, and Indeterminate → Checked, because a user pressing space on a mixed box is asserting "yes, all of it". Reaching Indeterminate is done by SetState, from the application's own knowledge of its children. TriState additionally lets Left and Right walk all three states, which is what an application whose children can be partially selected needs in order to clear the mixed state from the keyboard.

## Accessibility

The marker is the state: "[ ]", "[x]" or "[-]". Three different SHAPES, so the state survives a monochrome terminal, NO_COLOR, and a reader who cannot distinguish the colours an application might add. CheckedStyle may make the checked box bolder or brighter, but nothing is lost if it does not.

## More on accessibility

Three states means three **marks**, not three colours: empty box, a cross inside, and a dash for indeterminate. The box itself changes shape between states, so a monochrome terminal and a `NO_COLOR` terminal both show which state it is in.

## When not to use it

**Do not use it for "this is running right now".** That is [`Toggle`](/widgets/toggle/), and the distinction is not cosmetic: a checkbox means *include this in the operation*, a toggle means *this is currently active*. Users read the two differently and putting the wrong one on screen changes what they think the program will do.

**Do not set the indeterminate state by toggling.** Toggling produces unchecked and checked and nothing else. Indeterminate is only reachable by an application that has computed it from its children — a parent checkbox over a half-selected group — so if you have no children, you cannot be in that state and showing it would be a lie.

**Do not use it for a mutually exclusive choice.** A group of checkboxes says "any combination". If only one may be chosen, that is [`Radio`](/widgets/radio/) or [`Select`](/widgets/select/), and getting this wrong lets a user select two things the program cannot honour.

**Do not use it for an action.** A checkbox is a setting. A thing you press is a [`Button`](/widgets/button/).

**Instead:** [`Toggle`](/widgets/toggle/) for a live on/off, [`Radio`](/widgets/radio/) for one-of-N, [`Button`](/widgets/button/) for an action.

## Related

- [`Toggle`](/widgets/toggle/) — the sibling, and the reason the marker differs.
- [Forms](/guides/forms/)
- [Accessibility](/concepts/accessibility/) — colour is never the only signal, across the catalog.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
