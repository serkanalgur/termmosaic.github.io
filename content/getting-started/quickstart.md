---
title: "Quickstart"
description: "One file, a bordered panel that survives a resize, annotated line by line."
weight: 12
---

# Quickstart

Here is the smallest complete TermMosaic program. It opens the terminal, draws a
bordered panel with a frame counter and the negotiated colour depth, survives a
resize, and exits on `q`, Escape or Ctrl-C.

It is also, near enough, `examples/hello` — so if a line here does not match what
you see in the repository, the repository is the source of truth:

```
go run github.com/serkanalgur/termmosaic/examples/hello@v0.5.2
```

## The program

```go
package main

import (
	"fmt"
	"os"
	"sync"
	"time"

	"github.com/serkanalgur/termmosaic"
	"github.com/serkanalgur/termmosaic/buffer"
	"github.com/serkanalgur/termmosaic/input"
	"github.com/serkanalgur/termmosaic/layout"
	"github.com/serkanalgur/termmosaic/render"
	"github.com/serkanalgur/termmosaic/term"
	"github.com/serkanalgur/termmosaic/widgets/block"
)

const (
	blockW = 46
	blockH = 9
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "hello:", err)
		os.Exit(1)
	}
}

func run() error {
	t, err := term.Open(os.Stdin, os.Stdout, os.Getenv)
	if err != nil {
		return err
	}
	// Restoring the terminal is not optional on any exit path: a program that
	// leaves a terminal in raw mode has broken the user's shell.
	defer t.Close()

	w, h := t.Size()
	caps := t.Capabilities()

	r := render.New(term.NewSink(os.Stdout), render.Config{
		Width:   w,
		Height:  h,
		Caps:    caps,
		NoColor: render.NoColorFromEnv(os.Getenv),
	})
	// This program has no text input, so a cursor blinking in the last cell drawn
	// would look like a bug. It is managed-but-hidden.
	r.SetCursor(render.Cursor{Valid: true, Visible: false})

	root := newPanel(rootBounds(w, h), caps.ColourDepth())
	r.SetRoot(root)

	if err := t.EnterRawMode(); err != nil {
		return err
	}
	if err := t.EnterAltScreen(); err != nil {
		_ = t.LeaveRawMode()
		return err
	}
	if err := r.Reset(); err != nil {
		return err
	}

	// Both the input loop and the heartbeat below may want to stop the program,
	// and closing a channel twice panics, so the close goes through sync.Once.
	quit := make(chan struct{})
	var quitOnce sync.Once
	stop := func() { quitOnce.Do(func() { close(quit) }) }

	// The input Source is built AFTER raw mode: the kitty keyboard query it sends
	// is answered on the input stream and is meaningless without raw mode.
	sink := term.NewSink(os.Stdout)
	src := input.NewSource(t, withProbe(input.DefaultConfig(), sink))

	// The panel shows a counter that changes when a frame is drawn, so it needs a
	// heartbeat to stay alive. A real application is invalidated by whatever it is
	// displaying, and should not have this goroutine at all.
	stopBeat := make(chan struct{})
	go func() {
		ticker := time.NewTicker(time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-stopBeat:
				return
			case <-quit:
				return
			case <-ticker.C:
				r.InvalidateAll()
			}
		}
	}()

	// Keys and resizes arrive on ONE ordered channel, so a resize can never be
	// delivered between the bytes of a half-read escape sequence.
	go func() {
		for {
			select {
			case <-quit:
				return
			case ev, ok := <-src.Events():
				if !ok {
					stop() // the terminal reached EOF
					return
				}
				switch ev.Kind {
				case termmosaic.EventKey:
					if isQuitKey(ev) {
						stop()
						return
					}
				case termmosaic.EventResize:
					// ADR 0007 §5's order, with nothing between the two steps:
					// recompute the root's rectangle, then resize the renderer.
					// Renderer.Resize never draws, so the whole interval is
					// available to recompute bounds, and Resize already forces a
					// full repaint.
					w, h = ev.Size.W, ev.Size.H
					root.bounds = rootBounds(w, h)
					r.Resize(w, h)
				}
			}
		}
	}()

	pacer := render.NewPacer(r)
	frameErr := make(chan error, 1)
	go func() { frameErr <- pacer.Run(quit) }()

	err = <-frameErr
	close(stopBeat)
	_ = src.Close()
	_ = r.LeaveAltScreen()
	_ = t.LeaveRawMode()
	return err
}

// withProbe wires the input Source's enable sequences and kitty query to the same
// sink the renderer writes frames through, so the two cannot interleave badly.
func withProbe(cfg input.Config, sink termmosaic.Sink) input.Config {
	cfg.WriteProbe = func(p []byte) error {
		if _, err := sink.Write(p); err != nil {
			return err
		}
		return sink.Flush()
	}
	return cfg
}

// isQuitKey reports whether ev should end the program. These are keys a person
// reaches for, expressed in the decoder's vocabulary rather than as raw bytes:
// Ctrl-C arrives as Ctrl+'c' rather than as 0x03, and Escape arrives as KeyEscape
// only after the decoder has waited out its ambiguity delay.
func isQuitKey(ev termmosaic.Event) bool {
	switch {
	case ev.Key == termmosaic.KeyEscape:
		return true
	case ev.Rune == 'q' || ev.Rune == 'Q':
		return ev.Mod == 0
	case ev.Rune == 'c':
		return ev.Mod == termmosaic.ModCtrl
	}
	return false
}
```

