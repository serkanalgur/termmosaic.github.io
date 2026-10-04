---
title: "Forms"
description: "The nine form widgets as one workflow — focus, layout, validation — and why there is no Form container."
weight: 52
toc: true
---

# Forms

The nine form widgets: [`TextInput`](/widgets/textinput/),
[`TextArea`](/widgets/textarea/), [`Select`](/widgets/select/),
[`Checkbox`](/widgets/checkbox/), [`Radio`](/widgets/radio/),
[`Toggle`](/widgets/toggle/), [`Tabs`](/widgets/tabs/),
[`Button`](/widgets/button/), [`KeyHint`](/widgets/keyhint/).

## There is no `Form` container, on purpose

**A `Form` type was deliberately not built.** [ADR 0004](/adr/0004-layout-engine/)'s
constraint solver plus the `layout` package already cover composition, and a
`Form` would have been a **second way to do the same thing**.

That is the whole reason, and it has a consequence you should know before you
start: **a form is a layout and a focus order, both of which you own.** It is
about thirty lines of your code, and every form you build will differ anyway.

What a `Form` container would have added that you would then have to configure
around: its own layout policy, its own focus policy, and a `Validate()` hook
whose signature would not fit your data. If you want all three, write them for
your application; they are three lines of code each and they will be right.

## What the package shares

From `widgets/form`'s own godoc, four rules, each a consequence of something
decided elsewhere:

- **A widget's space is `Bounds()`, never `buf.Size()`.**
- **Every widget repaints its entire `Bounds()` before drawing content**, because
  the renderer diffs and never clears.
- **`Draw` is total for every rect**, including 0×0 and 1×1 and anything below
  `MinSize()`, and it clips rather than blanking.
- **Nothing size-derived is built inside `Draw`.** `Wrap`, `Truncate` and span
  construction allocate, so each widget caches against the rect it was computed
  for and rebuilds when the rect, the text or the styles change.

Plus three package-wide rules:

- **`EventPaste` is ONE undoable operation.** A 10,000-character paste is one
  step on `TextInput`'s undo stack, so one Ctrl-Z removes the whole of it.
- **`Draw` allocates nothing in steady state.** The visible runs are rebuilt only
  when the text, the caret, the styles or the rect change.
- **Nothing consumes `KeyTab`.** Every widget lets Tab through, so a form can move
  focus out of any of them with the keyboard.

That last one is the reason a form composes. If a widget consumed `Tab` while
focused, the user would be trapped.

## The workflow

### 1. Compose, with a `Block` for the chrome

Solve against `Interior()` so the fields never know the border exists — see
[Composing with Block](/guides/composing/).

{{< widget-capture "textinput" >}}

### 2. Own the focus order

A slice of `Focusable` and an index. Both are cheap, and making "Tab moves here"
an explicit statement beats a tree walk.

```go
type screen struct {
    name  *form.TextInput
    agree *form.Checkbox
    save  *button.Button

    focusable []termmosaic.Focusable
    focus     int
}

func (s *screen) setFocus(i int) {
    s.focusable[s.focus].SetFocused(false)
    s.focus = i
    s.focusable[s.focus].SetFocused(true)
    s.Invalidate()
}
```

`Focusable` is optional and discoverable by type assertion, and implementations
invalidate themselves — you do not have to.

### 3. Handle what the widgets did not consume

Keys reach the focused widget first, so application-level keys are exactly what
is left:

```go
func (s *screen) Handle(ev termmosaic.Event) bool {
    if ev.Kind != termmosaic.EventKey {
        return false
    }
    switch {
    case ev.Key == termmosaic.KeyTab:
        s.setFocus((s.focus + 1) % len(s.focusable))
        return true
    case ev.Key == termmosaic.KeyEscape, ev.Rune == 'q' && ev.Mod == 0:
        return false // the loop quits
    }
    return false
}
```

### 4. Validate by polling

**There is no change event.** A widget mutates its own state and invalidates
itself; it does not notify anyone. So a form that enables a button when its
inputs become valid reads the state after the fact:

```go
// In Handle, after the switch: a form with four widgets can afford to poll.
s.save.Disabled = s.name.Text() == "" || s.agree.State() != form.Checked
if s.save.Disabled != wasDisabled {
    s.Invalidate()
}
```

