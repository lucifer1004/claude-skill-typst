// Box components: note, callout

/// Creates a styled note box.
///
/// - body (content): The content to display
/// - type (string): Box type - "info", "warning", "error", or "tip"
/// - title (content, none): Optional title for the box
/// -> content
#let note(body, type: "info", title: none) = {
  let styles = (
    info: (fill: rgb("#e0f2fe"), border: rgb("#0ea5e9"), icon: "ℹ"),
    warning: (fill: rgb("#fef3c7"), border: rgb("#f59e0b"), icon: "⚠"),
    error: (fill: rgb("#fee2e2"), border: rgb("#ef4444"), icon: "✕"),
    tip: (fill: rgb("#dcfce7"), border: rgb("#22c55e"), icon: "✓"),
  )

  let style = styles.at(type, default: styles.info)

  block(
    fill: style.fill,
    stroke: (left: 3pt + style.border),
    inset: 1em,
    radius: (right: 4pt),
    width: 100%,
  )[
    #if title != none {
      text(weight: "bold")[#style.icon #title]
      v(0.3em)
    }
    #body
  ]
}

/// Creates a callout box with a colored header.
///
/// - body (content): The content to display
/// - title (content): The callout title
/// - color (color): Header background color
/// -> content
#let callout(body, title: [Note], color: rgb("#3b82f6")) = {
  block(
    stroke: 1pt + color,
    radius: 4pt,
    width: 100%,
    clip: true,
  )[
    #block(
      fill: color,
      width: 100%,
      inset: 0.7em,
    )[
      #text(fill: white, weight: "bold")[#title]
    ]
    #block(
      inset: 1em,
      width: 100%,
    )[#body]
  ]
}
