# Typst Language Fundamentals

For data types, operators, and built-in functions, see [types.md](types.md).

## Modes

Typst has two modes that determine how text is interpreted:

### Markup Mode

Default mode at document top level. Text is rendered as content:

```typst
Hello *bold* and _italic_ text.

= Heading
- List item
```

### Code Mode

Entered with `#`. Expressions and statements:

```typst
#let x = 1 + 2
#if condition { [content] }
#for i in range(5) { [Item #i] }
```

### Switching Between Modes

```typst
// Code → Markup: use [ ]
#let greeting = [Hello *world*]

// Markup → Code: use #
The answer is #(1 + 2).
```

## Imports and Paths

### Import Syntax

```typst
// Import from local file (relative to current file)
#import "utils.typ": helper, format
#import "lib/core.typ": *

// Import from Typst Universe packages
#import "@preview/package-name:0.1.0": func1, func2

// Import from local packages
#import "@local/my-package:0.1.0": *
```

### Path Resolution Rules

| Path Type     | Example              | Resolves To                              |
| ------------- | -------------------- | ---------------------------------------- |
| Relative      | `"utils.typ"`        | Relative to **current file's directory** |
| Root-relative | `"/src/lib.typ"`     | Relative to **project root**             |
| Package       | `"@preview/pkg:1.0"` | Typst Universe or local packages         |

```typst
// File structure:
// project/
// ├── main.typ
// └── src/
//     ├── lib.typ
//     └── utils.typ

// In main.typ:
#import "src/lib.typ": *      // ✅ Relative to main.typ
#import "/src/lib.typ": *     // ✅ Root-relative (same result)

// In src/lib.typ:
#import "utils.typ": *        // ✅ Relative to lib.typ (finds src/utils.typ)
#import "/src/utils.typ": *   // ✅ Root-relative
#import "../main.typ": *      // ✅ Parent directory
```

### Project Root (`--root`)

The project root controls:

1. Where `/`-prefixed paths resolve from
2. Security boundary (files outside root cannot be accessed)

```bash
# Default: root is the main file's directory
typst compile src/main.typ
# Root = src/, so "/lib.typ" looks for src/lib.typ

# Explicit root: set project root to current directory
typst compile src/main.typ --root .
# Root = ., so "/lib.typ" looks for ./lib.typ

# Common pattern for multi-file projects
typst compile document.typ --root .
```

### Common Path Errors

| Error                          | Cause                     | Fix                                                       |
| ------------------------------ | ------------------------- | --------------------------------------------------------- |
| "file not found"               | Wrong relative path       | Check path relative to **current file**, not project root |
| "file not found" with `/` path | Root not set correctly    | Use `--root .` or adjust path                             |
| "access denied"                | File outside project root | Move file inside root or adjust `--root`                  |

### Image and Data Files

```typst
// Images use the same path rules
#image("images/diagram.png")       // Relative to current file
#image("/assets/logo.png")         // Relative to project root

// Reading data files
#let data = json("data/config.json")
#let content = read("templates/header.typ")
```

### Include vs Import

```typst
// import: brings symbols into scope
#import "utils.typ": helper
#helper()

// include: directly inserts file content as-is
#include "chapter1.typ"  // Content appears here
```

**Scope difference**:

```typst
// chapters/intro.typ (content file)
This is chapter 1.

// vars.typ (module file)
#let shared-title = "Intro"

// main.typ
#include "chapters/intro.typ"
#shared-title  // ❌ Error! Variables defined in included files
               // do NOT leak to parent scope

// To share variables, use import from a module file:
#import "vars.typ": shared-title
#shared-title  // ✅ Works
```

Use `include` for document content, `import` for reusable functions/variables.

## Variables

```typst
// Immutable binding
#let name = "Alice"
#let count = 42
#let items = (1, 2, 3)

// Destructuring
#let (a, b) = (1, 2)
#let (first, ..rest) = (1, 2, 3, 4)

// Dictionary destructuring
#let (name: n, age: a) = (name: "Bob", age: 30)
```

## Data Types, Operators, and Built-ins

See [types.md](types.md) for the full reference. Quick summary:

- Primitives: `int`, `float`, `str`, `bool`, `none`
- Collections: arrays `(1, 2, 3)`, dictionaries `(key: val)`
- Content: `[Hello *world*]`

## Functions

### Basic Functions

```typst
#let greet(name) = [Hello, #name!]

#greet("Alice")  // Hello, Alice!
```

### Default Parameters

```typst
#let greet(name, greeting: "Hello") = [#greeting, #name!]

#greet("Bob")                    // Hello, Bob!
#greet("Bob", greeting: "Hi")    // Hi, Bob!
```

### Variadic Arguments

```typst
#let sum(..nums) = {
  let total = 0
  for n in nums.pos() {
    total += n
  }
  total
}

#sum(1, 2, 3)  // 6
```

### Named and Positional Args

```typst
#let format(..args) = {
  let positional = args.pos()   // Array
  let named = args.named()      // Dictionary
  // ...
}
```

### Anonymous Functions (Lambdas)

```typst
#let double = x => x * 2
#let add = (a, b) => a + b

#(1, 2, 3).map(x => x * 2)  // (2, 4, 6)
```

## Control Flow

### Conditionals

```typst
#if x > 0 {
  [Positive]
} else if x < 0 {
  [Negative]
} else {
  [Zero]
}

// Inline conditional (returns value)
#let sign = if x > 0 { "+" } else { "-" }
```

### Loops

```typst
// For loop
#for item in items {
  [- #item]
}

#for (i, item) in items.enumerate() {
  [#i: #item]
}

#for (key, value) in dict {
  [#key = #value]
}

// While loop
#let i = 0
#while i < 5 {
  [#i ]
  i += 1
}
```

### Loop Control

```typst
#for item in items {
  if item == "skip" { continue }
  if item == "stop" { break }
  [#item]
}
```

## Common Pitfalls

### Mutability in Closures

**Closures cannot modify captured variables**:

```typst
// ❌ WRONG
#let results = ()
#let add(x) = { results.push(x) }  // Error!

// ✅ CORRECT - Modify in loop
#let results = ()
#for item in items {
  results.push(item)
}
```

### None Returns

Functions without explicit return value return `none`:

```typst
#let maybe(x) = {
  if x > 0 { x }
  // Returns none if x <= 0
}

// Handle none
#let result = maybe(-1)
#if result != none {
  [Got: #result]
} else {
  [No result]
}
```

### Content vs String

```typst
// Content brackets are literal text — code is not evaluated inside
[1 + 2]         // Shows literal "1 + 2"
[Result: #(1 + 2)]  // Shows "Result: 3"

// Concatenation differs by type
#let result = [#prefix#body#suffix]       // content
#let combined = prefix-str + body-str     // string

// Check if "empty"
#let is-empty(x) = { x == none or x == "" or x == [] }
```

### Spacing

```typst
// Adjacent code blocks merge without space
#[A]#[B]  // "AB"

// Add explicit space
#[A] #[B]  // "A B"
#[A]#h(1em)#[B]  // "A  B" (1em space)
```

## Error Handling

Use `assert(condition, message: "...")` for preconditions and `panic("...")` for unreachable states.
