# Task

Build a reusable Typst conference-paper template and demonstrate it.

Requirements:

1. Create `/app/conf.typ` defining a template function `conf-paper(title:, authors:, body)` that:
   - sets A4 pages with 2cm margins,
   - renders the title centered in 17pt bold and the author list centered below it,
   - typesets the body in two columns with 10pt text,
   - shows the current top-level section title in the page header (dynamic per page),
   - numbers pages "1 / N" in the footer.
2. Create `/app/demo.typ` that imports the template from `conf.typ` and produces
   a demo paper with at least two level-1 sections.
3. Compile `/app/demo.typ` to `/app/demo.pdf`.
