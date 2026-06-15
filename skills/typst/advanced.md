# Advanced Typst Patterns

For language basics (syntax, imports, functions), see [basics.md](basics.md). For data types and operators, see [types.md](types.md). For labels, references, and everyday styling, see [styling.md](styling.md).

## XML Parsing

Typst has built-in XML parsing:

````typst
#let xml-content = ```xml
<root>
  <item name="first">Value 1</item>
  <item name="second">Value 2</item>
</root>
```.text

#let doc = xml(xml-content)
// doc is an array of nodes

// Navigate structure
#let root = doc.first()  // Root element
#let children = root.children  // Child nodes
#let attrs = root.attrs  // Attributes dictionary

// Find elements by tag
#let find-child(node, tag) = {
  node.children.find(c => (
    type(c) == dictionary and c.at("tag", default: "") == tag
  ))
}

#let find-children(node, tag) = {
  node.children.filter(c => (
    type(c) == dictionary and c.at("tag", default: "") == tag
  ))
}

// Get text content (handles nested text)
#let get-text(node) = {
  if type(node) == str { return node }
  if type(node) != dictionary { return "" }
  node.children.map(c => {
    if type(c) == str { c } else { get-text(c) }
  }).join("")
}
````

### XML Node Structure

```typst
// Element node
(
  tag: "element-name",
  attrs: (attr1: "value1", attr2: "value2"),
  children: (/* child nodes or strings */),
)

// Text nodes are plain strings in the children array
```

## State and Context

State allows tracking information across a document. Requires `context` to read.

### Basic State

```typst
#let counter = state("my-counter", 0)

// Update state
#counter.update(n => n + 1)

// Read state (must be in context)
#context counter.get()

// Display with context
#context [Count: #counter.get()]
```

### Custom Counters

```typst
#let example-counter = counter("example")

#let example(body) = {
  example-counter.step()
  block[*Example #context example-counter.display():* #body]
}
```

### State for Headers

```typst
#let chapter-title = state("chapter", none)

#show heading.where(level: 1): it => {
  chapter-title.update(it.body)
  it
}

#set page(header: context { chapter-title.get() })
```

### Final Values

```typst
// Get final value (at document end)
#let my-counter = state("my-counter", 0)
#context {
  let final-count = my-counter.final()
  [Total: #final-count]
}
```

### Tracking Across Document

```typst
// Track citations
#let _citations = state("citations", (:))

#let cite-marker(key) = {
  [#metadata((key: key)) <my-cite>]
  _citations.update(c => {
    if key not in c { c.insert(key, 0) }
    c.at(key) += 1
    c
  })
}

// At document end
#context {
  let data = _citations.final()
  // Process collected data...
}
```

## Query System

Query finds elements in the document. Requires `context`. For CLI introspection with `typst eval` (Typst 0.15+) or `typst query` (0.14 fallback), see [query.md](query.md).

### By Label

```typst
// Place metadata markers
#metadata((key: "item1", value: 42)) <marker>

// Query all markers
#context {
  let items = query(<marker>)
  for item in items {
    let data = item.value
    [Key: #data.key, Value: #data.value]
  }
}
```

### By Selector

```typst
// Query all headings
#context {
  let headings = query(heading)
  for h in headings { [- #h.body] }
}

// Query specific heading level
#context {
  let h1s = query(heading.where(level: 1))
}
```

### Within an Ancestor (Typst 0.15+)

Use `selector.within` to restrict matches to a section, figure, or other ancestor. This is especially useful for multi-document HTML bundles.

```typst
= Methods <sec:methods>

== Setup

