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

TermMosaic v0.7.0 is tagged and released, so pin the version:

```
go get github.com/serkanalgur/termmosaic@v0.7.0
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
go run github.com/serkanalgur/termmosaic/examples/hello@v0.7.0
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
go run github.com/serkanalgur/termmosaic/examples/markets@v0.7.0
```

That is a live finance dashboard — ECB rates from Frankfurter, crypto from
CoinGecko, **no API key and nothing to sign up for**. It fetches on its own
goroutine and needs outbound HTTPS. If you have no network, or want a
deterministic run, use `--offline`:

```
go run github.com/serkanalgur/termmosaic/examples/markets@v0.7.0 --offline
```

`q` quits, `r` refetches immediately, `?` opens the help overlay, and the wheel
and mouse work on the panels.

Then the newest one:

```
go run github.com/serkanalgur/termmosaic/examples/search@v0.7.0
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

This is deliberate in shape and unfinished in fact. Committing to owning the
terminal layer (ADR 0001) means Windows console mode flags are TermMosaic's
problem rather than a library's. The packaging half of that risk is closed:
cross-compilation to `windows/amd64` and `windows/arm64` is verified in CI. The
runtime half — an actual console backend — is open, and `docs/STATUS.md` records
it as a v1.0 risk.

## Under tmux or GNU screen

**DCS passthrough is not implemented.** Under tmux on a modern terminal, a
TermMosaic program can lose key and mouse reporting, because the sequences
TermMosaic emits are not wrapped for the multiplexer.

This is deferred with a stated trigger — any tmux user reporting broken keys or
mouse, or v1.0, whichever comes first. It is a real gap, not a caveat: if you
develop under tmux, test in a plain terminal before concluding the library is
broken. See [ADR 0005 §10](/adr/0005-input-decoding/) and
[Limitations](/limitations/#platform).

## What "released" means here

- **v0.7.0 is tagged and the module resolves.** `go get …@v0.7.0` works.
- **The API is not stable.** Every release before v1.0.0 is a pre-release, and a
  minor version **may contain behavioural changes**. What is promised: **no
  behavioural change in a patch release.** If v0.1.1 changes behaviour, that is a
  bug in the release, not policy.
- **Anything marked PROPOSED may change or be reversed.** The colour model is
  PROPOSED — built and working, but its 256- and 16-colour rungs have never been
  checked by a human eye.

The full statement is on [Limitations](/limitations/). Read it before you commit
to this in anything you care about.

## Next

- **[Quickstart](/getting-started/quickstart/)** — one annotated file.
- **[Your first app](/getting-started/your-first-app/)** — the loop, end to end.