# Typst Data Types and Operators

For syntax, imports, functions, and control flow, see [basics.md](basics.md).

## Primitives

```typst
#let n = 42          // Integer
#let f = 3.14        // Float
#let s = "hello"     // String
#let b = true        // Boolean
#let nothing = none  // None
```

## Strings

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

## Regex

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

## Arrays

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
#arr.map(str).join(", ")  // "1, 2, 3"
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

## Dictionaries

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

## Content

```typst
#let c = [Hello *world*]
// Content is the primary output type
// Most functions return content
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

## Type Inspection

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
