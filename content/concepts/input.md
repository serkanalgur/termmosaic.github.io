---
title: "Input"
description: "Decode, Parser, Source, the event model, one-event paste, and what is deliberately out of scope."
weight: 24
toc: true
---

# Input

The `input` package, and the reasoning behind it. The full record is
[ADR 0005](/adr/0005-input-decoding/).

## The shape: a pure decoder under a resumable driver

Three pieces, and the split between them is the design:

```go
func Decode(seq []byte, cfg Config) (Event, int, Status)   // pure
type Parser                                          // holds the unavoidable bytes
type Source                                          // merges input and resize onto one channel
```

### `Decode` is pure, and that is why it works

The worst bug in a terminal input layer is an escape sequence split across two
`read(2)` calls. If the decoder holds state, that bug is a flaky timing test.

**So `Decode` is a pure function of a byte slice.** A sequence arriving in
pieces is a pure function called twice, and the whole class of bug becomes a
one-line table-driven test.

### `Parser` holds only what it must

The unavoidable bytes — an incomplete sequence at the end of a chunk. It is the
only stateful part, and it is small enough to reason about.

### `Source` merges input and resize onto ONE ordered channel

This is the part that matters most in practice:

> **A resize can never be delivered between the bytes of a half-read escape
> sequence, and no input event is ever dropped to make room for a resize.**

The alternative — a separate resize channel, or two goroutines — produces exactly
the bug above. There is one channel, and it is ordered.

```go
for {
    select {
    case ev, ok := <-src.Events():
        if !ok {
            return          // the terminal reached EOF
        }
        switch ev.Kind {
        case termmosaic.EventKey:
            // keys
        case termmosaic.EventResize:
            // recompute bounds, then r.Resize
        }
    }
}
```

## Scope verdicts

| Feature | Verdict |
|---|---|
| **Kitty keyboard** | **In**, as progressive enhancement. Requests only `disambiguate`, with a 100 ms bounded probe. |
| **Bracketed paste** | **In**, and always **one `EventPaste` carrying the whole payload** — never a stream. |
| **Mouse decoding** | **In** — SGR 1006, urxvt 1015, X10. **Capture is off by default.** |
| **Focus decoding** | **In**, **reporting off by default.** |
| **IME / composition** | **Deferred and scoped out.** `EventCompose` and a `Compose` payload field are reserved. |

### Why paste is one event

A bracketed paste arrives as `ESC [ 200 ~ … ESC [ 201 ~`. Treating it as a stream
would mean the widget has to reassemble it, and every widget that pasted would
reassemble it differently.

**One event carrying the whole payload** means `TextInput` gets the whole thing
and makes it **one undoable operation**: a 10,000-character paste is one step on
the undo stack, so one Ctrl-Z removes the whole of it. That is a test, not a
hope.

### Why mouse capture is off by default

**Enabling it takes text selection and scrollback copying away from the user's
shell.** That is a real cost paid by the user, paid silently, for a feature most
programs use rarely. So it is opt-in. Focus reporting is off for the same reason.

## No IME, and what that actually costs

This is the sharpest limitation in the framework and it is worth being precise
about, because the honest version is worse-sounding than the vague one:

> **Composing Japanese, Chinese or Korean in a `TextInput` produces *wrong*
> behaviour, not degraded behaviour.**

There is no preedit and no composition support — a deliberate deferral in
ADR 0005 §7, not an oversight. On most terminals the committed text arrives as a
burst of ordinary key events, so **the text inserts correctly but pollutes the
undo stack with one entry per character**, and a single Ctrl-Z removes one
character instead of the composition.

Do not read this as parity with a framework that has IME support, and do not read
it as a gap being closed. It is a documented decision with a stated trigger:
two or more independent reports of CJK/IME input being unusable, or `TextInput`
shipping with undo groups large enough to be obviously wrong on
composition-shaped bursts, or a terminal shipping a preedit protocol with real
adoption. **Not before** — there is no `TextInput` to design against and no
reference implementation in any comparable framework.

The deferral is scoped, not vague: the door is left open at **three named seams**
so this is a deferred feature rather than a deferred rewrite.

1. `EventCompose` is declared, and never emitted in v0.x.
2. `Event` carries a `Compose *Compose` payload field.
3. The parser's entry point is the **byte stream**, not the event type — which is
   the direct consequence of `Decode` being pure.

## tmux DCS passthrough is a real gap

Under tmux on a modern terminal, a TermMosaic program **can lose key and mouse
reporting**, because the sequences TermMosaic emits are not wrapped for the
multiplexer. Deferred with a trigger: any tmux user reporting broken keys or
mouse, or v1.0, whichever comes first.

If you develop under tmux, test in a plain terminal before concluding the library
is broken.

## The key path allocates nothing

**0 allocations on the key path, pinned by a test.** ADR 0005 is explicit that
this is a property the ADR specifies and a test must pin, **not a measurement
taken today** — input decoding is I/O-bound, so a benchmark here would measure the
operating system.

That is a distinction this site keeps making on purpose: see
[Performance](/guides/performance/) for which numbers are measured and which are
specified-and-tested.

## Key names in hints are strings

`keyhint.Binding.Key` is a `string`, not a `termmosaic.Key`, for two reasons: a
hint can then name a key the `Key` enum does not have (`"ctrl+s"`), and the hint
says **what the user's terminal calls the key** rather than what the decoder
calls it. See [`KeyHint`](/widgets/keyhint/).

## Reading next

- [`TextInput`](/widgets/textinput/) — the reference implementation of the form
  set, because ADR 0005 §4 was written about it.
- [Forms](/guides/forms/) — the nine form widgets as one workflow.
- [Degradation and NO_COLOR](/concepts/degradation/) — the other encode-time
  decision.
- [ADR 0005](/adr/0005-input-decoding/) — verbatim, including §7 and §10.