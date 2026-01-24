# Advanced Typst Patterns

For language basics (types, operators, string/array/dict operations), see [basics.md](basics.md).

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

### Final Values

```typst
// Get final value (at document end)
#context {
  let final-count = counter.final()
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

## Labels and References

### Creating Labels

```typst
= Introduction <intro>

#figure(image("fig.png"), caption: [A figure]) <fig:main>
```

### Programmatic Labels

```typst
// Create label from string
#let key = "my-key"
#[Some content #label("ref-" + key)]

// Reference with link
#link(label("ref-" + key))[See here]
```

### Querying Labels

```typst
#context {
  let target = query(label("ref-mykey"))
  if target.len() > 0 {
    [Found at page #target.first().location().page()]
  }
}
```

## Working Around Closure Limitations

Closures cannot mutate captured variables. Use these patterns:

### Pattern 1: Accumulate in Loop

```typst
// ❌ WRONG
#let results = ()
#let process(x) = { results.push(x) }  // Error!

// ✅ CORRECT
#let results = ()
#for item in items {
  results.push(transform(item))
}
```

### Pattern 2: Fold for Accumulation

```typst
// Build dictionary from array
#let dict = items.fold((:), (acc, item) => {
  acc.insert(item.key, item.value)
  acc
})
```

### Pattern 3: State for Cross-Document

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

## Content vs String

```typst
// Content - rich formatted output
#let c = [Hello *world*]

// String - plain text
#let s = "Hello world"

// Convert string to content (implicit in most cases)
#[#s]

// Check if "empty"
#let is-empty(x) = {
  x == none or x == "" or x == []
}

// Concatenate content
#let result = [#prefix#body#suffix]

// For strings, use +
#let combined = prefix-str + body-str + suffix-str
```

## Performance Tips

1. **Precompute at document end**: Use `context` with `query()` and `.final()` to compute once
2. **Avoid deep recursion**: Typst has function call depth limits (~256)
3. **Cache expensive operations**: Store in state, compute once
4. **Use `.at(key, default: x)` instead of checking then accessing**

```typst
// ❌ Slower
#if key in dict { dict.at(key) } else { default }

// ✅ Faster
#dict.at(key, default: default)
```
