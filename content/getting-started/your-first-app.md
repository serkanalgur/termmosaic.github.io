---
title: "Your first app"
description: "Terminal, renderer, input, focus and the frame loop — end to end, with the failure modes named."
weight: 13
---

# Your first app

The [quickstart](/getting-started/quickstart/) gave you a panel and a loop. This
page adds the two things a real application needs and the quickstart deliberately
omits: **a widget that takes keys**, and **a layout with more than one thing in
it**.

Everything here is still pre-alpha. The [limitations](/limitations/) page applies
in full.

## The shape of a TermMosaic program

There is no framework object, no `App.Run()` and no message algebra. Five pieces,
each owned by you:

| Piece | What it is |
|---|---|
| `term.Terminal` | Size, raw mode, alternate screen, capability probing, reading. Two narrow interfaces — `Terminal` and `Sink` — and a direct `x/sys` implementation. |
| `render.Renderer` | Owns the double-buffered cells, the dirty rectangles, the two-tier diff and the pacer. You give it a root widget. |
| Your widget tree | Plain Go values implementing four methods. No registration, no reconciler. |
| `input.Source` | One ordered channel carrying decoded keys, mouse events and resizes. |
| Your loop | A `quit` channel, a goroutine per source, and `pacer.Run(quit)`. |

Two design decisions shape all of it and are worth knowing before you write
anything:

- **The renderer is hybrid, not retained-with-reconciler.** You keep the widget
  tree and invalidate rectangles. There is no virtual tree and no Elm-style loop,
  because requiring widget authors to implement correct incremental invalidation
  is a discipline Go cannot enforce. The cost is that `Draw` runs for every widget
  every frame — about 81 µs for 12,000 cells — with no lever to pull if that ever
  stops being cheap. [ADR 0003](/adr/0003-renderer-mode/).
- **The terminal layer is ours.** `tcell`'s flush costs 280,814 ns/op on a
  one-row-dirty workload where TermMosaic's two-tier diff costs 7,133 ns/op, and
  `tcell`'s headless backend cannot expose the cell buffer that widget tests need.
  That measurement is what settled [ADR 0001](/adr/0001-backend-strategy/), and
  it is why there is no compatibility layer with any other TUI.

## A form, with focus and keys

Three widgets, a solved layout, and a focus order you move yourself.

