---
title: "Getting started"
description: "Three pages: install it, run a program in one file, then build a real application end to end."
weight: 10
---

# Getting started

Three pages, in order. About fifteen minutes in total, and the third one is the
one that matters — a TUI is not a library call, it is a loop you own, and the
loop is where the design decisions show up.

1. **[Install](/getting-started/install/)** — Go 1.23+, `CGO_ENABLED=0`, and what
   is and is not released yet.
2. **[Quickstart](/getting-started/quickstart/)** — one file, a bordered panel
   that survives a resize, annotated line by line.
3. **[Your first app](/getting-started/your-first-app/)** — terminal, renderer,
   input, and a frame loop, end to end, with the failure modes named.

Before any of it: **TermMosaic is pre-alpha and the API will break without notice
until v1.0.0.** See [Limitations](/limitations/). If you are evaluating it rather
than adopting it, that page is the thing to read first — it is short, specific,
and lists what does not work.

## What you need

- **Go 1.23 or newer.** Nothing else. No cgo, no C compiler, no Node.
- **A terminal.** Linux and macOS. **Windows compiles but does not run** — the
  Windows backend is a stub that returns a loud error from every console
  operation.
- **Two dependencies**, both `golang.org/x`: `golang.org/x/sys` and
  `golang.org/x/term`.

## The examples

```
go run github.com/serkanalgur/termmosaic/examples/markets@v0.4.0   # live finance dashboard, no API key
go run github.com/serkanalgur/termmosaic/examples/hello@v0.4.0     # bordered panel, focus ring, ? help
```

`markets` is the more useful of the two to read: it is a real screen built out of
the catalog, fed by real network data, and [Dashboards](/guides/dashboards/) walks
through how. It takes `--offline` to run on bundled sample data if you have no
network.

**Both are keyboard- and mouse-driven.** Press `?` in either for its key list.

> `examples/dashboard` also still exists and overlaps `markets`. Whether to keep
> it or retire it is **undecided** — start with `markets`.

## Then

- **[Concepts](/concepts/)** — the twelve ideas. Start with
  [Renderer and diff](/concepts/renderer/) and
  [Widgets and focus](/concepts/widgets-and-focus/).
- **[Widgets](/widgets/)** — all 24, with a captured frame each.
- **[Architecture decisions](/adr/)** — the nine ADRs, verbatim, if you want
  the reasoning rather than the how.