# CLI Introspection (`typst eval` / `typst query`)

For the in-document `query()` function, see [advanced.md](advanced.md). For language basics, see [basics.md](basics.md).

Use `typst eval --in <file>` on Typst 0.15+. It evaluates a Typst expression in a document context and serializes the result as JSON or YAML. `typst query` is deprecated in Typst 0.15, but remains the 0.14 fallback.

## Version Check

```bash
typst --version
```

| Version | Preferred command                  |
| ------- | ---------------------------------- |
| 0.15+   | `typst eval --in doc.typ '...'`    |
| 0.14.x  | `typst query doc.typ "<selector>"` |

## Typst 0.15+: `typst eval`

```bash
typst eval --in doc.typ 'query(heading).len()'
typst eval --in doc.typ 'query(<doc-info>).first().value' --pretty
typst eval --in doc.typ 'query(<task>).map(it => it.value)' --pretty
```

| Option                | Effect                                   |
| --------------------- | ---------------------------------------- |
| `--in <FILE>`         | Evaluate in a document context           |
| `--format json\|yaml` | Serialize as JSON or YAML                |
| `--pretty`            | Pretty-print JSON                        |
| `--input key=value`   | Pass string to `sys.inputs` (repeatable) |
| `--root <DIR>`        | Set project root for `/path` imports     |

Use `typst eval` for expression probes too:

```bash
typst eval '1 + 2'
typst eval 'type("hi")'
```

## 0.14 Fallback: `typst query`

```bash
typst query [OPTIONS] <INPUT> <SELECTOR>
```

`typst query` accepts element selectors and labels:

```bash
typst query doc.typ "heading"
typst query doc.typ "figure"
typst query doc.typ "<doc-info>" --field value --one --pretty
```

The useful 0.14 options are `--field`, `--one`, `--format json|yaml`, `--pretty`, `--input`, and `--root`.

## Selectors

### Element type

```bash
typst eval --in doc.typ 'query(heading).len()'
typst eval --in doc.typ 'query(figure).len()'
typst eval --in doc.typ 'query(math.equation).len()'
```

### Label

```bash
typst eval --in doc.typ 'query(<my-label>).first().value'
```

### Filtered with `.where()`

```bash
typst eval --in doc.typ 'query(heading.where(level: 1)).len()'
typst eval --in doc.typ 'query(figure.where(kind: image)).len()'
typst eval --in doc.typ 'query(figure.where(kind: table)).len()'
```

### Restricted with `.within()` (Typst 0.15+)

```bash
typst eval --in doc.typ 'query(heading.where(level: 2).within(<methods>)).len()'
```

## `metadata()` Export

`metadata(value)` creates invisible content that holds any Typst value. Attach a label, then inspect it from the CLI.

```typst
#metadata("1.0.0") <version>
#metadata((title: "Report", status: "draft")) <doc-info>
```

```bash
typst eval --in doc.typ 'query(<version>).first().value'
# -> "1.0.0"

typst eval --in doc.typ 'query(<doc-info>).first().value' --pretty
# -> {"title": "Report", "status": "draft"}
```

### 0.14 equivalent

```bash
typst query doc.typ "<version>" --field value --one
typst query doc.typ "<doc-info>" --field value --one --pretty
```

## Type Mapping

| Typst        | JSON                            |
| ------------ | ------------------------------- |
| `str`        | string                          |
| `int`        | number                          |
| `float`      | number                          |
| `bool`       | boolean                         |
| `none`       | `null`                          |
| `array`      | array                           |
| `dictionary` | object                          |
| content      | nested object with `"func"` key |

## Label Placement in `context`

The label must go on `metadata()` itself, inside the context block:

```typst
// CORRECT: label on metadata
#context {
  let data = query(heading).len()
  [#metadata(data) <heading-count>]
}

// WRONG: label on context block, returns context content with no value field
#context {
  metadata(query(heading).len())
} <heading-count>
```

## Patterns

### Extract document metadata

```typst
// doc.typ
#metadata((
  title: "Product Spec",
  version: "2.1.0",
  authors: ("Alice", "Bob"),
  status: "final",
)) <doc-info>
```

