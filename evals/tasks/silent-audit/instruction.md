# Task

You are given a draft paper at `/app/draft.typ`. It compiles without errors,
but a careful review of the **rendered output** may reveal defects that compile
cleanly yet look wrong in the PDF.

Do a rendering QA pass:

1. Inspect the rendered output (do not rely on reading the source alone).
2. Fix every rendering defect you find, without changing the intended wording
   or the intended math.
3. Do not "fix" constructs that already render correctly.
4. Save the corrected source as `/app/main.typ` and compile it to
   `/app/main.pdf`.
