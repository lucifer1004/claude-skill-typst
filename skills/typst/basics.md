# Typst Language Fundamentals

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

## Data Types

### Primitives

```typst
#let n = 42          // Integer
#let f = 3.14        // Float
#let s = "hello"     // String
#let b = true        // Boolean
#let nothing = none  // None
```

### Strings

```typst
#let s = "hello"
#s.len()             // 5
#s.at(0)             // "h"
#s.contains("ell")   // true
#s.replace("l", "L") // "heLLo"
#s.split(" ")        // Array of words
#upper(s)            // "HELLO"
#lower("ABC")        // "abc"

// Trimming
#"  text  ".trim()           // "text"
#"  text  ".trim(at: start)  // "text  "
#"  text  ".trim(at: end)    // "  text"

// Checking
#s.starts-with("he")  // true
#s.ends-with("lo")    // true

// Split to chars
#"abc".split("")      // ("a", "b", "c")
```

### Regex

```typst
// Split with regex
#"a, b,  c".split(regex(",\\s*"))  // ("a", "b", "c")

// Match and capture
#let text = "v2.1.0"
#let match = text.match(regex("v(\\d+)\\.(\\d+)\\.(\\d+)"))
#if match != none {
  let captures = match.captures
  [Major: #captures.at(0), Minor: #captures.at(1)]
}

// Replace with regex
#"hello123world".replace(regex("\\d+"), "X")  // "helloXworld"

// Replace with capture groups
#"John Doe".replace(
  regex("([A-Z])[a-z]*\\s*"),
  m => m.captures.at(0) + "."
)  // "J.D."
```

### Arrays

```typst
#let arr = (1, 2, 3)
#arr.len()              // 3
#arr.at(0)              // 1
#arr.first()            // 1
#arr.last()             // 3
#arr.push(4)            // (1, 2, 3, 4)
#arr.pop()              // Returns 3, arr becomes (1, 2)
#arr.slice(1, 3)        // (2, 3)
#arr.contains(2)        // true
#arr.map(x => x * 2)    // (2, 4, 6)
#arr.filter(x => x > 1) // (2, 3)
#arr.find(x => x > 1)   // 2 (first match)
#arr.fold(0, (a, x) => a + x)  // 6
#arr.join(", ")         // "1, 2, 3"
#arr.sorted()           // Sorted copy
#arr.sorted(key: x => -x)  // (3, 2, 1) descending
#arr.rev()              // Reversed

// Check conditions
#arr.any(x => x > 2)    // true
#arr.all(x => x > 0)    // true

// Enumerate with index
#arr.enumerate().map(((i, x)) => [#i: #x])

// Dedup (requires sorted)
#(1, 1, 2, 2, 3).dedup()  // (1, 2, 3)
```

### Dictionaries

```typst
#let dict = (name: "Alice", age: 30)
#dict.at("name")        // "Alice"
#dict.at("missing", default: "N/A")
#dict.keys()            // ("name", "age")
#dict.values()          // ("Alice", 30)
#dict.pairs()           // ((name, "Alice"), (age, 30))
#dict.insert("city", "NYC")
#dict.remove("age")

// Check key existence
#if "name" in dict { ... }

// Iterate
#for (key, value) in dict {
  [#key = #value]
}

// Merge with spread
#let merged = (..dict, city: "NYC", age: 25)  // age overwritten
```

### Content

```typst
#let c = [Hello *world*]
// Content is the primary output type
// Most functions return content
```

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

### Content vs Value Context

```typst
// ❌ WRONG - Math in content mode
#let x = 1 + 2  // This is fine
[x = 1 + 2]     // This shows literal "1 + 2"

// ✅ CORRECT
[x = #(1 + 2)]  // Shows "x = 3"
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

### Assert

```typst
#let divide(a, b) = {
  assert(b != 0, message: "Division by zero")
  a / b
}
```

### Panic

```typst
#let required(x) = {
  if x == none {
    panic("Value is required")
  }
  x
}
```

## Debugging

### Type Inspection

```typst
#type(42)         // integer
#type("hello")    // string
#type((1, 2))     // array
#type((a: 1))     // dictionary
```

### Repr for Debugging

```typst
#repr((1, 2, 3))  // "(1, 2, 3)"
#repr((a: 1))     // "(a: 1)"
```

## Operators

### Arithmetic

```typst
#(5 + 3)   // 8
#(5 - 3)   // 2
#(5 * 3)   // 15
#(5 / 3)   // 1.666...
#calc.rem(5, 3)  // 2 (remainder)
```

### Comparison

```typst
#(5 == 5)  // true
#(5 != 3)  // true
#(5 < 10)  // true
#(5 <= 5)  // true
#(5 > 3)   // true
#(5 >= 5)  // true
```

### Logical

```typst
#(true and false)  // false
#(true or false)   // true
#(not true)        // false
```

### String/Array

```typst
#("a" + "b")       // "ab"
#((1, 2) + (3,))   // (1, 2, 3)
#("ab" * 3)        // "ababab"
#("x" in "text")   // true
```

## Methods vs Functions

```typst
// Method syntax
#"hello".len()
#(1, 2, 3).map(x => x * 2)

// Function syntax (equivalent)
#str.len("hello")
#array.map((1, 2, 3), x => x * 2)
```

## Useful Built-in Functions

```typst
// Math
#calc.abs(-5)     // 5
#calc.min(1, 2)   // 1
#calc.max(1, 2)   // 2
#calc.pow(2, 3)   // 8
#calc.sqrt(16)    // 4
#calc.floor(3.7)  // 3
#calc.ceil(3.2)   // 4
#calc.round(3.5)  // 4

// Range
#range(5)         // (0, 1, 2, 3, 4)
#range(1, 5)      // (1, 2, 3, 4)
#range(0, 10, step: 2)  // (0, 2, 4, 6, 8)
```
