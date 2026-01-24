# Typst Package Development

For Typst language basics (syntax, types, functions), see [basics.md](basics.md).

**Complete example**: See [examples/package-example/](examples/package-example/) for a minimal publishable package with submodules.

## Package Structure

```
my-package/
├── typst.toml       # Package manifest (required)
├── lib.typ          # Public API entrypoint
├── src/             # Internal modules
│   ├── core.typ
│   └── utils.typ
├── LICENSE
└── README.md
```

## typst.toml Manifest

```toml
[package]
name = "my-package"
version = "0.1.0"
entrypoint = "lib.typ"
authors = ["Your Name <@github-username>"]
license = "MIT"
description = "Short description"
repository = "https://github.com/user/my-package"
keywords = ["keyword1", "keyword2"]
categories = ["utility"]
compiler = "0.12.0"
exclude = ["tests/*", "docs/*"]
```

### Optional Template Section

```toml
[template]
path = "template"
entrypoint = "main.typ"
thumbnail = "thumbnail.png"
```

### Valid Categories

| Type     | Categories                                                                                             |
| -------- | ------------------------------------------------------------------------------------------------------ |
| Document | `book`, `report`, `paper`, `thesis`, `poster`, `flyer`, `presentation`, `cv`, `office`                 |
| Function | `components`, `visualization`, `model`, `layout`, `text`, `scripting`, `integration`, `utility`, `fun` |

## Module System

### Import Syntax

```typst
// From Typst Universe
#import "@preview/package:0.1.0": func1, func2
#import "@preview/package:0.1.0": *

// From local file
#import "src/core.typ": main-func
#import "utils.typ": long-name as short
```

### Entrypoint Pattern (lib.typ)

```typst
// Re-export public API only
#import "src/core.typ": main-func, Config
#import "src/utils.typ": helper
```

### Path Resolution in Packages

**Important**: Inside a package, the root path (`/`) resolves to the **package directory itself**, not the user's project root.

```typst
// Package structure:
// my-package/
// ├── lib.typ (entrypoint)
// └── src/
//     ├── core.typ
//     └── assets/
//         └── icon.svg

// In lib.typ:
#import "/src/core.typ": *     // ✅ Resolves to my-package/src/core.typ

// In src/core.typ:
#import "/src/assets/icon.svg" // ✅ Resolves to my-package/src/assets/icon.svg
#import "assets/icon.svg"      // ✅ Same result (relative to core.typ)
```

This isolation ensures packages are self-contained and don't depend on the user's file structure.

Modules must form a DAG (no circular imports).

## API Design

### Function Documentation

```typst
/// Creates a styled note box.
/// - body (content): The content to display
/// - type (string): "info", "warning", or "error"
/// -> content
#let note(body, type: "info") = { ... }
```

### Configuration Pattern

```typst
#let default-config = (color: blue, size: 12pt)

#let configure(..overrides) = {
  let cfg = default-config
  for (k, v) in overrides.named() { cfg.insert(k, v) }
  cfg
}
```

## Local Development

### Local Package Path

| OS          | Path                                   |
| ----------- | -------------------------------------- |
| Linux/macOS | `~/.local/share/typst/packages/local/` |
| Windows     | `%APPDATA%\typst\packages\local\`      |

Install locally:

```bash
mkdir -p ~/.local/share/typst/packages/local/my-package/0.1.0
cp -r . ~/.local/share/typst/packages/local/my-package/0.1.0/
```

### Testing Locally

```typst
#import "@local/my-package:0.1.0": *
#my-func(test-input)
```

## Publishing

### To Typst Universe

1. Fork https://github.com/typst/packages
2. Add package to `packages/preview/my-package/0.1.0/`
3. Create pull request

### Versioning

| Change                    | Version           |
| ------------------------- | ----------------- |
| Bug fixes                 | `0.1.0` → `0.1.1` |
| New features (compatible) | `0.1.0` → `0.2.0` |
| Breaking changes          | `0.1.0` → `1.0.0` |

### Checklist

- [ ] `typst.toml` complete
- [ ] `entrypoint` file exports public API
- [ ] `LICENSE` included
- [ ] `README.md` with usage examples
- [ ] Package compiles without errors

## Best Practices

1. **Minimal exports**: Only expose what users need
2. **Sensible defaults**: All optional parameters have defaults
3. **Document API**: Use `///` comments for all public functions
4. **Semantic versioning**: Follow semver strictly
5. **No breaking changes**: Deprecate before removing
