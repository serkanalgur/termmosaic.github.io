---
title: "Install"
description: "Go 1.23+, CGO off, two dependencies, and what is and is not released."
weight: 11
---

# Install

## Requirements

| | |
|---|---|
| **Go** | **1.23 or newer** — matches current stable |
| **cgo** | **Not used.** `CGO_ENABLED=0` builds are verified in CI for `linux/amd64`, `linux/arm64`, `darwin/amd64`, `darwin/arm64`, `windows/amd64`, `windows/arm64` |
| **Dependencies** | `golang.org/x/sys` and `golang.org/x/term`. That is all of them. |
| **Terminal library** | **None.** TermMosaic wraps no `tcell`, no Bubble Tea, no Textual. It owns the terminal layer through two small interfaces — see [ADR 0001](/adr/0001-backend-strategy/). |
| **Platforms that work** | **Linux and macOS.** |

## Get it

TermMosaic v1.0.0 is tagged and released, so pin the version:

```
go get github.com/serkanalgur/termmosaic@v1.0.0
```

**Prefer to work from a checkout?** That works too, and it is how the framework's
own CI builds:

```
git clone https://github.com/serkanalgur/termmosaic
cd termmosaic
go build ./...
go test ./...
```

## Check that it built

```
go run github.com/serkanalgur/termmosaic/examples/hello@v1.0.0
```

You should get a bordered panel titled `termmosaic` showing a live frame counter,
the negotiated colour depth and a focus ring. `Tab` moves focus, `?` opens the
help overlay, and `q`, Escape or Ctrl-C leaves. The panel now spans the terminal
and re-arranges itself as you resize; below 38×8 it says so in one line rather
than clipping.

**If `hello` prints "stdout is not a terminal"**, that is the example behaving
correctly rather than a failure: it checks before it draws, so it stays runnable
under redirection and in CI. Run it in a real terminal, or run the golden test
with `go test ./examples/hello/`.

Then try the more useful one:

```
go run github.com/serkanalgur/termmosaic/examples/markets@v1.0.0
```

That is a live finance dashboard — ECB rates from Frankfurter, crypto from
CoinGecko, **no API key and nothing to sign up for**. It fetches on its own
goroutine and needs outbound HTTPS. If you have no network, or want a
deterministic run, use `--offline`:

```
go run github.com/serkanalgur/termmosaic/examples/markets@v1.0.0 --offline
```

`q` quits, `r` refetches immediately, `?` opens the help overlay, and the wheel
and mouse work on the panels.

Then the newest one:

```
go run github.com/serkanalgur/termmosaic/examples/search@v1.0.0
```

That is a search-and-results screen on **real Wikipedia data** — no API key,
nothing to sign up for — with a `form.TextInput` query field, a `data.Table` of
results and a detail pane. `--offline` runs the whole screen on a transcribed
capture, so it works with no network at all. It is also the **first example with
a focusable widget in the focus ring**, which is what makes it the interesting
one to read: everything else proves a widget draws and a screen routes keys.

## Windows

**TermMosaic compiles for Windows and does not currently run there.** The
Windows backend is a stub that returns a loud error from every console
operation — it will not silently draw nonsense, it will tell you it cannot.

This is deliberate, and at v1.0.0 it is decided rather than merely unfinished:
**Windows is out of scope for v1.0.0** (ADR 0001, platform decision recorded
2026-10-05). Committing to owning the terminal layer means Windows console mode
flags are TermMosaic's problem rather than a library's. The packaging half is
closed: cross-compilation to `windows/amd64` and `windows/arm64` is still
verified in CI. The runtime half — an actual console backend — is not built and
is not promised for any particular release.

## Under tmux or GNU screen

**DCS passthrough is not implemented.** Under tmux on a modern terminal, a
TermMosaic program can lose key and mouse reporting, because the sequences
TermMosaic emits are not wrapped for the multiplexer.

This is deferred with a stated trigger — any tmux user reporting broken keys or
mouse, or v1.0, whichever comes first. **The v1.0 half of that trigger has
arrived and the gap remains** — still deferred, still real. It is not a caveat:
if you develop under tmux, test in a plain terminal before concluding the
library is broken. See [ADR 0005 §10](/adr/0005-input-decoding/) and
[Limitations](/limitations/#platform).

## What "released" means here

- **v1.0.0 is tagged and the module resolves.** `go get …@v1.0.0` works.
- **v1.0.0 is the first release that makes a stability promise.** The public API
  freezes there and Semantic Versioning applies in earnest: a behaviour change
  means a minor, not a quiet patch — with one documented exception:
  `widgets/widgettest`, the test harness, is excluded from that promise,
  because it must evolve with the framework. Every release before v1.0.0 was a
  pre-release under a break-without-notice policy. One honesty note the release
  carries itself: the gate's SemVer criterion is recorded **PARTIALLY MET**,
  because v0.5.1, v0.5.2 and v0.6.1 were patch numbers that carried behaviour
  changes — the promise starts at v1.0.0 and is not retroactive.
- **The colour model is DECIDED, not PROPOSED.** It moved to DECIDED on
  measurement at v1.0.0: the 256- and 16-colour rungs now select in Lab space
  (CIEDE2000), with selection error 0.000 on both rungs. This is a **behaviour
  change** — the bytes a program emits at those rungs differ from v0.7.x.
- **Anything else marked PROPOSED may still change or be reversed.** See the
  decision table in
  [`docs/STATUS.md`](https://github.com/serkanalgur/termmosaic/blob/main/docs/STATUS.md).

The full statement is on [Limitations](/limitations/). Read it before you commit
to this in anything you care about.

## Next

- **[Quickstart](/getting-started/quickstart/)** — one annotated file.
- **[Your first app](/getting-started/your-first-app/)** — the loop, end to end.