```go
package main

import (
	"fmt"
	"os"

	"github.com/serkanalgur/termmosaic"
	"github.com/serkanalgur/termmosaic/buffer"
	"github.com/serkanalgur/termmosaic/layout"
	"github.com/serkanalgur/termmosaic/render"
	"github.com/serkanalgur/termmosaic/term"
	"github.com/serkanalgur/termmosaic/widgets/block"
	"github.com/serkanalgur/termmosaic/widgets/button"
	"github.com/serkanalgur/termmosaic/widgets/form"
	"github.com/serkanalgur/termmosaic/widgets/keyhint"
)

// screen owns the widget tree and the focus order.
//
// Both are plain values. Focus is an index into a slice this type owns, not a
// tree walk, because the framework offers events to the focused widget and then
// to the tree and has no opinion about which of your widgets that should be.
type screen struct {
	bounds buffer.Rect

	name  *form.TextInput
	agree *form.Checkbox
	save  *button.Button
	hint  *keyhint.KeyHint

	// focus is an index into focusable, not a pointer. A slice keeps the order
	// visible and makes "Tab moves here" a statement rather than an accident.
	focusable []termmosaic.Focusable
	focus     int
}

func newScreen(r buffer.Rect) *screen {
	s := &screen{bounds: r}

	s.name = form.NewTextInput(buffer.Rect{})
	s.agree = form.NewCheckbox(buffer.Rect{}, "I have read the limitations")
	s.save = button.NewButton(buffer.Rect{}, "Save")
	s.save.Disabled = true // enabled once both the name and the box are set

	s.hint = keyhint.NewKeyHint(buffer.Rect{}, []keyhint.Binding{
		{Key: "tab", Help: "next field"},
		{Key: "enter", Help: "save"},
		{Key: "q", Help: "quit"},
	})

	s.focusable = []termmosaic.Focusable{s.name, s.agree, s.save}
	s.setFocus(0)
	return s
}

// setFocus moves focus and tells both the old and the new widget. Implementations
// invalidate themselves; you do not have to.
func (s *screen) setFocus(i int) {
	if s.focusable[s.focus] != nil {
		s.focusable[s.focus].SetFocused(false)
	}
	s.focus = i
	s.focusable[s.focus].SetFocused(true)
	s.Invalidate()
}

// Bounds satisfies termmosaic.Widget.
func (s *screen) Bounds() buffer.Rect { return s.bounds }

// Invalidate satisfies termmosaic.Widget.
//
// It marks the whole rectangle. Returning the layout-derived rects as well would
// be marginally cheaper and would need keeping in step with the layout, which is
// not a trade worth making by hand — see the sizing helper below.
func (s *screen) Invalidate() {}

// Handle satisfies termmosaic.Widget.
//
// Keys reach the focused widget first, so if it consumes them they never arrive
// here. What reaches here is everything the widget set did not take — which is
// exactly where application-level keys like Tab and q belong.
func (s *screen) Handle(ev termmosaic.Event) bool {
	if ev.Kind != termmosaic.EventKey {
		return false
	}
	switch {
	case ev.Key == termmosaic.KeyTab:
		s.setFocus((s.focus + 1) % len(s.focusable))
		return true
	case ev.Key == termmosaic.KeyEscape, ev.Rune == 'q' && ev.Mod == 0:
		return false // let the loop quit
	}

	// A widget that changed something the rest of the screen depends on has to
	// say so. There is no change event; polling after the fact is the pattern,
	// and on a form with four widgets it is free.
	if s.agree.State() == form.Checked {
		s.save.Disabled = false
		s.Invalidate()
	}
	return false
}

// Draw satisfies termmosaic.Widget.
//
// Everything is drawn every frame. What is NOT done every frame is the arithmetic
// and the parsing: the constraint list is built once per size change, and each
// widget caches whatever it derived from its own rect.
func (s *screen) Draw(buf *buffer.Buffer) {
	// One Block owns the border, the title and the background for the whole
	// screen. Its Interior() is what the layout is solved against, which is how
	// the content stops needing to know that a border and a padding exist.
	chrome := block.New(s.bounds)
	chrome.SetBorder(buffer.BorderRounded)
	chrome.SetPadding(1)
	chrome.SetTitleString("New project", buffer.NewStyle(fg, bg, buffer.AttrBold))
	chrome.Draw(buf)

	r := chrome.Interior()

	// The constraint vocabulary, in full:
	//   layout.Length(n)      exactly n cells
	//   layout.Min(n)         at least n cells
	//   layout.Max(n)         at most n cells
	//   layout.Percentage(p)  a percentage of what is available
	//   layout.Ratio(n, d)    n/d of what is available
	//   layout.Fill(w)        share what is left, in proportion to w
	//
	// Solve returns the SIZE of each constraint, and layout.Rect turns a resolved
	// size list into the rectangle child i occupies. That pair is the composition
	// rule: nesting is not a second engine, it is Solve on a sub-rectangle.
	xs := layout.Solve(layout.Horizontal,
		layout.Fill(1),    // the field takes the slack
		layout.Length(12), // the button is fixed
		2,                 // two cells of spacing between them
		r.W,
	)
	ys := layout.Solve(layout.Vertical,
		layout.Fill(1),   // everything above the hint bar
		layout.Length(1), // the hint bar is one row
		1,                // one row of spacing
		r.H,
	)

	field := layout.Rect(r, layout.Horizontal, xs, 2, 0)
	cta := layout.Rect(r, layout.Horizontal, xs, 2, 1)
	agree := field
	agree.Y = field.Y + 1
	hint := layout.Rect(r, layout.Vertical, ys, 1, 1)

	s.name.SetBounds(field)
	s.agree.SetBounds(agree)
	s.save.SetBounds(cta)
	s.hint.SetBounds(hint)

	s.name.Draw(buf)
	s.agree.Draw(buf)
	s.save.Draw(buf)
	s.hint.Draw(buf)
}

func main() {
	t, err := term.Open(os.Stdin, os.Stdout, os.Getenv)
	if err != nil {
		fmt.Fprintln(os.Stderr, "app:", err)
		os.Exit(1)
	}
	defer t.Close()

	w, h := t.Size()
	r := render.New(term.NewSink(os.Stdout), render.Config{
		Width:   w,
		Height:  h,
		Caps:    t.Capabilities(),
		NoColor: render.NoColorFromEnv(os.Getenv),
	})

	root := newScreen(buffer.Rect{X: 0, Y: 0, W: w, H: h})
	r.SetRoot(root)

	if err := t.EnterRawMode(); err != nil {
		fmt.Fprintln(os.Stderr, "app:", err)
		os.Exit(1)
	}
	if err := t.EnterAltScreen(); err != nil {
		_ = t.LeaveRawMode()
		fmt.Fprintln(os.Stderr, "app:", err)
		os.Exit(1)
	}
	if err := r.Reset(); err != nil {
		fmt.Fprintln(os.Stderr, "app:", err)
		os.Exit(1)
	}

	quit := make(chan struct{})
	// … input goroutine and pacer exactly as in the quickstart …
	pacer := render.NewPacer(r)
	_ = pacer.Run(quit)
}
```

