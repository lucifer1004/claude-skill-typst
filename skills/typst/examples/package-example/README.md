# example-utils

A minimal example Typst package demonstrating package structure and conventions.

## Installation

### Local Development

Copy to your local packages directory:

```bash
# Linux/macOS
mkdir -p ~/.local/share/typst/packages/local/example-utils/0.1.0
cp -r . ~/.local/share/typst/packages/local/example-utils/0.1.0/

# Then import in your document
#import "@local/example-utils:0.1.0": *
```

### From Typst Universe (after publishing)

```typst
#import "@preview/example-utils:0.1.0": *
```

## Usage

```typst
#import "@local/example-utils:0.1.0": note, callout, badge, iso-date, divider

// Note boxes
#note[This is an info note.]
#note(type: "warning")[Be careful!]
#note(type: "error", title: "Error")[Something went wrong.]
#note(type: "tip", title: "Pro Tip")[This is helpful.]

// Callout box
#callout(title: "Important")[
  This is a callout with a colored header.
]

// Badge
Status: #badge[Active] #badge(color: red)[Deprecated]

// Date formatting
Today: #iso-date(datetime.today())

// Divider
#divider()
```

## API Reference

### `note(body, type: "info", title: none)`

Creates a styled note box.

- `body`: Content to display
- `type`: One of "info", "warning", "error", "tip"
- `title`: Optional title

### `callout(body, title: [Note], color: rgb("#3b82f6"))`

Creates a callout box with colored header.

### `badge(label, color: rgb("#3b82f6"), text-color: white)`

Creates a colored badge/tag.

### `iso-date(d)`

Formats a datetime as YYYY-MM-DD.

### `divider(width: 100%, stroke: 0.5pt + gray)`

Creates a horizontal divider line.

## Package Structure

```
example-utils/
├── typst.toml      # Package manifest
├── lib.typ         # Public API entrypoint
├── README.md       # Documentation
└── src/
    ├── boxes.typ       # Box components (note, callout)
    └── formatting.typ  # Formatting utilities (badge, iso-date)
```

## License

MIT