That is not a workaround. On a form this size, polling is free, and a callback
per keystroke on every widget would be a design commitment the project has
deliberately not made.

### 5. Put the keys where the user is looking

`KeyHint` is the discoverability half of the catalog, and it is a widget rather
than a string helper because **a hint is the one piece of a form that changes
whenever the state changes** — a `Select` with no options has nothing to activate,
so its hint goes away.

{{< widget-capture "keyhint" >}}

## Choosing between the one-of-N widgets

Three widgets mean "one of these". They are not interchangeable:

| | Shows options | Best for |
|---|---|---|
| [`Select`](/widgets/select/) | below the field, scrollable | more options than fit, or a compact one-row control |
| [`Radio`](/widgets/radio/) | all at once, one row each | few options, and seeing them all matters |
| [`Tabs`](/widgets/tabs/) | as a strip above the pane | switching between **content**, not choosing a value |

`Tabs` is navigation, not a control that produces data. If the user is choosing
one of N *values*, `Tabs` is the wrong widget even though the interaction looks
similar.

And `Checkbox` versus `Toggle` is a semantic difference, not a visual one:

> A toggle means **"this is running right now"** and a checkbox means **"include
> this in the operation"**, and users read the two differently.

{{< widget-capture "checkbox" >}}

{{< widget-capture "radio" >}}

{{< widget-capture "select" >}}

{{< widget-capture "toggle" >}}

{{< widget-capture "tabs" >}}

{{< widget-capture "button" >}}

{{< widget-capture "textarea" >}}

## Two-state and one-of-N are not the same as a button

A `Button` presses. It does not hold a state, and it emits no event — `Handle`
consumes the key and returns. If pressing it should switch something on and
pressing it again should switch it off, that is a [`Toggle`](/widgets/toggle/),
because otherwise the screen cannot show the current state, which is the one
thing a control is for.

And a **disabled `Button` consumes nothing** — not a click, not a key. That is
deliberate, so a form can disable an action without removing the widget from the
tree. The cost is that the user gets no explanation: if they need to know *why*
an action is unavailable, leave it enabled and say so.

## What the form set cannot do

Stated here rather than discovered, because each of these is a real gap and
several are easy to assume otherwise:

- **`TextArea` has no rendered selection.** It tracks and moves a caret and
  supports editing, but the selected range is not drawn. `TextInput` renders its
  selection; `TextArea` does not. If a user needs to see part of a value they are
  editing, `TextArea` is the wrong widget.
- **No redo stack**, in either text field. There is undo.
- **No IME or composition.** Composing CJK in a `TextInput` produces *wrong*
  behaviour, not degraded behaviour — the committed text arrives as a burst of
  key events, so it inserts correctly but the undo stack gains one entry per
  character. See [Input](/concepts/input/).
- **No validation.** Nothing checks a field against a rule; that is your code.
- **No multi-select.** `Checkbox` is one box.
- **Mouse capture is off by default**, so clicking a field does nothing unless
  you enable it — and enabling it takes text selection and scrollback away from
  the user's shell.

## Accessibility, briefly

Every distinction in the form set is a shape or an attribute, so all of it
survives `NO_COLOR` and a monochrome terminal:

- Focus on a [`Button`](/widgets/button/) is `[Save]` ringed, not a colour.
- Selection in [`TextInput`](/widgets/textinput/) and
  [`Select`](/widgets/select/) defaults to reverse video.
- [`Checkbox`](/widgets/checkbox/) has three **marks**, one per state.

**And a form label is your job.** A terminal grid has no accessibility tree, so
`Placeholder` is not a label — it disappears on the first keystroke, which is
exactly when a user filling in the form most needs to know what the field was
for. See [Accessibility](/concepts/accessibility/).

## Reading next

- [`TextInput`](/widgets/textinput/) — the reference implementation of the whole
  form set, because ADR 0005 §4 was written about it.
- [Input](/concepts/input/) — the event model behind the key contracts.
- [Composing with Block](/guides/composing/) — the layout.
- [Your first app](/getting-started/your-first-app/) — this page as one file.