---
title: "Data display"
description: "Choosing between List, Table, Tree and Pager, and the traps each one has."
weight: 53
toc: true
---

# Data display

Four data widgets: [`List`](/widgets/list/), [`Table`](/widgets/table/),
[`Tree`](/widgets/tree/), [`Pager`](/widgets/pager/). They share a
virtualization engine and a focus contract, and each has a trap.

## Choosing

| Your data | Widget |
|---|---|
| One string per row | [`List`](/widgets/list/) |
| Rows in columns, with a header | [`Table`](/widgets/table/) |
| Nested, with expandable nodes | [`Tree`](/widgets/tree/) |
| Long text to read, with search | [`Pager`](/widgets/pager/) |

If two rows apply, pick on this order: **is it nested? → `Tree`. Does it have more
than one field? → `Table`. Is it prose? → `Pager`. Otherwise → `List`.**

## The shared contract

All four are `Focusable` on the same terms: **keys are consumed only while
focused**, and a press inside the rectangle takes focus as well as selecting, so
a click is a complete interaction without you writing a click handler.

All four render only the visible rows. See
[Virtualization](/concepts/virtualization/).

## `List`

{{< widget-capture "list" >}}

**The trap:** a `ListItem` is one string. Two or more columns is a `Table`, and
bolting a fixed-width formatter onto list items is how you get a table that cannot
scroll horizontally and misaligns on a wide glyph.

**The number that matters**, and it is measured:

| Items | `List` | `Table` |
|---|---|---|
| 10,000 | 13,320 ns | 16,801 ns |
| 100,000 | 14,242 ns | 17,885 ns |

Ten times the data for seven percent more time, at zero allocations. But it is
per-**frame** cost: **mutating the item list invalidates**, and doing that every
frame is a different cost from drawing.

## `Table`

{{< widget-capture "table" >}}

**Three traps, all of which will look like bugs:**

1. **Column widths are computed from content and available space.** A column
   holding a widget, a multi-line cell, or anything with its own alignment is a
   composition problem — render that cell yourself and pass a string.
2. **Scrolling to the end leaves a column partially visible.** `Table` keeps two
   horizontal offsets, and `clampColOffset`'s ceiling is the content's
   right-hand edge, which is generally not a column start. This is deliberate and
   tested. A resize that changes `contentW` or `totalW` re-clamps onto the same
   ceiling, **so the partial column can appear with no scrolling key pressed at
   all.**
3. **There is no column selection in v0.3.0.** Selection is one row.

**One amendment trap:** `Header` is a plain field, and toggling it invalidates.
That matters because a widget that caches column widths on `Bounds()` and is
handed `Header = true` would render the old layout **permanently** — nothing will
produce a different rect to repair it. `Table` obeys the rule; if you write a
similar widget, see [Responsiveness](/concepts/responsiveness/).

## `Tree`

{{< widget-capture "tree" >}}

**Two traps:**

- **Laziness is about rendering, not about your data.** Only visible rows are
  rendered; the nodes and the open/closed flags are yours. **A tree over a
  filesystem you have not walked is a tree over nothing.**
- **Expansion state is yours.** There is no tree controller holding it.

And the documentation trap: **expansion is state, and a still frame shows it only
as twisties and indentation.** The capture above cannot show you what expanding a
node looks like. That is why the plain-text capture sits beside every colour one
— see [Limitations](/limitations/#captures-are-cell-grids-not-terminal-screenshots).

## `Pager`

{{< widget-capture "pager" >}}

**It is read-only by construction.** It cannot be edited, deliberately: a pager
that accepted keystrokes would need a caret, a selection and an undo history to
be worth having. Editing long text is [`TextArea`](/widgets/textarea/), with the
caveat that it has no rendered selection in v0.3.0.

**Search is a key contract, not a live filter.** You set the query, the pager
highlights matches and reports the count in its status line, and moving between
them is a key. Search-as-you-type means building it yourself.

**There is no pager selection in v0.3.0.** It shows and searches; it hands nothing
back. If you need the user to pick a line, that is a different design and you
should expect to build it.

## Master/detail

Two panes with a list driving a detail view is [`Split`](/widgets/split/):

```go
split.New(layout.DirectionRow, list, detail)
```

Both panes are focusable, Tab moves between them, and the focused pane is the one
that takes keys. The `Split` capture shows the focused pane's marker in the second
pane's title — and note that a still frame **cannot show the Tab that got you
there**.

{{< widget-capture "split" >}}

## Numbers beside names

When the number is the point, print it. Every widget here truncates or marks a
value too wide rather than letting it bleed into the frame, and
[`BarChart`](/widgets/barchart/) puts each value beside each bar precisely
because bar colour alone is not a reading.

See [Dashboards](/guides/dashboards/) for putting several of these on one screen.

## Reading next

- [Virtualization](/concepts/virtualization/) — what the flat-cost claim does and
  does not cover.
- [Dashboards](/guides/dashboards/) — composing these into a screen.
- [`List`](/widgets/list/), [`Table`](/widgets/table/), [`Tree`](/widgets/tree/),
  [`Pager`](/widgets/pager/) — each with its full key contract and its "when not
  to use it".