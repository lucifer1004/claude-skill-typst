# CLI Query (`typst query`)

For the in-document `query()` function, see [advanced.md](advanced.md). For language basics, see [basics.md](basics.md).

`typst query` compiles a document and extracts structured data as JSON. It bridges Typst's introspection system with external tooling — shell scripts, CI pipelines, multi-pass builds.

## Syntax

```bash
typst query [OPTIONS] <INPUT> <SELECTOR>
```

| Argument     | Description                               |
| ------------ | ----------------------------------------- |
| `<INPUT>`    | Path to `.typ` file (use `-` for stdin)   |
| `<SELECTOR>` | Typst selector: element type or `<label>` |

Output goes to stdout as JSON (or YAML). Errors go to stderr. If compilation fails, exit code is 1 and stdout is empty — guard CI scripts accordingly.

## Key Options

| Option              | Effect                                                    |
| ------------------- | --------------------------------------------------------- |
| `--field <FIELD>`   | Extract one field from each match (e.g., `value`, `body`) |
| `--one`             | Expect exactly one match; return bare value, not array    |
| \`--format json     | yaml\`                                                    |
| `--pretty`          | Pretty-print JSON                                         |
| `--input key=value` | Pass string to `sys.inputs` (repeatable)                  |
| `--root <DIR>`      | Set project root for `/path` imports                      |

## Selectors

### Element type

```bash
typst query doc.typ "heading"
typst query doc.typ "figure"
typst query doc.typ "math.equation"
```

### Label

```bash
typst query doc.typ "<my-label>"
```

### Filtered with `.where()`

```bash
typst query doc.typ "heading.where(level: 1)"
typst query doc.typ "figure.where(kind: image)"
typst query doc.typ "figure.where(kind: table)"
```

## `metadata()` — The Primary Export Mechanism

`metadata(value)` creates invisible content that holds any Typst value. Attach a label, then query it from the CLI.

```typst
#metadata("1.0.0") <version>
#metadata((title: "Report", status: "draft")) <doc-info>
```

```bash
typst query doc.typ "<version>" --field value --one
# → "1.0.0"

typst query doc.typ "<doc-info>" --field value --one --pretty
# → {"title": "Report", "status": "draft"}
```

### Type mapping (Typst → JSON)

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

## `--field` and `--one`

```bash
typst query doc.typ "heading"                        # full element objects (array)
typst query doc.typ "heading" --field body            # one field per element (array)
typst query doc.typ "<version>" --field value --one   # exactly one match (bare value)
# --one exits with code 1 if 0 or 2+ matches
```

| Element         | Useful fields             |
| --------------- | ------------------------- |
| `metadata`      | `value`                   |
| `heading`       | `body`, `level`           |
| `figure`        | `caption`, `body`, `kind` |
| `math.equation` | `body`, `block`           |

## Label Placement in `context`

The label must go on `metadata()` itself, **inside** the context block:

```typst
// CORRECT — label on metadata
#context {
  let data = query(heading).len()
  [#metadata(data) <heading-count>]
}

// WRONG — label on context block, returns {"func":"context"} with no value field
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
typst query doc.typ "<doc-info>" --field value --one --pretty
VERSION=$(typst query doc.typ "<doc-info>" --field value --one | jq -r '.version')
```

### Export TOC with page numbers

Heading bodies are content, not strings. Use the `plain-text` helper from [advanced.md](advanced.md) (Content Introspection section) to extract text:

```typst
// plain-text() defined in advanced.md — recursive content-to-string extractor

#context {
  let toc = query(heading).map(h => {
    let pg = counter(page).at(h.location()).first()
    (level: h.level, title: plain-text(h.body), page: pg)
  })
  [#metadata(toc) <toc-export>]
}
```

```bash
typst query doc.typ "<toc-export>" --field value --one --pretty
# → [{"level":1,"title":"Introduction","page":1}, ...]
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
typst query doc.typ "<doc-stats>" --field value --one
# → {"headings":5,"figures":3,"equations":12,"pages":8}
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
PAGES=$(typst query main.typ "<page-count>" --field value --one)
typst compile main.typ --input "total-pages=$PAGES"
```

### Conditional metadata with `sys.inputs`

Label must be on `metadata()` inside the `if`, not on the `if` block (see label placement above).

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
typst query doc.typ "<ci-meta>" --field value --one --input mode=ci
```

### Structured task/status tracking

Multiple elements can share a label — `typst query` returns all matches as an array.

```typst
#let task(name, status, priority: "medium") = {
  metadata((name: name, status: status, priority: priority))
}

#task("Design API", "done", priority: "high") <task>
#task("Write tests", "in-progress") <task>
#task("Deploy", "pending", priority: "low") <task>
```

```bash
typst query doc.typ "<task>" --field value --pretty
# → [{"name":"Design API","status":"done","priority":"high"}, ...]
```

### CI version gate

```bash
#!/bin/bash
EXPECTED="2.1.0"
ACTUAL=$(typst query doc.typ "<version>" --field value --one | tr -d '"')
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "Version mismatch: expected $EXPECTED, got $ACTUAL" >&2
  exit 1
fi
```

### Batch validation

```bash
# Verify all docs have required metadata
for f in docs/*.typ; do
  typst query "$f" "<doc-info>" --field value --one > /dev/null 2>&1 \
    || echo "MISSING metadata: $f" >&2
done
```

## Agent Workflow

Agents cannot preview PDFs — use `typst query` to verify document structure:

```bash
typst query doc.typ "<expected-section>" --one > /dev/null 2>&1 && echo "OK"
typst query doc.typ "figure" | jq 'length'                    # figure count
typst query doc.typ "<doc-info>" --field value --one | jq -e '.status == "final"'
```

See [query-export.typ](examples/query-export.typ) for a runnable example.

### Fileless probe

When you need to test an expression's value without creating a scratch `.typ` file, pipe markup to stdin with `-`:

```bash
printf '#metadata(1 + 2) <probe>\n' | typst query - "<probe>" --field value --one
# → 3

printf '#metadata(type("hi")) <probe>\n' | typst query - "<probe>" --field value --one
# → "str"
```

Useful when docs or search are ambiguous about return types or runtime behavior. Exit code 1 on compile failure — stderr carries the error.