## The widget

The four-method `termmosaic.Widget` interface is the whole contract. Here is a
complete widget — a `Block` for the chrome and a body that changes each frame.

```go
// panel is the example's widget: a Block for the chrome, plus a body that
// changes each frame.
//
// The Block is a value field rather than a pointer because it has no identity:
// it is chrome, and a widget tree holding a pointer to a border would be one more
// thing to keep alive for no reason.
type panel struct {
	bounds buffer.Rect
	blk    block.Block
	depth  buffer.ColourDepth
	ticks  int
}

func newPanel(r buffer.Rect, depth buffer.ColourDepth) *panel {
	p := &panel{bounds: r, depth: depth}
	p.blk.SetBounds(r)
	p.blk.SetBorder(buffer.BorderPlain)
	p.blk.SetPadding(1)
	// The title is "termmosaic", not " termmosaic ": Block inserts the one space
	// on each side itself, and a caller that added them would shift the title two
	// columns right of where the border's interior says it belongs.
	p.blk.SetTitleString("termmosaic", stTitle)
	return p
}

func (p *panel) Bounds() buffer.Rect          { return p.bounds }
func (p *panel) Invalidate()                  {}
func (p *panel) Handle(termmosaic.Event) bool { return false }

// Draw paints the block. It runs every frame, as ADR 0003 specifies: widgets
// describe themselves on demand and are not required to implement incremental
// drawing, because Go cannot enforce invalidation discipline and silent
// invalidation bugs are the worst failure mode a TUI has.
func (p *panel) Draw(buf *buffer.Buffer) {
	// The Block is told its bounds every frame rather than only at construction:
	// the application recomputes them on a resize, and a Block whose rectangle
	// were stale would paint chrome in the wrong place (ADR 0007 §3).
	p.blk.SetBounds(p.bounds)
	p.blk.Draw(buf)

	// The body draws into the Block's interior, so it cannot touch the border,
	// the title or the padding however the block is resized.
	p.drawBody(buf, p.blk.Interior())
}

func (p *panel) drawBody(buf *buffer.Buffer, r buffer.Rect) {
	p.ticks++
	rows := [...]struct{ label, value string }{
		{"frame", ""},
		{"depth", p.depth.String()},
		{"quit", "press q"},
	}
	for i, row := range rows {
		const labelCol, valueCol = 0, 10
		if r.W <= valueCol || r.H <= i {
			// Too narrow for a value, or too short for this row: skip it and keep
			// the rest. Clipping, never blanking.
			continue
		}
		buf.SetString(r.X+labelCol, r.Y+i, row.label, stMuted)
		if i == 0 {
			p.writeInt(buf, r.X+valueCol, r.Y+i, p.ticks)
			continue
		}
		buf.SetString(r.X+valueCol, r.Y+i, row.value, stValue)
	}
}

// writeInt writes v's decimal digits left to right. It is the allocation-free
// replacement for fmt.Sprintf("%d", v) on the draw path: fmt.Sprintf allocates,
// and one allocation per frame is exactly what the 0-allocs draw path forbids.
func (p *panel) writeInt(buf *buffer.Buffer, x, y, v int) int {
	div := 1
	for d := v / 10; d > 0; d /= 10 {
		div *= 10
	}
	for {
		buf.Set(x, y, rune('0'+v/div%10), stValue)
		x++
		if div == 1 {
			return x
		}
		div /= 10
	}
}
```

The style constants `stTitle`, `stMuted` and `stValue` come from
`buffer.NewStyle`, shown next.

## Styles

There is no theme. A `buffer.Style` is a foreground, a background and an
attribute set, passed **by value**, and it is built with `buffer.NewStyle` rather
than a composite literal — a partial literal would silently leave a channel at
opaque black, which is `Style`'s documented footgun.

