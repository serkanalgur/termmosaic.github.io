---
title: "Guides"
description: "Composition, forms, data display, dashboards, performance and migration — task-shaped rather than widget-shaped."
weight: 50
---

# Guides

The widget pages are organised by widget. These six are organised by **task**,
because most of the time you are not looking up "what does `Split` do" — you are
working out how to build something.

- **[Composing with Block](/guides/composing/)** — borders, padding, and solving a
  layout against `Block.Interior()` so your content stops knowing a border exists.
- **[Forms](/guides/forms/)** — the nine form widgets as one workflow. Focus,
  layout, validation, and why there is no `Form` container.
- **[Data display](/guides/data-display/)** — choosing between `List`, `Table`,
  `Tree` and `Pager`.
- **[Dashboards](/guides/dashboards/)** — building a real screen, walking through
  `examples/markets`.
- **[Performance](/guides/performance/)** — every measured number on this site,
  and an explicit list of what is *not* measured.
- **[Migrating from another TUI](/guides/migration/)** — what carries over from
  Bubble Tea, Ink or `tcell`, and what does not.

## A note on examples

There are three runnable programs today. The two to start with:

```
go run github.com/serkanalgur/termmosaic/examples/markets@v0.4.0   # live finance dashboard
go run github.com/serkanalgur/termmosaic/examples/hello@v0.4.0     # bordered panel, focus ring
```

`markets` needs no API key and takes `--offline` for bundled sample data. Both are
keyboard- and mouse-driven; press `?` in either for its key list.

> `examples/dashboard` also still exists and **overlaps `markets`**. Whether to
> keep it or retire it is **undecided**, so the guides point at `markets` and do
> not present the two as equally recommended. It has not been removed.

**The project's `CONTRIBUTING.md` requires a runnable example per widget, and that
requirement is not yet met for all 24.** Where a widget page has no program to
point at, that is the gap — and it is recorded on
[Limitations](/limitations/#project-stage) rather than papered over. Widget pages
carry captured frames instead, and a capture cannot show interaction: see
[Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots).