---
title: "Dashboards"
description: "Building the examples/markets screen — three reflowing bands, real network data on a goroutine, a focus ring, and per-panel key routing."
weight: 54
toc: true
---

# Dashboards

A widget catalog is evaluated by what an application can **build** with it, not
by what each widget does alone. So this page walks through `examples/markets`,
which is a real screen — a live finance dashboard — composed entirely from the
catalog.

```
go run github.com/serkanalgur/termmosaic/examples/markets@v1.0.0
go run github.com/serkanalgur/termmosaic/examples/markets@v1.0.0 --offline
```

`q` quits, `r` refetches immediately, `?` opens the help overlay, space pauses
the auto-refresh, and the wheel and mouse work on the panels.

> **On `examples/dashboard`.** An older program by that name still exists in the
> framework repository and it **overlaps `markets` heavily** — both are multi-panel
> screens built from the catalog. **Whether to keep it or retire it is undecided.**
> This page walks through `markets` because it is the one that exercises the parts
> this release is about: a goroutine feeding the screen through `Renderer.Post`,
> responsive bands, and keyboard-plus-mouse input. It has not been removed, and
> the two are not presented here as equally recommended.

## What is on the screen

Three bands, and the middle one is where the layout work is:

- a **KPI row** — four headline figures side by side: the spot rate, the
  day-on-day change, and the window's two extremes. Together they answer "where is
  it, which way is it going, and how far has it come" without the reader
  cross-referencing anything.
- a **time series** — a [`Sparkline`](/widgets/sparkline/) of the primary pair
  over the fetched window, a [`Gauge`](/widgets/gauge/) showing where the spot
  sits inside that window's range, and a [`Meter`](/widgets/meter/) of the day's
  move in basis points against named bands.
- a **detail band** — a [`Table`](/widgets/table/) of every tracked pair with its
  rate and signed change, and a [`BarChart`](/widgets/barchart/) of the largest
  moves.

**The application spells no border rune and invents no title threshold** — the
chrome belongs to `widgets/block`, per
[ADR 0008 §2](/adr/0008-style-and-text/).

## The data, and why it is on a goroutine

ECB FX rates come from **Frankfurter** and crypto from **CoinGecko**. **Neither
needs an API key**, which is a deliberate constraint: an example you cannot run in
the first thirty seconds is an example nobody runs.

The rule the example is built around is that **`Draw` never blocks**:

> The network runs on its own goroutine and hands its results over through
> `render.Renderer.Post`, so the render goroutine only ever reads state a fetch
> has already published. A dashboard that fetched on its frame path would freeze
> for up to the fetch timeout on every cycle.