```bash
typst eval --in doc.typ 'query(<doc-info>).first().value' --pretty
VERSION=$(typst eval --in doc.typ 'query(<doc-info>).first().value.at("version")' | jq -r .)
```

### Export document statistics

```typst
#context {
  let stats = (
    headings: query(heading).len(),
    figures: query(figure).len(),
    equations: query(math.equation).len(),
    pages: counter(page).final().first(),
  )
  [#metadata(stats) <doc-stats>]
}
```

```bash
typst eval --in doc.typ 'query(<doc-stats>).first().value' --pretty
# -> {"headings":5,"figures":3,"equations":12,"pages":8}
```

### Export TOC with page numbers

Heading bodies are content, not strings. Use the `plain-text` helper from [advanced.md](advanced.md) (Content Introspection section) to extract text.

```typst
#let plain-text(value) = repr(value)

#context {
  let toc = query(heading).map(h => {
    let pg = counter(page).at(h.location()).first()
    (level: h.level, title: plain-text(h.body), page: pg)
  })
  [#metadata(toc) <toc-export>]
}
```

```bash
typst eval --in doc.typ 'query(<toc-export>).first().value' --pretty
# -> [{"level":1,"title":"Introduction","page":1}, ...]
```

### Multi-pass compilation

Query in pass 1, feed back via `--input` in pass 2. Example: "Page X of N" footer.

```typst
// main.typ
#let total = sys.inputs.at("total-pages", default: none)

#set page(footer: context {
  let current = counter(page).get().first()
  if total != none [Page #current of #total] else [Page #current]
})

= Chapter One
#lorem(200)

= Chapter Two
#lorem(300)

#context [#metadata(counter(page).final().first()) <page-count>]
```

```bash
PAGES=$(typst eval --in main.typ 'query(<page-count>).first().value')
typst compile main.typ --input "total-pages=$PAGES"
```

### Conditional metadata with `sys.inputs`

Label must be on `metadata()` inside the `if`, not on the `if` block.

```typst
#let mode = sys.inputs.at("mode", default: "normal")
#if mode == "ci" [
  #metadata((
    version: "1.0.0",
    packages: ("cetz", "tablex"),
  )) <ci-meta>
]
```

```bash
typst eval --in doc.typ 'query(<ci-meta>).first().value' --input mode=ci --pretty
```

### Structured task/status tracking

Multiple elements can share a label. `query(<task>)` returns all matching metadata elements.

```typst
#let task(name, status, priority: "medium") = {
  metadata((name: name, status: status, priority: priority))
}

#task("Design API", "done", priority: "high") <task>
#task("Write tests", "in-progress") <task>
#task("Deploy", "pending", priority: "low") <task>
```

```bash
typst eval --in doc.typ 'query(<task>).map(it => it.value)' --pretty
# -> [{"name":"Design API","status":"done","priority":"high"}, ...]
```

### CI version gate

```bash
#!/bin/bash
EXPECTED="2.1.0"
ACTUAL=$(typst eval --in doc.typ 'query(<version>).first().value' | tr -d '"')
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "Version mismatch: expected $EXPECTED, got $ACTUAL" >&2
  exit 1
fi
```

### Batch validation

```bash
for f in docs/*.typ; do
  typst eval --in "$f" 'query(<doc-info>).first().value' > /dev/null 2>&1 \
    || echo "MISSING metadata: $f" >&2
done
```

## Agent Workflow

Use `typst eval --in` to verify document structure without opening a PDF:

```bash
typst eval --in doc.typ 'query(<expected-section>).len() > 0' | grep true
typst eval --in doc.typ 'query(figure).len()'                    # figure count
typst eval --in doc.typ 'query(<doc-info>).first().value.at("status")' | jq -e '. == "final"'
```

See [query-export.typ](examples/query-export.typ) for a runnable example.

## Fileless Probe

For a raw expression:

```bash
typst eval '1 + 2'
# -> 3
```

For document-context probes from stdin:

```bash
printf '#metadata(1 + 2) <probe>\n' | typst eval --in - 'query(<probe>).first().value'
# -> 3
```

Useful when docs or search are ambiguous about return types or runtime behavior. Exit code 1 on compile failure; stderr carries the error.
