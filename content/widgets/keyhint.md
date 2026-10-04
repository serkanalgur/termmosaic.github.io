---
title: "KeyHint"
weight: 13
description: "A one-line bar of key names and their meanings."
widgetName: "KeyHint"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewKeyHint(r buffer.Rect, bindings []form.Binding) *form.KeyHint"
capture: "keyhint"
---

A one-line bar of key names and their meanings.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

KeyHint renders the keys available right now: the discoverability half of the form catalog.

It is a widget rather than a string helper because a hint is the one piece of a form that changes whenever the state changes — a Select with no options has nothing to activate, so its hint goes away — and because it must obey the same repaint and clipping rules as everything else. Drawing it by hand at each call site is how a form ends up with three different hint styles.

## Rendered output

{{< widget-capture keyhint >}}

> **About this capture.** This frame is 40 columns wide and the bar does not fit. It is **truncated with a marker**, not silently cut and not silently dropping entries — the trailing `…` is the widget telling you there were more keys. (The capture manifest's note for this widget says the opposite; the godoc and this frame are the evidence, so the note above wins. It is recorded rather than quietly dropped.)

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewKeyHint(r buffer.Rect, bindings []form.Binding) *form.KeyHint
```

`NewKeyHint` takes `[]Binding`, each a key and its meaning. It is a widget rather than a string helper precisely because a hint is the one piece of a form that changes whenever the state changes.

- `Bindings` — `[]Binding` — a key name and its meaning, in the order they should be shown. There is no priority field; an over-long bar is truncated with a marker from the right.
- `Sep` — `string` — the separator between bindings.
- `Ascii` — `bool` — ASCII key names for terminals without the Unicode arrows and such.

## Accessibility

Each binding's key is BRACKETED — "[tab] next field" — so the key is a shape distinct from its description and the hint is readable without colour. No colour is used at all by default: KeyStyle, HelpStyle and SeparatorStyle all resolve to the terminal's own colours, and the hint is legible as plain text.

## When not to use it

**Do not use it as the only documentation.** A hint bar shows the keys that are available *now*; it is a reminder, not a tutorial. A user who has never seen your program has not read it, and it is the first thing to disappear when the terminal is short — which is exactly when a confused user needs it.

**Do not list bindings that are not reachable in the current state.** The widget will faithfully render whatever you give it, including keys that do nothing. A hint bar that lies is worse than no hint bar, and this is the most common way to get it wrong.

**Do not expect it to reflow.** When the bar has fewer cells than the bindings need, it **truncates with a marker** — a trailing `…` — rather than reflowing onto a second line or dropping entries. Check the 40-column capture above: the last binding is cut and marked. There is no priority scale on `Binding`, so **the order you pass them in is the order they are sacrificed from the right**, and if the binding a user most needs is going to be the one cut, put it first.

**Do not put it on a fixed row you expect to survive a small terminal** without checking. It is one line tall and it is the first thing a narrow layout should give up.

**Instead:** Nothing — this is the right widget for the job. Put the durable explanation in your README and the ephemeral keys here.

## Related

- [`Button`](/widgets/button/) — what a hint is usually describing.
- [`Select`](/widgets/select/) — a `Select` with no options has nothing to activate, so its hint goes away.
- [Responsiveness and the size budget](/concepts/responsiveness/)
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
