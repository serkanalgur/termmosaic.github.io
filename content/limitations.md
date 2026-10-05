---
title: "Limitations"
description: "What TermMosaic does not do, every item traceable to the framework's own status document. Read this before you rely on anything."
toc: true
---

# Limitations

This page is not an appendix. It is linked from the landing page, from every
widget page's footer, and from the [FAQ](/faq/), and every item on it is
traceable to the framework's `docs/STATUS.md` or `CHANGELOG.md` at v0.4.1. If
something is missing here and you find it in the repository, that is a bug in
this page — [open an issue](https://github.com/serkanalgur/termmosaic/issues).

## Captures are cell grids, not terminal screenshots

**Every picture on this site is the cell grid the renderer produced, not a
screenshot of anyone's terminal.** It comes from `cmd/capture` in the framework
repo, which renders each widget through `widgettest.Capture` — the same path the
tests assert on — and translates `MemorySink.Cells()` into HTML.

That makes the captures trustworthy in one specific way: the documentation cannot
show something no test pins. It does not make them terminal screenshots. What is
**not** shown:

- **No interaction.** A capture is one settled frame after N frames of settling.
  It cannot show a keypress, a selection moving, a cell flickering, a pager
  scrolling, or a tree expanding. This is the largest gap and it is not closable
  without a browser build of the runtime, which
  [`docs/ARCHITECTURE.md`](https://github.com/serkanalgur/termmosaic/blob/main/docs/ARCHITECTURE.md)
  lists as a written non-goal ("no WASM build").
- **No animation or timing.** Frame pacing, the 30–60 fps budget and
  `render.Pacer` are invisible.
- **No live resize.** Each widget page shows three fixed widths instead —
  40, 80 and 120 columns — which is more informative than a resize demo because
  each frame is exact and the widths are named.
- **No terminal fidelity.** You are not seeing the reader's font or its cell
  aspect ratio, their colour scheme, their background, their terminal's
  wide-glyph behaviour, or any terminal-side ligature or shaping.
- **No cursor blinking, and the cursor mark is a convention.** The capture tool
  marks the cursor as a hollow, dotted-underlined cell, because a terminal cursor
  sits *under* a glyph rather than on top of it and a static frame cannot blink.

### Braille and Block Elements may misalign

**`Gauge` and `Sparkline` use Braille (U+2800–28FF); `ProgressBar`, `Meter`,
`Gauge` and `BarChart` use Block Elements (U+2580–259F).** In a web font these can
render at a different advance width than a terminal gives them, and that destroys
the alignment those five widgets depend on.

That is why **every widget page shows the plain-text capture beside the colour
one**, and why the plain-text form is the exact `MemorySink.String()` output —
the same thing the golden files compare against. The plain-text capture is
truthful. The colour capture is persuasive. If a gauge looks wrong in your
browser, read the text.

**One asymmetry, stated rather than hidden:** the colour captures come at all
three widths (40, 80, 120) but the plain-text capture comes at the **widest**
one only — 120 columns. The 40- and 80-column frames are available in colour
only. So the cross-width comparison on a widget page is a colour comparison, and
the exact-cell reference beside it is a 120-column reference.

**Do not mistake a captured frame for a live terminal.** A reader who does will
draw the wrong conclusion about how a widget looks on their own setup, and that
is the failure mode this page exists to prevent.

### What a capture *can* be trusted for

- Which glyphs are drawn, and in which cells — the plain-text form is exact.
- How a widget degrades across 40, 80 and 120 columns.
- Which states a widget has distinct renderings for, because a capture of each
  state is a separate file.
- `MinSize()`, which was **called**, not parsed, when the manifest was generated.

## Project stage

- **Pre-alpha. The API will break without notice before v1.0.0.** Every release
  before v1.0.0 is a pre-release and a minor version may contain behavioural
  changes. What *is* promised: **no behavioural change in a patch release.** If
  v0.1.1 changes behaviour, that is a bug in the release, not policy.
- **`Widget` is the one thing held fixed.** Four methods — `Bounds`, `Draw`,
  `Invalidate`, `Handle` — unchanged across all eight architecture decisions.
- **Anything marked PROPOSED may change or be reversed.** See the decision table
  in [`docs/STATUS.md`](https://github.com/serkanalgur/termmosaic/blob/main/docs/STATUS.md).
- **There is no version selector on this site.** The plan records this as a
  decision rather than an oversight: the widget pages are generated from the
  current source, so a version selector would have to render from a checkout, not
  from a site.
- **Not every widget has a runnable example yet.** `CONTRIBUTING.md` requires one
  per widget. Three programs exist today: `examples/markets` (the flagship — a
  live finance dashboard, keyboard and mouse driven),
  `examples/hello` (a responsive panel with a focus ring and a `?` help overlay),
  and `examples/dashboard`.
  **`examples/dashboard` overlaps `examples/markets` heavily and whether to keep
  it or retire it is undecided.** It has not been removed; the documentation
  points new readers at `markets` and does not present the two as equally
  recommended. Where a widget's page has no program to point at, that is the gap,
  and it is not papered over on the widget page.

## The `keymap` layer is specified, not built

**[ADR 0009](/adr/0009-command-and-keymap/) is Accepted, and nothing implements
it.** There is no `keymap` package in the framework, and **no command palette
exists.** `keymap` was targeted at v0.4.0, and **both v0.3.0 and v0.4.0
shipped on 2026-10-05 without it**, so there is no version it is currently
scheduled for.

**What you have today: widgets dispatch their own keys.** A `Table` consumes the
arrows, a `Menu` consumes its navigation, and the application writes the routing
plus the keys no widget wants — Tab, the quit keys, and anything specific to the
app. That is the pattern both examples use, and it is what ADR 0009 exists to
replace.

**Why it is listed here rather than left implicit:** a reader who reads ADR 0009
and finds no `keymap` package should conclude the ADR is unimplemented, not that
they missed something. The spec is real and the code is absent, and this site does
not blur the two.

One consequence already visible in the framework: `examples/markets` hand-rolls
its key routing and needs a `bindings()` function plus a help overlay that lists
the keys by hand. A command layer would make that declarative. Until then, it is
boilerplate you write yourself.

## `Renderer.Post` changed behaviour in v0.2.0 — apps on v0.1.0 should read this

**In v0.1.0, `Post` never woke the frame pacer, and any app driving screen updates
from `Post` painted one frame and idled forever.** `NeedsFrame()` ignored queued
callbacks while `Pacer.Run` gates every frame on `NeedsFrame()`, and posted
callbacks only run inside `Render` — so the callback could not run until a frame
happened, and a frame would not happen until the callback ran.

This is documented in [ADR 0003](/adr/0003-renderer-mode/) as **the safe way to
mutate widget state**, precisely because it is safe against a concurrent `Draw`.
So this was not an exotic path: it was the recommended one.

Fixed in v0.2.0, with a regression test. **This is why v0.2.0 is a minor bump and
not a patch — it is a behavioural change**, which the project's release policy
allows for a minor release and forbids for a patch.

**If you are moving from v0.1.0 and your screen was not updating**, this is why,
and upgrading fixes it. The symptom was a live-looking program that simply never
changed again — not a hang, a crash or a visible error.

## `Tree` label styling took effect in v0.4.0 — this changes what you see

**This is the change in v0.4.0, and it is a behaviour change rather than a new
feature: styling you set on a [`Tree`](/widgets/tree/) used to be silently
discarded on the label, and it is now honoured.** Nothing has to change to
compile or to run. But if your tree renders differently after upgrading, that is
this release working, not a regression.

**Plainly: a program whose `Tree` relied on its labels ignoring `Style`,
`ItemStyle` and `SelectedStyle` will now render differently.** Before this
release, a node's `Style`, the `ItemStyle` fallback and the selected row's
`SelectedStyle` reached the expander glyph and nothing else — the label was
written through a call that took no style, so it came out in whatever the
terminal's own default happened to be. Those three fields are documented as
applying to the node, and now they do.

`drawRow` computed the content style — node `Style`, falling back to
`ItemStyle`, and `SelectedStyle` outright when the row was selected — and applied
it to a single cell, then wrote the label beside it through a different call. The
computed style stopped exactly where the two code paths diverged. The label now
goes through the same `paintRow` path `List` and `Table` use, over a rectangle
covering the label region alone, so the fill cannot bleed into the expander
marker or the indent. Four tests pin it: node style reaching the label, the
`ItemStyle` fallback, a multi-span label keeping its own styles, and the ASCII
path.

**If you worked around the old behaviour, undo the workaround.** A program that
compensated in its own styles because the widget's were ignored is now
double-counting, and should remove the compensation.

**Why this is a minor bump and not a patch.** Changing what a library widget
draws is the definition of a behaviour change, and the project's release policy
puts those in a minor — a patch that changed behaviour would itself be a bug in
the release. The framework's [`CHANGELOG.md`](/adr/changelog/) records it under
Breaking.

**Two things in this release did not close.**

- **No capture on this site moved, and that is expected.** The generator's tree
  entry sets no styles, so it never exercised the broken path and the fix is
  inert for the captures. A widget page can be correct while its picture is
  merely uninformative.
- **The CI posture change has since been run, and it was green.** Every action
  moved to a Node 24 major and every runner image is pinned by name
  (`ubuntu-24.04`, `macos-15`, `windows-2025`) rather than tracking `-latest`.
  This was originally verified statically — each action's `action.yml` declares
  `using: node24` — and not by a run. **It has now been executed by a real GitHub
  Actions run: all twelve checks on the v0.4.0 pull request passed**, namely
  `test (ubuntu-24.04)`, `test (macos-15)`, `test (windows-2025)`, `gofmt`,
  `golangci-lint`, `zero-allocation diff`, and the six `cross-compile` legs for
  `linux/amd64`, `linux/arm64`, `darwin/amd64`, `darwin/arm64`,
  `windows/amd64` and `windows/arm64`. The post-merge run on `main` was green
  too, as was the v0.4.1 dependency-bump run.

  So the concern the previous release raised is closed: none of the four action
  major bumps changed an input, a default or a behaviour the project relies on,
  and `macos-15` and `windows-2025` are now images this project has actually run
  on rather than new ones it has only read about. **What that green run does not
  cover is the item below**, which no CI configuration has ever covered.

**And one long-standing item that this release did not fix.** The Windows backend
still runs **zero tests at runtime**. `term/terminal_windows_test.go` is
compile-only verified — `GOOS=windows go vet ./...` is the only check that has
ever covered it — and **those tests have never been executed anywhere.** It is
restated here because it is the item most easily mistaken for coverage: the file
exists and is substantial, which reads like Windows is tested, and it is not. See
[Platform](#platform) for why the Windows backend is a stub in the first place.

## `List` and `Table` styling took effect in v0.3.0 — this changes what you see

**This is the most visible change in v0.3.0, and it is a behaviour change rather
than a new feature: styling you set on a `List` or a `Table` used to be
silently discarded, and it is now honoured.** Nothing has to change to compile or
to run. But if your widgets look different after upgrading, that is this release
working, not a regression.

**Two independent bugs, one visible consequence each.**

On `List`, the style computed for each row was never actually passed to the paint
call — it was computed and thrown away. So a `List` drew each item using whatever
styles the item's own text spans happened to carry, and `SelectedStyle`, the field
documented as the selected row's rendition, reached only the background fill and
never the glyphs. `ItemStyle` on an unselected row and `SelectedStyle` on the
selected row now both apply, and on the selected row the selected style wins —
which is the precedence those two fields have always documented.

On `Table`, the sentinel passed to mean "write these spans verbatim" was
`buffer.DefaultStyle`, which is a wrong choice for that job: the unset check
compares against the zero `Style{}`, and `DefaultStyle` is a *resolved* style, not
an unset one. The guard therefore never fired, and every cell's own `Style` was
overwritten with the terminal's default colours — along with every column's
`CellStyle`. Cell spans and column styles now render as given. `HeadingStyle` was
never affected, because it is passed as a real override rather than as the
sentinel, and it still works.

**Why this is a minor bump and not a patch.** Both fields were already documented
as taking effect. The code contradicted its own documentation, so this is a fix to
behaviour that was already promised — but a patch release that changes what
renders would itself be a bug in the release, so the project policy makes it a
minor. The framework's [`CHANGELOG.md`](/adr/changelog/) records both under
Breaking.

**If you worked around the old behaviour, undo the workaround.** A program that
compensated in its own styles because the widget's were ignored is now
double-counting, and should remove the compensation.

**One thing that did not change: a multi-span row keeps its per-span styles.**
The override only applies when a row is a single span. Flattening a multi-span row
would mean building a string on the frame path, which the package's
zero-allocation claim rules out. A row that deliberately carries several styles
still renders with them. This limit was equally true before — it was just
invisible, because nothing else about row styling worked either.

## Platform

- **Windows is a stub that returns a loud error from every console operation.**
  The package compiles and cross-compiles cleanly for `windows/amd64` and
  `windows/arm64`, so the packaging works and the runtime does not. **On Windows
  this framework does not currently draw anything.** Linux and macOS are the
  supported platforms.
- **tmux and GNU screen DCS passthrough is missing.** Under tmux on a modern
  terminal, a TermMosaic program can lose key and mouse reporting, because the
  sequences TermMosaic emits are not wrapped for the multiplexer. Deferred with a
  stated trigger: any tmux user reporting broken keys or mouse, or v1.0,
  whichever comes first.

## Input

- **No IME or preedit support.** This is a deliberate deferral, not an oversight,
  and the consequence is worth stating plainly: **composing Japanese, Chinese or
  Korean in a `TextInput` produces *wrong* behaviour rather than degraded
  behaviour.** On most terminals the committed text arrives as a burst of ordinary
  key events, which inserts correctly but pollutes the undo stack with one entry
  per character, so a single Ctrl-Z removes one character instead of the
  composition. The event model reserves `EventCompose` and a `Compose` payload so
  this can be added later as a feature rather than as a rewrite of every widget.
  See [ADR 0005 §7](/adr/0005-input-decoding/). Do not read this as parity with a
  framework that has it, and do not read it as a gap being closed — it is a
  documented decision.
- **Mouse capture is off by default.** Enabling it takes text selection and
  scrollback copying away from the user's shell. That is the default on purpose,
  and the framework has no opinion about your application changing it —
  `examples/markets` opts in and restores the previous mode on exit. Nothing in
  the catalog enables it for you.
- **Focus reporting is off by default**, for the same reason.
- **`form.Tabs` consumes every wheel notch**, whether or not the pointer is over
  it. That is defensible for a form — scrolling a list there does not require
  focus — but in an application it means a tab row early in the focus ring
  swallows every notch, and the panel underneath never sees one.
  `examples/markets` routes the wheel to the widget whose rectangle contains the
  pointer as an **application-level** workaround; **the widget itself is
  unchanged**, and this is still open. It wants an ADR decision, because the fix
  is a policy question — hit-tested or focus-scoped — and not a bug.

## Text and internationalization

- **Wide glyphs and grapheme clusters are handled, but the handling is
  provisional.** A double-width glyph occupies two cells and its continuation cell
  takes its owning span's style, so rows do not flicker — and those paths were
  benchmarked for the first time in v0.1.0 (a full repaint costs 74,139 ns/op
  against the ASCII scene's 74,078, all paths 0 allocs/op). What is **not** done:
  the cell-width table is hand-written from East Asian Width ranges rather than
  generated from Unicode data, so newly assigned wide blocks are wrong until the
  table is updated; and **grapheme clusters are not composed**, so a flag emoji
  renders as two cells' worth of junk and a zero-width-joiner sequence renders as
  several glyphs.
- **The diff's wide-glyph cursor-move overhead was fixed in v0.2.0**, and the fix
  is worth stating as a correction to an earlier entry on this page. The old text
  said the defect was unfixed and out of scope; that was true at v0.1.0 and is no
  longer. Run suppression had assumed one cell per rune, so every wide glyph was
  preceded by a cursor-position escape: **6,000 cursor moves and 68,832 bytes**
  against the narrow scene's 30 moves and 6,233 bytes — about **11×** — for
  identical output. The tracker now advances by the glyph's **cell width**, giving
  **60 moves and 19,443 bytes, 3.12×**. The ASCII path is unchanged at
  **~7,200 ns/op with 0 allocs**, and the benchmark that had pinned the defective
  behaviour now asserts the corrected one.
- **Grapheme clusters are still uncomposed**, so a flag emoji still renders as two
  cells' worth of junk and a zero-width-joiner sequence as several glyphs.
- **`geometry.ClampCount` and `geometry.Budget` count cells, not glyphs**, so a
  row budget computed from them can be one row optimistic once wide characters are
  in play.

## Colour

- **The colour quantiser is unvalidated.** The redmean mapping from truecolor to
  the 256- and 16-colour rungs is implemented and works, but **nobody has checked
  that its output is perceptually acceptable.** Treat the 256 and 16 rungs as
  provisional. The `buffer.Quantiser` interface exists so a Lab-space mapping can
  replace it without touching anything else.
- **`Caps.Unicode` is a proxy, not a probe.** It is the honest one available
  without querying the terminal out of band, and a terminal configured out of
  band will disagree with it.
- **`NO_COLOR` is honoured at encode time**, so no widget path consults the
  environment. Suppressing colour does not suppress attributes — reverse video
  still works, which is why selection and focus survive it.

## Widgets

- **There is no `Form` container widget**, by decision. ADR 0004's solver plus
  `layout` covers composition, and a `Form` type would have been a second way to
  do the same thing. See [Forms](/guides/forms/).
- **`TextArea` has no rendered selection.** It tracks and moves a caret and
  supports editing, but the selected range is not drawn. `TextInput` renders its
  selection; `TextArea` does not. Half a selection is worse than none.
- **`BarChart`'s horizontal category labels were all drawn at absolute column 0**
  until v0.2.0, because `adapt` never set `axisRow`. Inside `Bounds` only for a
  chart at the origin, and a widget writing outside its own rectangle everywhere
  else. Fixed; named here because it is a good illustration of why `Draw` must
  stay inside `Bounds` at all.
- **There is no redo stack**, in either text field.
- **There is no table column selection and no pager selection.** Selection is one
  table row; a `Pager` shows and searches but hands nothing back.
- **No keyboard column selection in `Table`**, no multi-select anywhere, and no
  clipboard integration.
- **`Tree` expansion state is the application's to hold.** Laziness means only
  visible rows are *rendered*; the nodes and the open/closed flags are yours.

## Layout and responsiveness

- **There are no framework breakpoints and no size classes**, by decision in
  [ADR 0007](/adr/0007-responsive-screens/). A size class is a lossy function of
  two numbers and a product decision in the wrong layer. Each widget's threshold
  is a local named constant beside its own `Draw`.
- **No resize has ever been observed against a real terminal being dragged.**
  ADR 0007's drag-resize costs are derived from existing code and from ADR
  0002/0003's measurements. Four of ADR 0007 §3's tests were written for v0.1.0
  and they **found a real defect** — `Render` flushed the sink even when it wrote
  nothing — but a scripted resize sweep is not a human dragging a window.
- **The cache-poisoning debug mode is still not built.** ADR 0007's expensive half
  remains a convention rather than a check: a debug mode that corrupts a widget's
  cache after `Draw` and asserts the next frame is identical would catch that
  whole class of bug instead of leaving it to review.
- **`MinSize()` is an assertion, not enforcement.** The framework does nothing
  with it. What to do when the available space is below it is the application's
  decision, because only the application knows whether losing a table is
  acceptable.

## Theme

- **There is no theme in v1**, and that is a decision with a written trigger, not
  an omission. Widgets carry `Style` fields and the framework's defaults are the
  terminal's own colours plus named attribute styles. The trigger for adding a
  theme is **the first style *role* that two widgets must share.** Until then a
  theme layer would be an abstraction over a concept the catalog does not have.
  [Why, in full](/concepts/no-theme/).

## Still open

- **Kitty graphics protocol in v1, or stay text-only?** Leaning no. Images
  undermine the grid-of-cells assumption the whole renderer rests on. Still open
  because "no" has not been formally decided.
- **Headless backend: v1 or v0.5?** Largely settled — ADR 0001 makes it a v1
  deliverable. The remaining sub-question is its assertion surface: it must
  expose the cell buffer, not just recorded bytes. It does expose the cell
  buffer; whether the surface is complete is open.
- **The width table is hand-written.** Derived from East Asian Width ranges rather
  than generated from Unicode data, so newly assigned wide blocks are wrong until
  it is updated. A benchmark cannot make a table correct.
- **`form.Tabs`' wheel behaviour is undecided.** See
  [Input](#input) above. It wants an ADR.
- **`examples/dashboard` overlaps `examples/markets` and the decision is open.**
  See [Project stage](#project-stage) above.

## This site

- **It is generated, and partly of it is committed.** The widget pages come from
  `scripts/gen_widgets.py`, which merges the framework's `manifest.json`, godoc
  extracted from the Go source, and hand-written prose in
  `data/widget_prose.json`. The captures themselves are framework artefacts,
  copied unmodified. The ADRs are byte-identical to the framework's.
- **Two sections of every widget page cannot be generated** — the example and
  "when not to use it" — and the second is hand-written per widget. A reviewer
  reading a widget page knows exactly which parts to check.
- **No analytics, no cookies, no third-party requests.** Search is Pagefind,
  indexed from the built HTML, and its script is loaded on one page only.
- **If you find an inaccuracy here, that is a bug in this site**, not a matter of
  opinion. Please report it.