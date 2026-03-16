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

Query finds elements in the document. Requires `context`.

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

For performance profiling and optimization, see [perf.md](perf.md).
