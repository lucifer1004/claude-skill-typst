// Query export example — demonstrates metadata export for CLI introspection.
//
// Usage:
//   typst eval --in examples/query-export.typ 'query(<doc-info>).first().value' --pretty
//   typst eval --in examples/query-export.typ 'query(<doc-stats>).first().value' --pretty
//   typst eval --in examples/query-export.typ 'query(<task>).map(it => it.value)' --pretty
//   typst eval --in examples/query-export.typ 'query(heading).map(it => it.body)' --pretty
//   typst compile examples/query-export.typ /dev/null -f pdf
//
// Multi-pass (inject total page count):
//   PAGES=$(typst eval --in examples/query-export.typ 'query(<page-count>).first().value')
//   typst compile examples/query-export.typ --input "total-pages=$PAGES"

// --- Document metadata (plain, no context needed) ---

#metadata((
  title: "Query Export Demo",
  version: "1.0.0",
  authors: ("Alice", "Bob"),
  status: "draft",
)) <doc-info>

// --- Task tracking (multiple elements with same label) ---

#let task(name, status, priority: "medium") = {
  metadata((name: name, status: status, priority: priority))
}

#task("Design API", "done", priority: "high") <task>
#task("Write tests", "in-progress") <task>
#task("Deploy", "pending", priority: "low") <task>

// --- Page setup ---

#let total = sys.inputs.at("total-pages", default: none)

#set page(paper: "a4", margin: 2cm, footer: context {
  let current = counter(page).get().first()
  if total != none [Page #current of #total] else [Page #current]
})
#set heading(numbering: "1.1")

= Introduction

#lorem(100)

== Background

#lorem(80)

= Methods

#lorem(120)

= Results

#lorem(100)

// --- Computed exports (require context) ---
// Label goes on metadata INSIDE the context block.

#context {
  let stats = (
    headings: query(heading).len(),
    pages: counter(page).final().first(),
  )
  [#metadata(stats) <doc-stats>]
}

#context [#metadata(counter(page).final().first()) <page-count>]
