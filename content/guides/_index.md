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
  `examples/dashboard`.
- **[Performance](/guides/performance/)** — every measured number on this site,
  and an explicit list of what is *not* measured.
- **[Migrating from another TUI](/guides/migration/)** — what carries over from
  Bubble Tea, Ink or `tcell`, and what does not.

## A note on examples

There are two runnable programs today: `examples/hello` (a bordered,
resize-aware panel) and `examples/dashboard` (list, table, log, meters).

```
go run github.com/serkanalgur/termmosaic/examples/hello@v0.1.0
go run github.com/serkanalgur/termmosaic/examples/dashboard@v0.1.0
```

**The project's `CONTRIBUTING.md` requires a runnable example per widget, and that
requirement is not yet met for all 22.** Where a widget page has no program to
point at, that is the gap — and it is recorded on
[Limitations](/limitations/#project-stage) rather than papered over. Widget pages
carry captured frames instead, and a capture cannot show interaction: see
[Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots).