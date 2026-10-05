---
title: "Dialog"
weight: 24
description: "A modal box with a title, a body and a row of actions."
widgetName: "Dialog"
widgetPackage: "widgets/dialog"
widgetConstructor: "dialog.New(r buffer.Rect, v dialog.Variant) *dialog.Dialog"
capture: "dialog"
---

A modal box with a title, a body and a row of actions.

Package `widgets/dialog`. API reference: [pkg.go.dev/widgets/dialog](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/dialog).

Dialog is a modal: a bordered box with a title, a body, and a row of actions or a list of choices.

It is Focusable, and its keys are consumed only while it has focus. It is Minimizable, and MinSize is the whole widget including the border and padding the block contributes (ADR 0007 §2).

A Dialog is a plain value in every respect that matters: it is not safe for concurrent use, because SetBounds and Draw race by design — the renderer owns Bounds between frames (ADR 0003).

## Rendered output

{{< widget-capture dialog >}}

> **About this capture.** Modal: keys do not reach the tree beneath. The focused action is ringed rather than coloured - a bracket pair of the same width as the idle pair, so moving focus never reflows the row - and reinforced with reverse video, which survives NO_COLOR because colour is suppressed only at encode time. Escape is Cancel, never a no-op.

## Package context

Package dialog provides Dialog: the catalog's modal — a box with a title, a body, and either a row of buttons or a list of choices.

## Constructing it

```go
dialog.New(r buffer.Rect, v dialog.Variant) *dialog.Dialog
```

`NewDialog` takes a rect and a `Variant`: `VariantInfo`, `VariantConfirm` or `VariantChoice`. Actions are variadic, so `SetActions(a, b)` rather than a slice.

- `Variant` — `VariantInfo` (one dismiss), `VariantConfirm` (cancel and OK), `VariantChoice` (a pick list).
- `Actions` — `[]Action` — each a label and an optional style. A label too narrow for the row is truncated with a marker, never clipped.
- `CancelAction` — The index Escape activates. It is always set: Escape is Cancel, never a no-op.
- `BodyStyle / ActionStyle / FocusStyle / ChoiceStyle / ChoiceFocusStyle` — `buffer.Style` per element role.

## More on accessibility

The focused action is marked with a **ring** — a bracket pair of the same width as the idle pair, so moving focus never reflows the row — and reinforced with reverse video. Reverse video survives `NO_COLOR`, because colour is suppressed only at encode time. Focus is restored to whatever had it when the dialog closes, so tabbing order resumes where it was. The focused **choice** label is written in `ChoiceFocusStyle` as well as filled in it — until v0.5.1 it was filled and marked in the focus style while its *text* stayed in the unfocused one, so under the default styles the row a reader is meant to look at rendered dark-on-dark.

## When not to use it

**Do not use it for information the user did not ask for.** A dialog blocks the tree beneath it; putting a passive notice in one makes the user dismiss it to get on. Use a status line.

**Do not use it to ask more than one question.** Two questions in one dialog produce two partial answers and one guess at the rest.

**Do not use it for errors the user can fix themselves.** If the remedy is obvious, say it where they are instead of interrupting.

**Instead:** A passive status message belongs on a status line or a [`Meter`](/widgets/meter/); a single inline error belongs to [`TextInput`](/widgets/textinput/)'s own validation; a choice between many options is a [`Menu`](/widgets/menu/).

## Related

- Menu
- KeyHint
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/dialog` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/dialog)