```go
var (
	bg      = buffer.NewColour(0x10, 0x14, 0x1c)
	fg      = buffer.NewColour(0xd8, 0xdc, 0xe4)
	titleFg = buffer.NewColour(0x30, 0xc0, 0x80)
	dim     = buffer.NewColour(0x60, 0x6a, 0x7a)
	edge    = buffer.NewColour(0x30, 0x36, 0x40)
)

var (
	stBody   = buffer.NewStyle(fg, bg, 0)
	stMuted  = buffer.NewStyle(dim, bg, 0)
	stValue  = buffer.NewStyle(fg, bg, 0)
	stAccent = buffer.NewStyle(titleFg, bg, 0)
	stTitle  = buffer.NewStyle(titleFg, bg, buffer.AttrBold)
	stEdge   = buffer.NewStyle(edge, bg, 0)
)
```

This is an application's styling decision, which is where
[ADR 0008](/adr/0008-style-and-text/) puts it: **the framework ships no default
colours at all**, only attribute-only named styles. See
[No theme, and why](/concepts/no-theme/).

## Layout: why two `layout.Solve` calls

```go
// rootBounds returns the panel's rectangle inside an sw-by-sh screen.
//
// It is two layout.Solve calls — one per axis — because that is the documented
// path rather than the anti-pattern ADR 0007 was written about. The
// centred(sw, sh, 46, 9) this replaces hard-coded the block's size, clamped it by
// hand, and used centre-of-screen arithmetic that no amount of shrinking made
// correct: at 20x8 the user got a 20x8 block whose body rows were silently cut
// off, and at 10x4 the title and the body with it. Nothing crashed and nothing
// was useful — the block survived rather than adapted.
func rootBounds(sw, sh int) buffer.Rect {
	xs := layout.Solve(layout.Horizontal, centredOnAxis(blockW), 0, sw)
	ys := layout.Solve(layout.Vertical, centredOnAxis(blockH), 0, sh)
	return buffer.Rect{
		X: layout.Offset(xs, 0, 1),
		Y: layout.Offset(ys, 0, 1),
		W: xs[1],
		H: ys[1],
	}
}

// centredOnAxis puts a block of n cells in the middle of one axis: n cells if
// they fit, and whatever is left over shared evenly either side if they do not.
func centredOnAxis(n int) []layout.Constraint {
	return []layout.Constraint{layout.Fill(1), layout.Max(n), layout.Fill(1)}
}
```

`Max(n)` says what the previous code meant: as much room as this block would
like, never more than the screen has. The two `Fill(1)` either side *are* the
centring — the leftover space, shared equally — and when there is no leftover
they get nothing, which **is** the clamp, expressed rather than hand-written.

Two properties `Solve` guarantees that the old arithmetic could not:

- **`Max` is bounded by the space it is measured against**, so the result cannot
  overflow the screen and needs no clipping afterwards (ADR 0007 §1 rule 2).
- **Largest-remainder distribution is deterministic.** It hands a leftover cell
  to the *earliest-declared* `Fill`, so when the slack above and below is odd the
  panel sits one row **lower** than dead centre. On a 14-row screen that is three
  rows above and two below. That is documented behaviour, not a bug to work
  around.

## The five things that will bite you

1. **A widget's space is `Bounds()`, never `buf.Size()`.** The buffer is the
   screen; the rect is the widget's space. This is rule 1 of ADR 0007 §1 and
   every widget in the catalog obeys it.
2. **A widget repaints its whole `Bounds()` before drawing content into it.**
   The renderer diffs and never clears, so a widget that does not repaint its
   rect leaves stale cells behind after a shrink. `Block` fills the rect in
   `Background` first, which is why composing one is the easy way to comply.
3. **Anything derived from the size is computed once per size change, not per
   frame.** `Draw` must be allocation-free; `buffer.Wrap` and `buffer.Truncate`
   allocate and are therefore banned from `Draw`. Cache against the rect, rebuild
   when the rect changes.
4. **A widget that caches on `Bounds()` must drop that cache when anything else
   `Draw` reads changes.** `Invalidate()` now means *both* "mark dirty" and "drop
   every value you have cached". A widget that caches column widths on `Bounds()`
   and is then handed `Header = true` renders the old layout permanently — nothing
   will produce a different rect to repair it. This is ADR 0007's 2026-10-04
   amendment and it is the sharpest edge in the framework.
5. **Move focus deliberately.** `Handle` is offered to the focused widget first,
   then to the tree. A widget that consumes a key only while focused cannot be
   tabbed away from by itself — see [Widgets and focus](/concepts/widgets-and-focus/).

## Where to go next

- **[Your first app](/getting-started/your-first-app/)** — this same program with
  the pieces explained, plus input handling on a real widget.
- **[Widgets and focus](/concepts/widgets-and-focus/)** — the `Widget` interface,
  `Focusable` and `Minimizable`.
- **[Renderer and diff](/concepts/renderer/)** — what actually happens on
  `Render`.
- **[The catalog](/widgets/)** — 24 widgets, each with a captured frame.
- **[Input](/concepts/input/)** — the event model, and why paste is one event.