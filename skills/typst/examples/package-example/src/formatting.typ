// Formatting utilities: dates, badges

/// Formats a datetime in ISO format (YYYY-MM-DD).
///
/// - d (datetime): The date to format
/// -> string
#let iso-date(d) = {
  d.display("[year]-[month padding:zero]-[day padding:zero]")
}

/// Creates a colored badge/tag.
///
/// - text (string, content): Badge text
/// - color (color): Background color (default: blue)
/// - text-color (color): Text color (default: white)
/// -> content
#let badge(label, color: rgb("#3b82f6"), text-color: white) = {
  box(
    fill: color,
    inset: (x: 0.5em, y: 0.25em),
    radius: 3pt,
  )[
    #text(fill: text-color, size: 0.85em, weight: "medium")[#label]
  ]
}

/// Formats a keyboard shortcut.
///
/// - keys (string): Keyboard shortcut (e.g., "Ctrl+S")
/// -> content
#let kbd(keys) = {
  let parts = keys.split("+")
  parts
    .map(k => box(
      fill: luma(240),
      stroke: 0.5pt + luma(200),
      inset: (x: 0.4em, y: 0.2em),
      radius: 3pt,
    )[#text(size: 0.9em, font: "monospace")[#k]])
    .join([+])
}