**That is exactly the path v0.1.0 got wrong.** `Renderer.Post` queued callbacks
but never woke the frame pacer — `NeedsFrame()` ignored queued work while
callbacks only ran inside `Render`, so an app driving updates from `Post` painted
one frame and idled forever. `markets` is what surfaced it: live runs painted one
empty frame and stopped, while `--offline` masked it completely because an instant
fetch returned before the first frame ran. **Fixed in v0.2.0**, with a regression
test. If you are upgrading from v0.1.0 and your app used `Post`, that was your
bug. See the [FAQ](/faq/#why-did-my-app-freeze-on-v010).

**`--offline` is not a mock.** It runs the same layout and rendering code as the
live path, on a bundled capture of real responses, which is what the golden tests
render — so CI never depends on the internet and a golden failure is never a
network failure. It is also what you run on a plane.

**It degrades visibly.** A failed fetch says which source failed and keeps
whatever the other one returned; a fetch that has never succeeded replaces the
bands with a panel that names the failure. A dashboard that hangs on a dead
network, or that renders an absent number as zero, is worse than one that says
"no data".

## Three bands that reflow

The breakpoints are local named constants beside the layout, which is
[ADR 0007](/adr/0007-responsive-screens/)'s rule 5 — **they are this
application's product decisions and the framework deliberately has no vocabulary
for them**:

| Width | Arrangement |
|---|---|
| **≥ 108** | every panel, side by side |
| **≥ 86** | the series band **stacks** — gauge and meter move *beneath* the sparkline; the detail band keeps the table and gives the chart its own column |
| **≥ 58** | one panel per band: the sparkline alone, the table alone, and the KPI row cut to two figures by `geometry.ClampCount` |
| **< 58** | a one-line diagnostic, never a clipped dashboard |

Two things are worth copying here.

**The panels move; they do not merely get narrower.** The middle band is the one
that matters, and it is the one the layout test pins. Asserting "the screen
changed" would pass for a layout that had only reflowed its text; asserting that
the gauge's rectangle is now *below* the sparkline's rather than beside it cannot.

**`geometry.ClampCount` decides how many KPI tiles fit**, rather than the
application counting and comparing integers. That is the arithmetic the framework
ships precisely so applications do not re-derive it — see
[Layout and constraints](/concepts/layout/).

**This is what `examples/hello` got wrong until v0.2.0.** It used `Max(46)`
inside two `Fill(1)`s, so it shrank on a small terminal and never grew: a 200×60
screen still drew a 46×9 block floating in the middle. That is clamping, not
responsiveness. It now spans the terminal across four bands, and below 38×8 says
so in one line.

## One constraint solve, off the frame path

The layout is a `layout.Solve` call, not arithmetic divided by hand:

```go
rows := layout.Solve(layout.Vertical, bandConstraints, bandGap, r.H)
head := layout.Rect(r, layout.Vertical, rows, 0, 0)
body := layout.Rect(r, layout.Vertical, rows, 0, 1)
foot := layout.Rect(r, layout.Vertical, rows, 0, 2)
```

Two decisions worth copying:

- **`layout.Solve` rather than hand arithmetic**, because
  [ADR 0004](/adr/0004-layout-engine/) chose a closed constraint set precisely
  so that **exactly one solver exists**. A second arithmetic pass inside an
  application is how two solvers start to disagree about overflow.
- **The remainder goes to the last cell of each axis**, so the widgets fill the
  screen exactly. That is a consequence of the largest-remainder rule, not an
  extra pass.

**And it is not on the frame path.** Everything derived from the rectangle — which
band arrangement applies, how many KPI tiles fit, each band's rectangle — is
computed in an `adapt` function keyed on the rectangle, and recomputed only when
the rectangle differs. `Draw` reads those cached rectangles and calls the widgets'
`Draw`. It does not format, wrap, truncate, append or allocate.

That is not discipline for its own sake: **every string in the example is
formatted off the draw path**, because a `fmt.Sprintf` inside `Draw` is an
allocation per frame, which is exactly what
[ADR 0008 §4](/adr/0008-style-and-text/) forbids. `layout.Solve` allocates too —
it returns a newly allocated slice — which is a second reason it belongs in
`adapt` and not in `Draw`.

## Focus: a ring, and the keys nobody else wants

```go
d.focusables = []termmosaic.Focusable{d.table, d.tabRow}
```

Two entries, and the whole composition contract is this:

> **Widgets own their keys — the table consumes the arrows, the tab row consumes
> left and right — and the application owns the routing and the keys no widget
> wants: Tab, space, `r`, `?`, and the quit keys.**

Neither half knows about the other, which is why adding a panel to this screen
means adding it to the focus ring and nothing else. Space is the *application's*
key rather than a widget's because the thing it pauses is the **fetch**, which no
widget knows about.

**A key the application claims is consumed even when it did nothing visible**, so
a form never falls through to the next field because the reader pressed space at
the end of a list. It is the same rule `form.Select` applies internally, and it is
what stops `?` reaching the table as a stray rune.

> **This is the thing ADR 0009 exists to replace, and this example is the one
> that has not been converted.** The `keymap` layer **shipped in v0.6.0** — but
> `examples/markets` still dispatches by its own `switch`, so the routing above is
> what you write by hand here. `examples/hello` and `examples/search` have been
> converted; see their source for what the registry version of the above looks
> like. There is still **no command palette**, and a key the keymap consumes
> shadows a widget's own `switch` without the registry being able to report it.
> See [Limitations](/limitations/#v060-keymap--a-new-package-and-nothing-you-wrote-breaks).

## The mouse, and one routing decision worth stealing

Mouse capture is **opt-in in this example only**, and the previous mode is
restored on exit. [ADR 0005](/adr/0005-input-decoding/)'s default stays off,
because capturing the mouse takes the user's shell selection away.

The screen's help overlay is **modal for keys but deliberately not for the mouse**:
a reader who opened it and then clicks a table row expects the row to be selected,
and an overlay that swallowed the mouse too would be worse than no overlay. One
detail worth copying: while the help is open, `q` still quits — a help panel that
turned "quit" into "close a panel" for as long as it was open would be a trap.

**Click routing** offers the event to every focusable widget and takes focus from
the one that consumed it, so a click on a table row both selects the row and makes
the table the keyboard's target. No widget can do that on its own.

**Wheel routing is different, and the reason is that no widget can do it alone.**

Widgets are hit-tested — since v0.5.2, [ADR 0010](/adr/0010-mouse-routing/) says a
widget handles a pointer event only when the pointer is inside its `Bounds()` — so
the tab row no longer steals notches aimed at the panels beneath it. **Until
v0.5.2 it did**: `form.Tabs` consumed a wheel notch whether or not the pointer was
over it, and it is first in the focus ring, so it swallowed **every** notch in the
application.

So the example asks **the widget whose rectangle contains the pointer**, and only
that one. **Focus is deliberately not taken by a wheel event**: a reader scrolling
is reading, not committing to a panel, and moving focus under the pointer would
rewrite the key hint while they are still looking at the numbers. A click is the
gesture that commits.

**A notch over a KPI tile — which no widget in the ring owns — is now declined by
all of them and reaches the application**, which is the right outcome: nothing on
screen scrolls. Before v0.5.2 it scrolled the tab row by three.

The loop still exists, and it is worth knowing why: what it buys is the rule that
**the wheel never takes focus**, which no widget can implement alone.

Clicks are *not* routed this way, and the asymmetry is the point — a click is a
commitment to a panel, so the click loop falls through to ring order and takes
focus from whoever consumed it. Hit-testing is each widget's own business; see
[Limitations](/limitations/#input).

## The palette, and monochrome

Every widget here carries a non-colour signal, **which is the accessibility
requirement, not a bonus**:

- moves are **signed** — an arrow and a sign, never colour alone
- `Gauge` and `Sparkline` are Braille; `Meter`'s zone boundaries are `+` and its
  threshold is `|`, with the active band **named in text**

Check it yourself with `NO_COLOR=1`. If anything becomes unreadable, the example
has a bug rather than a theme — see [Accessibility](/concepts/accessibility/).

{{< widget-capture "gauge" >}}

{{< widget-capture "sparkline" >}}

{{< widget-capture "meter" >}}

{{< widget-capture "barchart" >}}

### Read those captures carefully

**`Gauge` and `Sparkline` are Braille.** In a web font those glyphs can take a
different advance width than a terminal gives them, and that destroys the
alignment the whole widget depends on. **That is why every widget page on this
site shows the exact plain-text capture beside the colour one.** The text is the
truth; the colour is the persuasion.

And none of these can show you the dial *moving* or the series *growing*, which
is the other thing a still frame cannot do.

## What this screen does not show

- **Performance under your data.** The flat-cost numbers in
  [Virtualization](/concepts/virtualization/) are the catalog's own benchmarks on
  the catalog's own scenes.
- **A resize against a real terminal.** See
  [Limitations](/limitations/#layout-and-responsiveness).
- **That the network behaves.** The golden tests render `--offline` precisely so
  a network failure can never be mistaken for a rendering failure.
- **A command palette.** There isn't one to show; see
  [Limitations](/limitations/#there-is-still-no-command-palette).

## Building your own

The order that works:

1. **Solve the layout first**, against `Block.Interior()` — see
   [Composing with Block](/guides/composing/). Get one constraint list per axis
   and `layout.Rect` for each child.
2. **Keep every network call off the frame path**, and hand results over through
   `Renderer.Post` rather than a shared mutable field.
3. **Decide the focus order**, as a slice. It is a list, not a tree walk, and it
   makes "Tab moves here" a statement.
4. **Route keys explicitly, and consume what you claim** — including on a no-op.
5. **Check the monochrome case.** `NO_COLOR=1 go run ./examples/markets`. If
   anything becomes unreadable, add a non-colour signal.
6. **Test it headlessly** — see [Headless testing](/concepts/headless-testing/).
   A dashboard is exactly the kind of screen that should have a golden file,
   because a layout regression shows up as a diff in a string rather than as an
   exception.

## Reading next

- [Data display](/guides/data-display/) — choosing the data widgets.
- [Composing with Block](/guides/composing/) — the chrome and the layout.
- [Performance](/guides/performance/) — what is measured and what is not.
- [Limitations](/limitations/) — including the `keymap` gap and the platforms
  this does not run on.