# Typst Package Development

For Typst language basics (syntax, functions), see [basics.md](basics.md). For types and operators, see [types.md](types.md).

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

For configuration patterns (default dictionaries, overrides), see [template.md](template.md).

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

### Visual Regression Testing with tytanic

[tytanic](https://github.com/typst-community/tytanic) (`tt`) compiles test files, renders pages to PNG, and diffs against stored references.

```bash
cargo install tytanic
```

Directory layout:

```
my-package/
├── typst.toml
├── lib.typ
└── tests/
    └── basic/
        ├── test.typ       # test document
        └── ref/
            └── 1.png      # reference image (one per page)
```

Test file (`tests/basic/test.typ`):

```typst
#import "/lib.typ": *
#my-func("test input")
```

Commands:

```bash
tt run                  # compile and compare all tests against refs
tt run basic            # run a specific test
tt update               # accept current output as new references
tt list                 # list discovered tests
```

Commit `ref/` images to version control so CI can detect regressions. See the [tytanic guide](https://typst-community.github.io/tytanic/) for ephemeral references and advanced test modes.

### Formatting with typstyle

```bash
cargo install typstyle
typstyle -i lib.typ src/*.typ       # format in place
typstyle --check lib.typ src/*.typ  # CI check (exit 1 if unformatted)
```

## Publishing

### Validate with typst-package-check

Run the [official validator](https://github.com/typst/package-check) before submitting to Typst Universe:

```bash
cargo install typst-package-check
typst-package-check check .
```

Checks: `typst.toml` schema, entrypoint exists, package compiles, license valid, file size limits.

### To Typst Universe

1. Run `typst-package-check check .` and fix any errors
2. Fork https://github.com/typst/packages
3. Add package to `packages/preview/my-package/0.1.0/`
4. Create pull request

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
- [ ] `typst-package-check check .` passes
- [ ] `typstyle --check` passes
- [ ] `tt run` passes (if visual tests exist)

## Best Practices

1. **Minimal exports**: Only expose what users need
2. **Sensible defaults**: All optional parameters have defaults
3. **Document API**: Use `///` comments for all public functions
4. **Semantic versioning**: Follow semver strictly
5. **No breaking changes**: Deprecate before removing
