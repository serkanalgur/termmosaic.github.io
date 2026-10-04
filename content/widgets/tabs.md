---
title: "Tabs"
weight: 11
description: "A horizontal strip of labels, one of which is the active pane."
widgetName: "Tabs"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewTabs(r buffer.Rect, labels []string) *form.Tabs"
capture: "tabs"
---

A horizontal strip of labels, one of which is the active pane.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

Tabs is a single row of tab labels with one selected, scrollable when the tabs do not all fit.

## Rendered output

{{< widget-capture tabs >}}

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewTabs(r buffer.Rect, labels []string) *form.Tabs
```

`NewTabs` takes the labels. The labels are the tab strip; the panes behind them are yours — `Tabs` selects, it does not contain.

- `TabStyle` — `buffer.Style` — an unselected label.
- `SelectedStyle` — `buffer.Style` — the active label. The active tab also carries a distinct glyph, so it survives `NO_COLOR`.
- `Ascii` — `bool` — ASCII tab glyphs.

## Key contract

Keys are consumed only while focused. Moving with an arrow SELECTS, as in every tab bar: there is no separate commit step, because a tab bar has no unselected state to commit from.

| Keys | Effect |
| --- | --- |
| `left / right` | KeyLeft / KeyRight select the previous / next tab |
| `up / down` | KeyUp / KeyDown do the same, so a tab bar works in a vertical form layout too |
| `home / end` | KeyHome / KeyEnd select the first / last tab |
| `page up/down` | KeyPageUp / KeyPageDown select as many tabs as fit |
| `activate` | KeyEnter or KeySpace fires OnSelect for the selected tab |
| `wheel` | MouseWheelUp / MouseWheelDown scroll without selecting |

## Accessibility

The selected tab is BRACKETED — "[Name]" — and every other tab is space-padded — " Name ". The bracket is a shape, so the selection is readable in a monochrome terminal, under NO_COLOR, and by a reader who sees no difference between two colours an application chose. This is the requirement from ADR 0008's accessibility rule: a selected tab must be distinguishable without colour.

Keeping the unselected mark a space rather than nothing is deliberate. It means every tab is exactly its label plus two cells, so selecting a different tab cannot reflow the row, and the brackets are unambiguously the selection indicator rather than decoration.

## When not to use it

**Do not use it to hold the panes.** `Tabs` is the strip and the selection. The content behind each tab is a separate widget you show and hide. If you find yourself wanting a `Tabs` that owns its panes, that is [`Split`](/widgets/split/) plus a `Tabs` above it, and it is two widgets on purpose.

**Do not use it for a value.** It is navigation, not a control that produces data. If the user is choosing one of N *values*, that is [`Select`](/widgets/select/) or [`Radio`](/widgets/radio/).

**Do not expect the tab strip and the pane to resize together.** `Tabs` takes its own rect. Give it the strip row; give the pane the rest. That is a solved constraint list, not a nesting relationship.

**Do not use it when there are more tabs than fit and the important one is off-screen.** It scrolls, and which direction it scrolls in and where it lands on a state change is worth checking against your own labels.

**Instead:** [`Split`](/widgets/split/) plus a `Tabs` above it for content panes; [`Select`](/widgets/select/) for a value.

## Related

- [`Select`](/widgets/select/) — one of N, but as a value rather than as navigation.
- [Composition](/guides/composing/) — the `Split` + `Tabs` arrangement.
- [Forms](/guides/forms/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
