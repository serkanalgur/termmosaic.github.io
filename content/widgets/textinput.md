---
title: "TextInput"
weight: 5
description: "A single-line editable field with a cursor, a selection and undo."
widgetName: "TextInput"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewTextInput(r buffer.Rect) *form.TextInput"
capture: "textinput"
---

A single-line editable field with a cursor, a selection and undo.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

TextInput is a single-line editable text field: a caret, an optional selection, word motions, undo, and bracketed paste.

It is the reference implementation of the whole form set, because ADR 0005 §4 was written about it. Three properties are load-bearing and each is pinned by a test:

- EventPaste is ONE undoable operation. A 10,000-character paste is one step on the undo stack, so one Ctrl-Z removes the whole of it.
- Draw allocates nothing in steady state. The visible runs are rebuilt only when the text, the caret, the styles or the rect change, which is ADR 0007 §3's rect-keyed adaptation applied to a per-keystroke value.
- Draw is total for every rect, including 0×0 and 1×1, and below its MinSize it clips rather than blanking.

## Rendered output

{{< widget-capture textinput >}}

> **About this capture.** This capture is taken with the field focused, so the cursor mark is live.

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewTextInput(r buffer.Rect) *form.TextInput
```

`NewTextInput` takes only a rect. Everything else — placeholder, styles, the ASCII lever — is an exported field, and `Text` is also a field, set through `SetText`/`Text()` rather than by assignment so the widget can invalidate.

- `Placeholder` — `string` — shown while the field is empty. It is a placeholder, not a label: it disappears on the first keystroke.
- `SelectionStyle` — `buffer.Style` — how a selected range is drawn. Unset means reverse video, so selection is visible with no configuration and under `NO_COLOR`.
- `CursorStyle` — `buffer.Style` — the caret cell.
- `Ascii` — `bool` — force ASCII markers where the Unicode set would otherwise be used.

## Key contract

Keys are consumed only while the field is focused, so an unfocused field in a form cannot be typed into. Modifiers are read through KeyMod.Has, which is why every binding below has a spelled-out modifier rather than an exact match.

| Keys | Effect |
| --- | --- |
| `insert` | any printable rune |
| `backspace` | KeyBackspace; with ModCtrl or ModAlt, the word before ModCtrl+'h' is accepted too, because a terminal sends Ctrl-Backspace as 0x08 or as 'h' depending on terminfo |
| `delete` | KeyDelete; with ModCtrl or ModAlt, the word after |
| `left / right` | KeyLeft / KeyRight; with ModShift extends the selection, with ModCtrl or ModAlt moves by word |
| `home / end` | KeyHome / KeyEnd; with ModCtrl the whole text |
| `select all` | ModCtrl+'a' |
| `undo` | ModCtrl+'z' |
| `paste` | EventPaste, inserted verbatim minus CR and LF |

A newline cannot be typed: KeyEnter is NOT consumed, so the enclosing form decides what Enter means. That is why multi-line editing is TextArea's job and not this widget's.

## More on accessibility

The caret, the selection and focus are all **shapes or attributes**, not colours. Under `NO_COLOR`, which suppresses colour but not attributes, a selected range is still reverse video and a focused field still carries its marker. What `TextInput` does **not** provide is any notion of a label for a screen reader, because a terminal grid has no accessibility tree to attach one to — the label is your responsibility, drawn next to the field.

## When not to use it

**Do not use it for anything longer than a line.** It wraps rather than scrolls horizontally and does not do the vertical. Multi-line editing is [`TextArea`](/widgets/textarea/), and `TextArea` shares `TextInput`'s editor, so nothing is lost by going there.

**Do not use it for CJK, IME or emoji composition and expect it to work.** This is the sharpest limitation in the catalog. There is no preedit and no composition support — a deliberate deferral in ADR 0005 §7, not an oversight — and the consequence is *wrong* behaviour rather than degraded behaviour: on most terminals the committed text arrives as a burst of ordinary key events, so the text inserts correctly but the undo stack gains one entry per character, and a single Ctrl-Z removes one character instead of the composition. The event model reserves `EventCompose` so this can be added later as a feature rather than a rewrite, but it is not there in v0.x.

**Do not use it inside a `Block` sized from the outer rect.** The field's usable width is the block's interior after `Border` and `Padding`, and the placeholder and the value are truncated against *that*. Size it from the inner rect.

**Do not use it as a search box and expect a debounce or an incremental-results contract.** It is a text field. It emits no events; `Handle` consumes keys and mutates its own value, and the application reads `Text()` after the fact. Wiring a search is your loop's business.

**Do not rely on a wide glyph occupying one cell.** A double-width glyph takes two, and its continuation cell carries the owning span's style so the row does not flicker. If you are counting cells to place a field, you are counting wrong for any CJK or emoji content.

**Instead:** [`TextArea`](/widgets/textarea/) for multiple lines, [`Select`](/widgets/select/) for a closed set, [`Checkbox`](/widgets/checkbox/) for a boolean.

## Related

- [Input](/concepts/input/) — the event model, paste-as-one-event, and why the key path is 0-alloc.
- [Forms](/guides/forms/) — the nine form widgets as one workflow.
- [Limitations](/limitations/) — IME, wide glyphs, and the colour model now decided at v1.0.0.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
