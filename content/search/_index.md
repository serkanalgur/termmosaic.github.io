---
title: "Search"
description: "Full-text search over every page of this site. Indexed by Pagefind from the built HTML."
weight: 99
sitemap:
  exclude: true
---

# Search

Search covers every page of this site — the widget pages, the concepts, the
guides and the eight ADRs. The index is built by
[Pagefind](https://pagefind.app/) from the rendered HTML after Hugo runs, so it
never disagrees with what is on the page.

{{< pagefind >}}

**If search returns nothing,** use the navigation in the sidebar. Every page is
reachable from [the start page]({{ "/" | relURL }}) without search.

## What search covers, and what it does not

- **It covers the prose.** Widget summaries, key contracts, the concepts, and
  the full text of all eight ADRs.
- **It covers widget pages**, including their "when not to use it" sections,
  which are the parts most likely to answer the question you arrived with.
- **The captures are not searchable.** A cell grid is a grid of characters to a
  text index, and indexing it would fill every widget's results with box-drawing
  runes. The widget's *name*, *package*, *constructor* and *summary* are
  indexed, which is what you would search for anyway.

This page is the only page on the site that loads any JavaScript. Everything else
is static HTML and CSS.