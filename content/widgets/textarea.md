---
title: "TextArea"
weight: 6
description: "A multi-line editable field with wrapping, selection and undo."
widgetName: "TextArea"
widgetPackage: "widgets/form"
widgetConstructor: "form.NewTextArea(r buffer.Rect) *form.TextArea"
capture: "textarea"
---

A multi-line editable field with wrapping, selection and undo.

Package `widgets/form`. API reference: [pkg.go.dev/widgets/form](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/form).

TextArea is a multi-line editable text region that wraps rather than scrolls horizontally.

The wrapping is buffer's, not this widget's: the content is handed to buffer.Wrap and the resulting Wrapped is cached against the rect it was built for. Wrap allocates twice over, so calling it in Draw would add an allocation to every frame — the failure ADR 0008 §4 exists to prevent. The first Draw after a width change wraps; every Draw after that reads the cache.

## Rendered output

{{< widget-capture textarea >}}

## Package context

Package form provides the input widgets: TextInput, TextArea, Select, Checkbox, Radio, Toggle, Tabs, Button and KeyHint.

Four rules, each of which is a consequence of something decided elsewhere, and each of which is enforced by this package's tests rather than by convention:

- A widget's space is Bounds(), never buf.Size() (ADR 0007 §1 rule 1).
- Every widget repaints its entire Bounds() before drawing content, because the renderer diffs and never clears (ADR 0007 §1 rule 3).
- Draw is total for every rect, including 0×0, 1×1 and anything below MinSize, and it clips rather than blanking (ADR 0007 §4).
- Nothing derived from the size or from the text is built inside Draw. Wrap, Truncate and span construction allocate, so each widget caches the result against the rect it was computed for and rebuilds when the rect, the text or the styles change (ADR 0007 §3, ADR 0008 §4).

## Constructing it

```go
form.NewTextArea(r buffer.Rect) *form.TextArea
```

It shares `TextInput`'s editor, so the field surface is the same one: `Text`, caret motions, selection, undo, bracketed paste.

- `TextStyle` — `buffer.Style` — the content. An unset value resolves to the terminal's own colours.
- `CursorStyle` — `buffer.Style` — the caret cell.
- `Background` — `buffer.Style` — the field background.

## Key contract

Keys are consumed only while focused, and the caret moves by VISUAL line and cell column, so Up and Down follow the wrapping rather than the newline characters.

| Keys | Effect |
| --- | --- |
| `insert` | any printable rune |
| `newline` | KeyEnter inserts U+000A |
| `backspace` | KeyBackspace; ModCtrl or ModAlt deletes the word before |
| `delete` | KeyDelete; ModCtrl or ModAlt deletes the word after |
| `left / right` | KeyLeft / KeyRight; ModShift extends the selection, ModCtrl or ModAlt moves by word |
| `up / down` | KeyUp / KeyDown, one visual line |
| `home / end` | KeyHome / KeyEnd within the visual line; with ModCtrl, within the whole text |
| `page up/down` | KeyPageUp / KeyPageDown, one screen |
| `select all` | ModCtrl+'a' |
| `undo` | ModCtrl+'z' |
| `paste` | EventPaste, inserted verbatim INCLUDING newlines |

KeyTab is NOT consumed: in a form, tab moves between fields, and swallowing it here would make a text area impossible to leave with the keyboard.

## When not to use it

**Do not use it where the selected range must be visible.** In v0.3.0 `TextArea` **tracks and moves a caret and supports editing, but does not draw its selection**. `TextInput` renders its selection; `TextArea` does not. This is a recorded gap rather than a design choice, and it is one of the reasons `TextArea` is not the right widget for a value the user needs to see part of.

**Do not use it to show long text the user only reads.** It is editable and has no read-only mode. A scrolling read-only view is [`Pager`](/widgets/pager/), and a pager with search in it is usually what someone wants when they say "show me this file".

**Do not use it for a single-line field.** [`TextInput`](/widgets/textinput/) is the smaller widget and has the rendered selection this one lacks.

**Do not use it expecting a redo stack.** There is undo and there is no redo, in either field. The editor has no redo history and adding one is a widget API addition, not a patch.

**Instead:** [`Pager`](/widgets/pager/) to read, [`TextInput`](/widgets/textinput/) for one line.

## Related

- [`TextInput`](/widgets/textinput/) — the same editor, one line, with a rendered selection.
- [Forms](/guides/forms/)
- [Limitations](/limitations/) — no rendered selection here, no IME in either.
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/form` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/form)
