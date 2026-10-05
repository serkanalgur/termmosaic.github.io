---
title: "Menu"
weight: 23
description: "A navigable menu with nested submenus to arbitrary depth."
widgetName: "Menu"
widgetPackage: "widgets/menu"
widgetConstructor: "menu.New(r buffer.Rect, items ...menu.Item) *menu.Menu"
capture: "menu"
---

A navigable menu with nested submenus to arbitrary depth.

Package `widgets/menu`. API reference: [pkg.go.dev/widgets/menu](https://pkg.go.dev/github.com/serkanalgur/termmosaic/widgets/menu).

Menu is a tree of items with a cursor path, nested submenus and a keyboard contract.

It is Focusable: keys are consumed only while focused, and a press inside the widget both selects and takes focus, so a click is a complete interaction without the application writing a click handler.

## Rendered output

{{< widget-capture menu >}}

> **About this capture.** The selected item and any open branch are marked with a character and a rule, not colour alone. Depth beyond one submenu is available but not shown here.

## Package context

Package menu provides Menu, a keyboard-driven menu with nested submenus to arbitrary depth.

## Constructing it

```go
menu.New(r buffer.Rect, items ...menu.Item) *menu.Menu
```

`NewMenu` takes a rect and variadic `Item`s. An `Item` with a non-empty `Items` field is a branch and gets the submenu marker; everything else is a leaf.

- `Items` — `[]Item` — the top level. Set it again at any time with `SetItems`.
- `Open` — Opens the menu, if it is closed. A closed menu is not drawn at all.
- `ItemStyle / SelectedStyle / DisabledStyle / HintStyle / CheckStyle / HeaderStyle` — `buffer.Style` per row role. An unset `SelectedStyle` means `ItemStyle` with `AttrReverse`, so a selection is legible with no configuration.
- `Checkable` — An `Item.Checkable` makes the row carry a check gutter, so a setting can be both visible and togglable in one list rather than two.
- `Ascii` — `bool` — use ASCII markers instead of `▸` and `✓` for terminals or fonts that misrender them.

## More on accessibility

The selected row carries a `>` in the marker gutter, which is a **character** rather than colour — so it survives `NO_COLOR` and appears in the plain-text capture. Level headers are bracketed when active and not when inactive, so depth is legible without colour. Disabled rows have no marker at all rather than a dimmed one, because a dimmed row is easy to miss entirely.

## When not to use it

**Do not use it for a flat list of items.** A row of tabs or a list of results is not a menu, and a menu implies commands with sub-commands. Use [`Tabs`](/widgets/tabs/) or [`List`](/widgets/list/).

**Do not nest it inside a `Dialog` for a simple yes/no.** A confirm is [`Dialog`](/widgets/dialog/) with two actions; building it from a menu loses the modal guarantee and the cancel-by-default behaviour.

**Do not use it as a command palette.** A palette is fuzzy-matched text over many commands, and this is an exact list over a known tree. [ADR 0009](/adr/0009-command-and-keymap/) specifies the keymap layer that a palette needs; it is not built yet.

**Instead:** A flat set of modes is [`Tabs`](/widgets/tabs/); a modal question is [`Dialog`](/widgets/dialog/); key commands with help text and rebinding need [ADR 0009](/adr/0009-command-and-keymap/), which is specified but not built yet.

## Related

- Dialog
- KeyHint
- [TermMosaic limitations that apply to every widget](/limitations/)
- Source: [`widgets/menu` on GitHub](https://github.com/serkanalgur/termmosaic/tree/main/widgets/menu)
