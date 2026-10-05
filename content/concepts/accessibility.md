---
title: "Accessibility"
description: "Colour is never the only signal — what the catalog provides, and what it structurally cannot."
weight: 30
toc: true
---

# Accessibility

One of TermMosaic's seven design pillars, and the one with the sharpest limits.
This page states both halves: what the catalog actually does, and what a grid of
cells makes impossible.

## The rule

> **Colour is never the only signal.**

In `widgets/viz` this is a **hard requirement rather than a nicety**, and the
package's godoc gives the reason: *a bar chart whose only distinction between
"fine" and "critical" is a hue is unreadable to a colour-blind reader and to every
monochrome terminal.*

The way it is honoured is the same everywhere: **every distinction has a second
representation that is a glyph, an attribute, or a number.**

## The non-colour signals, widget by widget

| Widget | The signal that is not colour |
|---|---|
| [`Button`](/widgets/button/) | Focus is a **shape**: `[Save]` ringed while focused, ` Save ` padded while not. Both rings are the same width, so focus cannot reflow a form. |
| [`Checkbox`](/widgets/checkbox/) | Three **marks** — empty box, cross inside, dash for indeterminate. Three states, three glyphs. |
| [`Radio`](/widgets/radio/), [`Select`](/widgets/select/) | The selection is a marker and reverse video. `SelectedStyle` unset means reverse video. |
| [`TextInput`](/widgets/textinput/), [`TextArea`](/widgets/textarea/) | Caret, selection (reverse video), and focus as a shape. |
| [`List`](/widgets/list/), [`Table`](/widgets/table/), [`Tree`](/widgets/tree/) | The marker gutter glyph beside the selected row. |
| [`List`](/widgets/list/)'s scrollbar | The thumb's **position**. Never its colour. |
| [`Tree`](/widgets/tree/) | Open and closed are **different twisty glyphs**, plus indentation. |
| [`ProgressBar`](/widgets/progressbar/) | The fill character differs from the track character, **and** fill and track styles differ by attribute as well as colour. |
| [`Gauge`](/widgets/gauge/) | `ShowValue` prints the number as digits. Braille gives ~8 levels per cell; the dial tells you *roughly where*, the digits tell you *how much*. |
| [`Meter`](/widgets/meter/) | **Three** non-colour signals: zone boundaries are `+`, the threshold is `|`, and the active band is **named in text**. |
| [`Sparkline`](/widgets/sparkline/) | The threshold defaults to **reverse video**, an attribute rather than a colour, and the last sample is marked distinctly. |
| [`BarChart`](/widgets/barchart/) | Every bar carries its **value as text** beside it. |
| [`KeyHint`](/widgets/keyhint/) | Key names are words. |

## Why attributes are the load-bearing part

**`NO_COLOR` suppresses colour. It does not suppress attributes.** So anything
expressed as reverse video, bold or dim survives a `NO_COLOR` terminal, a
monochrome terminal, and a colour-blind reader alike.

That is why "unset means `AttrReverse`" is the framework's default for
`SelectedStyle` and `FocusStyle` rather than "unset means a highlighted blue": it
is the difference between a default that degrades and a default that disappears.

It is also why the framework **ships no colours at all** — see
[No theme, and why](/concepts/no-theme/). An unset style resolves to the
**terminal's own colours**, so a framework default cannot override the user's
contrast settings or their colour scheme.

## Keyboard operation

**Full keyboard operation** is a design pillar, and the key contracts on each
widget page are part of the contract rather than documentation of an
implementation. Three things make it work:

- **Focus is always visible**, by shape rather than by colour (see `Button`).
- **Widgets consume keys only while focused**, so an unfocused widget cannot
  swallow input meant for the tree.
- **A disabled widget consumes nothing** — not a click, not a key. `Button` does
  this deliberately so an action can be disabled without removing the widget.

Two honest gaps: **`TextArea` has no rendered selection** in v0.2.0 (it tracks
and moves a caret and supports editing, but the selected range is not drawn), and
there is **no redo stack** in either text field.

## What a terminal grid cannot provide

This is the part that is easy to overclaim, so it is stated plainly.

**There is no accessibility tree.** A terminal is a grid of cells on a screen.
There is nothing for a screen reader to traverse, and no way to attach a label,
a role or a value to a particular cell. So:

- **A `TextInput` has no accessible name.** The label is your responsibility,
  drawn as cells next to the field. `Placeholder` is a placeholder and not a
  label: it disappears on the first keystroke, which is exactly when a user
  filling in a form most needs to know what the field was for.
- **There is no live region.** A `Meter` cannot announce that it crossed its
  threshold. The value has to be on screen and readable.
- **There is no per-cell contrast checking.** Contrast between a foreground and a
  background the *application* chose is the application's responsibility. The
  framework can only decline to have an opinion.

## There is no reduced-motion gate

**A reduced-motion flag is not built**, and the reason is stated rather than
dodged: **the catalog animates nothing today, so there is nothing to gate.**

That is a real reason and it is also a temporary state. If a widget ever
animates — a spinner, a progress tween — a `prefers-reduced-motion`-equivalent
has to arrive with it, and at that point the omission stops being harmless. It
is listed in [Limitations](/limitations/#theme) alongside the theme decision as
the kind of thing that is not a feature gap being closed but a boundary that has
not been tested against yet.

## Where the numbers come from

Nothing on this site claims an accessibility conformance level, and that is
deliberate. **There is no WCAG conformance claim for a terminal grid** — the
guidelines assume a DOM, focus rings in a browser's tab order, and semantic
elements, and none of those exist here.

What can be claimed is arithmetic: every distinction listed in the table above
survives with colour suppressed. That is checkable, and it is what the widget
tests and this site's own captures check.

## Reading next

- [Styling and spans](/concepts/styling/) — `AttrReverse` and the other
  attributes.
- [Degradation and NO_COLOR](/concepts/degradation/) — the encode-time
  mechanism.
- [`Meter`](/widgets/meter/) — the widget with three non-colour signals.
- [Limitations](/limitations/) — the accessibility gaps, including
  `TextArea`'s selection.