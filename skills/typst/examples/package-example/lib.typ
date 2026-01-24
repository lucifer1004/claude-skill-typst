// Example Utils Package
// A minimal example package demonstrating Typst package structure

// === Re-exports from submodules ===
#import "src/boxes.typ": callout, note
#import "src/formatting.typ": badge, iso-date

// === Package-level functions ===

/// Creates a horizontal divider line.
///
/// - width (length): Line width (default: 100%)
/// - stroke (stroke): Line style (default: 0.5pt + gray)
/// -> content
#let divider(width: 100%, stroke: 0.5pt + luma(180)) = {
  v(0.5em)
  line(length: width, stroke: stroke)
  v(0.5em)
}

/// Wraps content in a centered block with optional width.
///
/// - body (content): Content to center
/// - width (length): Container width (default: auto)
/// -> content
#let centered(body, width: auto) = {
  align(center, block(width: width, body))
}
