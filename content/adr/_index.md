---
title: "Architecture decisions"
description: "The ten ADRs, verbatim — what was decided, what was rejected, and why."
weight: 70
---

# Architecture Decision Records

TermMosaic's architecture decisions are recorded here as ADRs. Each is a dated
document that states what was decided, what was rejected, and why.

**An ADR is not deleted when it stops being true.** If a decision is reversed, the
original stays and a new one supersedes it, so the reasoning history survives.
That is why ADR 0008 is 60 KB and ADR 0005 is 50 KB: they carry the evidence,
including the parts that did not work out.

## These are verbatim

**The ten pages below are the framework's own files, copied byte for byte.**
They are not summaries, because a summary is a second source of truth that drifts
— and a decision record that disagrees with itself is worse than none. The only
edit is the removal of each file's own `# Title` heading, since the site renders
the title from front matter and would otherwise emit two `<h1>`s.

One piece of plumbing: sibling `.md` links inside the ADRs are rewritten to point
at the corresponding page here, by a Hugo link render hook. That is the reason you
can click from ADR 0005 to ADR 0007 and land on a page.

If you want the originals:
[`docs/adr/`](https://github.com/serkanalgur/termmosaic/tree/main/docs/adr).

## Index

| # | Title | Status | Date |
|---|---|---|---|
| [0001](/adr/0001-backend-strategy/) | [Backend strategy](/adr/0001-backend-strategy/) | Accepted | 2026-10-03 |
| [0002](/adr/0002-buffer-representation/) | [Cell buffer representation](/adr/0002-buffer-representation/) | Accepted | 2026-10-03 |
| [0003](/adr/0003-renderer-mode/) | [Renderer mode](/adr/0003-renderer-mode/) | Accepted | 2026-10-03 |
| [0004](/adr/0004-layout-engine/) | [Layout engine](/adr/0004-layout-engine/) | Accepted | 2026-10-03 |
| [0005](/adr/0005-input-decoding/) | [Input decoding](/adr/0005-input-decoding/) | Accepted | 2026-10-04 |
| [0006](/adr/0006-subbuffer-cell-access/) | [Sub-buffer cell access](/adr/0006-subbuffer-cell-access/) | Accepted | 2026-10-04 |
| [0007](/adr/0007-responsive-screens/) | [Responsive screens](/adr/0007-responsive-screens/) | Accepted | 2026-10-04 |
| [0008](/adr/0008-style-and-text/) | [Style, theme and text](/adr/0008-style-and-text/) | Accepted | 2026-10-04 |
| [0009](/adr/0009-command-and-keymap/) | [Commands and keymap](/adr/0009-command-and-keymap/) | Accepted | 2026-10-05 |
| [0010](/adr/0010-mouse-routing/) | [Mouse routing](/adr/0010-mouse-routing/) | Accepted | 2026-10-05 |

## Decisions at a glance

- **0001 — Backend: pluggable, own the core.** Two narrow interfaces
  (`Terminal`, `Sink`) with a direct `golang.org/x/sys` implementation and a
  headless memory sink. We wrap **no** terminal library. The evidence that
  settled it: `tcell`'s flush costs 280,814 ns/op on a one-row-dirty workload
  where our two-tier diff costs 7,133 ns/op, and `tcell`'s headless backend
  cannot expose the cell buffer that widget tests need.

- **0002 — Buffer: AoS with a padding-free 16-byte `Cell`.** This **overturned
  the previous leaning toward struct-of-arrays.** OpenTUI's SoA row-skip
  advantage is a Zig `mem.eql` advantage and does not transfer to Go: the
  packed AoS row skip *ties* with SoA (5,373 vs 5,128 ns/op) and is 4.4×
  *faster* when every row is dirty (147.2 vs 636.7 ns/op), because it is one
  wide memcmp instead of four. A two-tier diff on a 200×60 scene writes ~141×
  fewer bytes than a full repaint. Byte-wise row comparison additionally
  requires the compared range to be **contiguous**, not just `Cell` to be
  padding-free — see the 2026-10-04 amendment.

- **0003 — Renderer: hybrid.** A retained widget tree invalidated by rectangle,
  with widgets describing themselves on demand. No reconciler, no Elm loop.
  Static chrome is cheap because of the diff, not because of the renderer mode.

- **0004 — Layout: constraint-based, own solver.**
  `Length`/`Min`/`Max`/`Percentage`/`Ratio`/`Fill`, matching what Bubble Tea users
  already know. `Fill` is **order-insensitive** — a deliberate, tested divergence
  from tmux's priority-ordered rule. Flexbox via Yoga was rejected because
  **cgo breaks `CGO_ENABLED=0` cross-compilation**, contradicting the
  single-static-binary goal.

- **0005 — Input: a pure decoder under a resumable driver, in a new `input`
  package.** `Decode(seq []byte, cfg Config) (Event, int, Status)` is pure, so
  the worst input bug — a sequence split across two `read(2)` calls — is a
  one-line table-driven test rather than a flaky timing test. A `Parser` holds
  only the unavoidable bytes, and a `Source` merges input and resize into one
  ordered stream. Scope verdicts: **kitty keyboard IN** (progressive
  enhancement, request only `disambiguate`, 100 ms bounded probe); **paste IN**
  and always **one `EventPaste` carrying the whole payload**, never a stream;
  **mouse decoding IN** (SGR 1006, urxvt 1015, X10) but **capture OFF by
  default** because it steals selection and scrollback from the user's shell;
  **focus decoding IN**, reporting OFF by default; **IME DEFERRED and scoped
  out**, with `EventCompose` and a `Compose` payload field reserved so it is a
  later feature rather than a rewrite.

- **0006 — Cell access: a row accessor, not a flat slice.** `Buffer.Cells()`
  is **removed**. It returns the flat backing slice, whose index
  `y*Width()+x` is silently wrong for a sub-buffer — the same unsoundness ADR
  0002 fixed once already, in `SubBuffer`, left open at a different door. It
  is replaced by `Row(y) []Cell`, which is correct on top-level buffers and views
  alike because the stride never leaves the `buffer` package. `RowBytes` becomes
  a `*Buffer` method that **panics on a sub-buffer** — settling ADR 0002's v1.0
  risk item 1b now rather than at v1.0 — and `diff.Frame` carries
  `*buffer.Buffer` instead of `[]buffer.Cell`, so the "diff only top-level
  buffers" rule is enforced by a type rather than by a doc comment. `Stride()` is
  deliberately not exported.

- **0007 — Responsive screens: a budget, not a reflow.** There are **no size
  classes and no framework breakpoints** — a size class is a lossy function of
  two numbers and a product decision in the wrong layer, and every threshold a
  widget needs is a local named constant beside its own `Draw`. What the
  framework shares is the *arithmetic*: `geometry.ClampCount(n, available)`,
  `geometry.Budget(regions, available)` with a four-value `Priority` scale, and
  an optional `termmosaic.Minimizable` interface declaring a widget's smallest
  meaningful size. Policy stays per widget; safety and arithmetic are shared.
  The **`Widget` interface is unchanged** — the space is already reachable from
  `Bounds()`, and adaptation is lazy and self-detecting (a widget re-derives
  anything size-derived when `Bounds()` differs), which beats a fourth mandatory
  method precisely because a widget cannot forget it. **Degenerate sizes are a
  decided contract: no panic, ever; clip, never blank** — below `MinSize()` a
  widget draws its minimum layout clipped, and 0×0 is a valid size that writes
  zero bytes. A resize always repaints the whole screen, because
  `buffer.Resize` discards the cells a partial diff would need; and drag-resize
  coalescing is **free**, because an app that calls `r.Resize` per event and
  lets the pacer decide when to paint already gets it. **Amended 2026-10-04:**
  the rect is not the only thing a size-derived cache depends on. A widget that
  caches column widths on `Bounds()` and is then handed `Header = true` renders
  the old layout *permanently* — nothing will produce a different rect to
  repair it. So `Invalidate()` now also means **drop every value the widget has
  cached**, and a widget exposing a setter for anything `Draw` reads must
  invalidate in that setter.

- **0008 — Style, theme, and text: one `Style` value, one `Span` type, one
  border vocabulary, and deliberately no theme in v1.** `buffer.Style` bundles
  fg/bg/attr and is passed **by value** — 12 bytes, three registers, no
  allocation, so it costs exactly what the three loose arguments it replaces cost
  and keeps ADR 0002's 0-allocs frame path. It lives in `buffer` because
  `geometry` cannot hold it without an import cycle (`buffer` imports
  `geometry`; `Style` needs `Colour`), which is the same cycle-exclusion
  reasoning that put ADR 0007's vocabulary in the leaf. Styled text goes through
  `Span` + `Buffer.SetSpans`, whose load-bearing rule is that **a wide glyph's
  continuation cell takes its owning span's style** — a mismatched one never
  compares equal and flickers that row forever. `Wrap`/`Truncate` **allocate
  and are therefore never called from `Draw`**; they are built on the
  size-change check ADR 0007 §3 already established. **There is no theme in
  v1**: widgets carry `Style` fields, the framework's defaults are the terminal's
  own colours plus named attribute styles, and a theme is triggered by the first
  role two widgets must share. Borders are one set of names —
  `BorderPlain`/`Rounded`/`Double`/`Thick`/`ASCII` — with the glyph tables in
  `buffer` and one `Block` as the only thing in the catalog that draws one.

- **0009 — Commands and keymap: a named action, and a key as one way to reach
  it. Implemented in v0.6.0; no palette.** Read
  [ADR 0009](/adr/0009-command-and-keymap/) for the reasoning. The `keymap`
  package shipped — named commands, a 16-byte comparable `Chord`, and resolution
  by context specificity (**focus, then screen, then global, with no numeric
  priority**) at 0 allocs/op — and `Widget` is byte-identical, so nothing you
  wrote breaks. **What has not shipped:** the `Ctrl+K` palette UI that ADR 0009
  §9 deliberately scopes out; the optional `Commandable`/`Clickable` interfaces,
  which **no catalog widget implements**; and `Registry.SetFocus`, so
  `Describe(ScopeFocus)` is over-inclusive rather than incomplete. A key the
  keymap consumes shadows a widget's own `switch` and **the registry cannot
  report that overlap** — it is told a widget's bounds and published chords,
  never what its `Handle` does. See
  [Limitations](/limitations/#v060-keymap--a-new-package-and-nothing-you-wrote-breaks).

- **0010 — Mouse routing: widgets hit-test themselves.** One sentence — **a
  widget handles a pointer event only if the pointer is inside its `Bounds()`** —
  and it covers every `Mouse` action, wheel included. The alternative considered
  and rejected is a framework routing helper (`RouteMouse(root, ev) Widget`, or an
  optional `Hittable` interface): it is new exported API against a `Widget` that
  ADR 0007 and ADR 0009 both freeze, it needs a tree walk that `Widget` cannot
  express because there is no `Children()`, and it can only answer "which rect"
  where a widget can answer "which cell means what". So the fix is three call
  sites and one shared helper. The defect was real and not cosmetic: `form.Tabs`,
  first in `examples/markets`' focus ring, consumed **every wheel notch in the
  application** whether or not the pointer was over it. **Two exemptions are
  stated rather than left implicit**: a release ends a drag wherever the pointer
  is, and a drag continues outside `Bounds` once a press has claimed it.

## Still open

- **Kitty graphics protocol in v1, or stay text-only?** Leaning no. Images
  undermine the grid-of-cells assumption the whole renderer rests on, and the
  feature is not in the widget catalog.
- **Headless backend: v1 or v0.5?** Largely settled by ADR 0001; the remaining
  sub-question is its assertion surface.
- **Windows console support.** ADR 0001 commits to owning the terminal layer,
  which makes console mode flags our problem. The packaging half is closed —
  `CGO_ENABLED=0` builds are verified for `windows` and `linux/arm64` — and the
  runtime half is a **stub that returns a loud error**. At v1.0.0 this was
  narrowed from "risk" to **decision**: Windows is out of scope for v1.0.0, the
  supported platforms are Linux and macOS, and the Windows CI test leg was
  dropped (the cross-compile legs remain).
- **`widgets/widgettest`'s compatibility promise.** It is public, so v1.0.0's
  stability promise covers it by default — the release notes do not exclude it.
  Whether that surface *should* be frozen is **undecided**: `docs/STATUS.md`
  names two options (promote it to a decided surface, or move it under
  `internal/`) and picks neither.
- **The cache-poisoning debug mode is built, and it found eight stale caches.**
  It shipped in v0.5.0 as ADR 0007 §3's deferred "expensive half", and
  `widgets/cacheaudit` fails the build on a finding. What it does *not* cover is
  every exported raw field — the gate covers the transitions it names, and several
  same-shaped fields are not named by any.
- **The colour model is no longer open.** It moved **PROPOSED → DECIDED on
  measurement** at v1.0.0 (2026-10-06): PR #18's CIEDE2000 audit found the
  redmean weights inert and PR #19 replaced the quantiser through the
  `buffer.Quantiser` hook. An earlier entry on this page recorded that
  `docs/adr/README.md`'s open list disagreed with `docs/STATUS.md` on this —
  the framework's README has since been corrected, and both now record the
  model as decided. The record of what was wrong is kept in the audit's own
  source rather than erased.

Full detail is in
[`docs/STATUS.md`](https://github.com/serkanalgur/termmosaic/blob/main/docs/STATUS.md).