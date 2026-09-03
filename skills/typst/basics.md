# Typst Language Fundamentals

For data types, operators, and built-in functions, see [types.md](types.md).

## Modes

Markup mode (default at document top level) renders text as content; code mode starts with `#` and evaluates expressions:

```typst
Hello *bold* and _italic_.      // markup

#let x = 1 + 2                  // code
#for i in range(3) [Item #i]

// Switch: markup inside code with [ ], code inside markup with #
#let greeting = [Hello *world*]
The answer is #(1 + 2).
```

## Imports and Paths

```typst
#import "utils.typ": helper, format     // local file
#import "@preview/package-name:0.1.0": *  // Typst Universe package
```

| Path Type     | Example              | Resolves To                    |
| ------------- | -------------------- | ------------------------------ |
| Relative      | `"utils.typ"`        | Current file's directory       |
| Root-relative | `"/src/lib.typ"`     | Project root                   |
| Package       | `"@preview/pkg:1.0"` | Typst Universe / local package |

`--root` sets the project root: where `/`-prefixed paths resolve from, and the security boundary (files outside it cannot be read). For multi-file projects, run from the repo root: `typst compile src/main.typ --root .`

| Error                           | Cause                     | Fix                                                          |
| ------------------------------- | ------------------------- | ------------------------------------------------------------ |
| "file not found"                | Wrong relative path       | Check path relative to **current file**, not project root    |
| "file not found" with `/` path  | Root not set correctly    | Use `--root .` or adjust path                                |
| "would escape the project root" | File outside project root | Move file inside root or raise `--root` to a common ancestor |

`include` inserts a file's content inline; `import` brings symbols into scope. Bindings from an *included* file do **not** leak into the parent scope — share functions/variables via `import`:

```typst
#include "chapter1.typ"             // content appears here; its `let`s stay private
#import "vars.typ": shared-title    // shared values come from import
```

Data files follow the same path rules: `image("images/diagram.png")`, `json("data/config.json")`.

## Variables

```typst
#let name = "Alice"                  // immutable binding
#let (a, b) = (1, 2)                 // destructuring
#let (first, ..rest) = (1, 2, 3, 4)
```

See [types.md](types.md) for the full type reference. Quick summary: primitives (`int`, `float`, `str`, `bool`, `none`), arrays `(1, 2, 3)`, dictionaries `(key: val)`, content `[Hello *world*]`.

## Functions

```typst
#let greet(name, greeting: "Hello") = [#greeting, #name!]  // default param
#let double = x => x * 2                                   // lambda
#let sum(..nums) = nums.pos().fold(0, (a, b) => a + b)     // variadic

#greet("Bob", greeting: "Hi")   // named args use `:` not `=`
```

Inside a variadic function, `args.pos()` / `args.named()` return positional and named arguments.

## Control Flow

```typst
#let sign = if x > 0 { "+" } else { "-" }   // blocks return values

#for (i, item) in items.enumerate() [#i: #item]
#for (key, value) in dict [#key = #value]

#let i = 0
#while i < 5 { [#i ]; i += 1 }   // break/continue work as usual
```

## Common Pitfalls

### Mutability in Closures

**Closures cannot modify captured variables**:

```typst
// ❌ WRONG
#let results = ()
#let add(x) = { results.push(x) }  // Error!

// ✅ CORRECT - modify in loop
#let results = ()
#for item in items {
  results.push(item)
}
```

### None Returns

Functions without an explicit return value return `none`:

```typst
#let maybe(x) = {
  if x > 0 { x }
  // returns none if x <= 0
}

#let result = maybe(-1)
#if result != none [Got: #result] else [No result]
```

### Content vs String

```typst
// Content brackets are literal text — code is not evaluated inside
[1 + 2]                 // shows literal "1 + 2"
[Result: #(1 + 2)]      // shows "Result: 3"

// Concatenation differs by type
#let result = [#prefix#body#suffix]      // content
#let combined = prefix-str + body-str    // string

// Check if "empty"
#let is-empty(x) = { x == none or x == "" or x == [] }
```

### Spacing

```typst
// Adjacent code blocks merge without space
#[A]#[B]            // "AB"
#[A] #[B]           // "A B"
#[A]#h(1em)#[B]     // "A  B" (1em space)
```

## Error Handling

Use `assert(condition, message: "...")` for preconditions and `panic("...")` for unreachable states. For assertion patterns and debug techniques, see [debug.md](debug.md).