#context {
  let local = query(heading.where(level: 2).within(<sec:methods>))
  [Method subsections: #local.len()]
}
```

### By Label String

```typst
#context {
  let target = query(label("ref-mykey"))
  if target.len() > 0 {
    [Found at page #target.first().location().page()]
  }
}
```

### Location-Based

```typst
#context {
  let items = query(<marker>)
  let here-loc = here()

  // Find items before current location
  let before = items.filter(i => (
    i.location().position().y < here-loc.position().y
  ))
}
```

## Closure Workarounds

Closures cannot mutate captured variables (see basics.md "Mutability in Closures"). Beyond the loop accumulation pattern, two more options:

### Fold for Accumulation

```typst
// Build dictionary from array
#let dict = items.fold((:), (acc, item) => {
  acc.insert(item.key, item.value)
  acc
})
```

### State for Cross-Document

```typst
#let _data = state("data", ())

#let add-item(item) = {
  _data.update(d => { d.push(item); d })
}

// Read accumulated data
#context {
  let all-items = _data.final()
}
```

## Content Introspection

Content elements (headings, text, figures, etc.) can be inspected and decomposed programmatically. This is essential for advanced show rules and template development.

### Core Methods

```typst
= Hello *World*

// func() — the element's constructor (for type comparison)
#context {
  let h = query(heading).first()
  let is-heading = h.func() == heading   // true
  let is-text = h.func() == text         // false
}

// fields() — dictionary of all field values
#context {
  let h = query(heading).first()
  let f = h.fields()
  // f.keys() → ("level", "depth", "offset", "numbering", "supplement",
  //             "outlined", "bookmarked", "hanging-indent", "body")
}

// has() / at() — check and access fields
#context {
  let h = query(heading).first()
  let has-body = h.has("body")     // true
  let level = h.at("level")        // 1
}
```

### Content Tree Structure

Content is a tree. Compound elements have `children`; leaf elements have `text`. Whitespace is a separate `space` node:

```typst
// [Hello *World*] decomposes to:
// sequence
//   ├── text("Hello")
//   ├── space
//   └── strong
//       └── text("World")

// Access children via fields()
#let body = [Hello *World*]
#let f = body.fields()
// "children" in f → true
// f.children → (text("Hello"), space, strong(...))
```

### Show Rule Decomposition Pattern

Intercept an element, decompose its content, transform parts, reassemble:

```typst
// Bold text before first colon in list items
#show list.item: it => {
  let fields = it.body.fields()
  if "text" in fields and ":" in fields.text {
    let idx = fields.text.position(":")
    list.item[*#(fields.text.slice(0, idx)):*#(fields.text.slice(idx + 1))]
  } else if "children" in fields {
    let (before, after, found) = ((), (), false)
    for child in fields.children {
      if found { after.push(child) }
      else if type(child) != str and child.func() == text and ":" in child.text {
        let idx = child.text.position(":")
        before.push(child.text.slice(0, idx))
        found = true
        let post = child.text.slice(idx + 1)
        if post.len() > 0 { after.push(post) }
      } else { before.push(child) }
    }
    if found { list.item[*#(before.join()):*#(after.join())] } else { it }
  } else { it }
}

- Name: John Doe
- Age: 25
- No colon here
```

### Recursive Plain-Text Extraction

Extract plain text from any content element (useful for metadata export, see [query.md](query.md)):

```typst
#let plain-text(content) = {
  let fields = content.fields()
  if "text" in fields {
    fields.text
  } else if "children" in fields {
    fields.children.map(c => {
      if type(c) == str { c }
      else if c.func() == [ ].func() { " " }  // space element
      else { plain-text(c) }
    }).join()
  } else if "body" in fields {
    plain-text(fields.body)
  } else if "child" in fields {
    plain-text(fields.child)
  } else { "" }
}
```

### Common Element Fields

| Element     | Key fields                                        |
| ----------- | ------------------------------------------------- |
| `heading`   | `level`, `body`, `numbering`, `outlined`          |
| `text`      | `text` (leaf — the actual string)                 |
| `strong`    | `body`                                            |
| `emph`      | `body`                                            |
| `list.item` | `body`                                            |
| `enum.item` | `body`, `number`                                  |
| `figure`    | `body`, `caption`, `kind`, `supplement`           |
| `sequence`  | `children` (array of child elements)              |
| `space`     | (no fields — check with `c.func() == [ ].func()`) |

For performance profiling and optimization, see [perf.md](perf.md).