The elided tail is the same three blocks as the [quickstart](/getting-started/quickstart/):
a `sync.Once`-guarded `stop`, the goroutine reading `src.Events()` and switching
on `EventKey` and `EventResize`, and `close(stopBeat)` / `src.Close()` /
`LeaveAltScreen` / `LeaveRawMode` on the way out. Copy that file rather than
retyping it — it is
[`examples/hello/main.go`](https://github.com/serkanalgur/termmosaic/blob/main/examples/hello/main.go).

## Six rules that will save you a day

### 1. Your space is `Bounds()`, never `buf.Size()`

`buf.Size()` is the **screen**. `Bounds()` is **your** rectangle. A widget that
reads `buf.Size()` will happily paint over its neighbours. This is rule 1 of
[ADR 0007 §1](/adr/0007-responsive-screens/) and every widget in the catalog
obeys it.

### 2. Repaint your whole rect before drawing into it

The renderer **diffs and never clears**. So if a widget does not repaint its
`Bounds()` before drawing content, shrinking leaves stale cells on screen. A
[`Block`](/widgets/block/) in `Background` does this for you, which is the main
reason to compose one. [ADR 0007 §1 rule 3](/adr/0007-responsive-screens/).

### 3. Degenerate sizes are a contract, not an accident

**No panic, ever. Clip, never blank.** A 0×0 rect is valid and writes zero
bytes. A rect below `MinSize()` draws its minimum layout clipped. `Draw` must be
total for every rect, and there are tests that hold every widget to it — but
that is the framework's widgets. **Yours are your responsibility**, and this is
the single most common way a TermMosaic widget crashes on a resize.

### 4. Cache against the rect, and drop the cache when anything else changes

`Draw` must not allocate. `buffer.Wrap` and `buffer.Truncate` allocate and are
banned from `Draw`, so build them in a size-change check and read the result in
`Draw`.

**And `Invalidate()` now means both "mark dirty" *and* "drop everything you have
cached".** A widget that caches column widths on `Bounds()` and is then handed
`Header = true` renders the old layout *permanently* — nothing will produce a
different rect to repair it. This is ADR 0007's 2026-10-04 amendment, it is the
sharpest edge in the framework, and it applies to your setters too: **any setter
that writes a field `Draw` reads must invalidate.**

### 5. Build styles with `buffer.NewStyle`

A composite literal would silently leave a colour channel at opaque black.
`NewStyle` is the constructor that cannot do that. There is no theme — see
[No theme, and why](/concepts/no-theme/).

### 6. Move focus yourself, and offer events focused-first

`Focusable` is optional and discoverable by a type assertion. Events go to the
focused widget, then to the tree. So a widget that consumes `Tab` while focused
will trap the user — which is why none of them do. If your screen-level `Handle`
wants `Tab`, the widgets under it must not.

## Where to go next

- **[Concepts](/concepts/)** — the twelve ideas behind all of this.
- **[Forms](/guides/forms/)** — the nine form widgets as one workflow.
- **[Composing with Block](/guides/composing/)** — layout, borders and
  composition.
- **[Headless testing](/concepts/headless-testing/)** — how to test a widget
  without a terminal, which is the reason the headless sink exists.
- **[Widgets](/widgets/)** — the catalog, with captures.