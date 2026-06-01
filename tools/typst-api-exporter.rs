//! Export Typst's current standard-library API as normalized JSON.
//!
//! This file is copied into an upstream `typst/typst` checkout as
//! `docs/src/bin/export-api.rs` and compiled as part of the `typst-docs`
//! package. Keeping it in this repository lets CI use upstream `main` without
//! maintaining a fork.

use std::collections::BTreeSet;
use std::env;
use std::fs;
use std::path::PathBuf;

use serde::Serialize;
use typst::foundations::{
    CastInfo, Func, NativeParamInfo, Repr, Scope, Symbol, Type, Value,
};
use typst::{Features, Library, LibraryExt};
use typst_library::Category;

#[derive(Debug, Serialize)]
struct ApiEntry {
    name: String,
    category: String,
    kind: String,
    oneliner: String,
    params: Vec<ApiParam>,
    returns: Vec<String>,
    route: String,
    weight: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    value: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    contextual: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    element: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    deprecated: Option<String>,
}

#[derive(Debug, Serialize)]
struct ApiParam {
    name: String,
    types: Vec<String>,
    required: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    default: Option<String>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    strings: Vec<String>,
}

fn main() {
    let out = parse_out_arg();
    let entries = export_entries();
    write_entries(&out, &entries);
}

fn parse_out_arg() -> PathBuf {
    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        if arg == "--out" {
            return args
                .next()
                .map(PathBuf::from)
                .unwrap_or_else(|| usage("--out requires a path"));
        }
        if let Some(path) = arg.strip_prefix("--out=") {
            return PathBuf::from(path);
        }
        usage(&format!("unexpected argument: {arg}"));
    }
    usage("missing --out");
}

fn usage(message: &str) -> ! {
    eprintln!("{message}");
    eprintln!("usage: export-api --out <path>");
    std::process::exit(2);
}

fn write_entries(out: &PathBuf, entries: &[ApiEntry]) {
    if let Some(parent) = out.parent() {
        fs::create_dir_all(parent).expect("create output directory");
    }
    let data = serde_json::to_vec(entries).expect("serialize API entries");
    fs::write(out, data).expect("write API entries");
    eprintln!("wrote {} entries to {}", entries.len(), out.display());
}

fn export_entries() -> Vec<ApiEntry> {
    let library = Library::builder().with_features(Features::all()).build();
    let mut entries = Vec::new();
    collect_scope(library.global.scope(), None, "", &mut entries);
    entries
}

fn collect_scope(
    scope: &Scope,
    inherited_category: Option<Category>,
    prefix: &str,
    entries: &mut Vec<ApiEntry>,
) {
    for (name, binding) in scope.iter() {
        let value = binding.read();
        let category = binding.category().or(inherited_category);
        let path = join_path(prefix, name.as_str());

        match value {
            Value::Func(func) => {
                if let Some(category) = category {
                    push_func(entries, &path, category, "function", func, None);
                }
            }
            Value::Type(ty) => {
                if let Some(category) = category {
                    push_type(entries, &path, category, ty);
                }
            }
            Value::Symbol(symbol) => {
                if path.starts_with("sym.") || path.starts_with("emoji.") {
                    push_symbol(entries, &path, symbol);
                }
            }
            Value::Module(module) => {
                collect_scope(module.scope(), category, &path, entries);
            }
            _ => {}
        }
    }
}

fn push_type(entries: &mut Vec<ApiEntry>, path: &str, category: Category, ty: &Type) {
    let name = ty.short_name().to_string();
    let route = route_for_top_level(category, path);
    entries.push(ApiEntry {
        name: name.clone(),
        category: category_title(category).to_string(),
        kind: "type".to_string(),
        oneliner: oneliner(ty.docs()),
        params: vec![],
        returns: vec![],
        route: route.clone(),
        weight: category_weight(category),
        value: None,
        contextual: None,
        element: None,
        deprecated: None,
    });

    if let Ok(constructor) = ty.constructor() {
        push_func(entries, &name, category, "constructor", &constructor, Some(&route));
    }

    push_scoped_defs(entries, &name, category, ty.scope(), &route);
}

fn push_func(
    entries: &mut Vec<ApiEntry>,
    path: &str,
    category: Category,
    kind: &str,
    func: &Func,
    route_override: Option<&str>,
) {
    let route = route_override
        .map(str::to_string)
        .unwrap_or_else(|| route_for_func(category, path));
    let entry_name = if kind == "constructor" {
        path.to_string()
    } else {
        path.to_string()
    };
    entries.push(ApiEntry {
        name: entry_name.clone(),
        category: category_title(category).to_string(),
        kind: kind.to_string(),
        oneliner: func.docs().map(oneliner).unwrap_or_default(),
        params: func
            .params()
            .filter_map(|param| param.to_native().map(param_info))
            .collect(),
        returns: func.returns().map(cast_types).unwrap_or_default(),
        route: route.clone(),
        weight: category_weight(category),
        value: None,
        contextual: func.contextual().filter(|value| *value),
        element: func.to_element().map(|_| true),
        deprecated: None,
    });

    if kind != "method" {
        if let Some(scope) = func.scope() {
            push_scoped_defs(entries, &entry_name, category, scope, &route);
        }
    }
}

fn push_scoped_defs(
    entries: &mut Vec<ApiEntry>,
    parent: &str,
    category: Category,
    scope: &Scope,
    route: &str,
) {
    for (name, binding) in scope.iter() {
        if let Value::Func(func) = binding.read() {
            let full_name = format!("{parent}.{name}");
            push_func(entries, &full_name, category, "method", func, Some(route));
        }
    }
}

fn push_symbol(entries: &mut Vec<ApiEntry>, path: &str, symbol: &Symbol) {
    let mut seen = BTreeSet::new();
    for (modifiers, value, _) in symbol.variants() {
        let symbol_base = path
            .strip_prefix("sym.")
            .or_else(|| path.strip_prefix("emoji."))
            .unwrap_or(path);
        let suffix = modifiers
            .into_iter()
            .filter(|modifier| !modifier.is_empty())
            .collect::<Vec<_>>()
            .join(".");
        let name = if suffix.is_empty() {
            symbol_base.to_string()
        } else {
            format!("{symbol_base}.{suffix}")
        };
        if !seen.insert(name.clone()) {
            continue;
        }
        entries.push(ApiEntry {
            name: format!("sym.{name}"),
            category: "Symbols".to_string(),
            kind: "symbol".to_string(),
            oneliner: format!("{value}  (sym.{name})"),
            params: vec![],
            returns: vec![],
            route: symbol_route(path),
            weight: category_weight(Category::Symbols),
            value: Some(value.to_string()),
            contextual: None,
            element: None,
            deprecated: None,
        });
    }
}

fn param_info(param: &NativeParamInfo) -> ApiParam {
    ApiParam {
        name: param.name.to_string(),
        types: cast_types(&param.input),
        required: param.required,
        default: param.default.map(|make| make().repr().to_string()),
        strings: cast_strings(&param.input),
    }
}

fn cast_types(info: &CastInfo) -> Vec<String> {
    let mut values = Vec::new();
    collect_cast_types(info, &mut values);
    dedup(values)
}

fn collect_cast_types(info: &CastInfo, values: &mut Vec<String>) {
    match info {
        CastInfo::Any => values.push("any".to_string()),
        CastInfo::Value(value, _) => values.push(value.ty().short_name().to_string()),
        CastInfo::Type(ty) => values.push(ty.short_name().to_string()),
        CastInfo::Union(infos) => {
            for info in infos {
                collect_cast_types(info, values);
            }
        }
    }
}

fn cast_strings(info: &CastInfo) -> Vec<String> {
    let mut values = Vec::new();
    collect_cast_strings(info, &mut values);
    dedup(values)
}

fn collect_cast_strings(info: &CastInfo, values: &mut Vec<String>) {
    match info {
        CastInfo::Value(Value::Str(value), _) => values.push(value.to_string()),
        CastInfo::Union(infos) => {
            for info in infos {
                collect_cast_strings(info, values);
            }
        }
        _ => {}
    }
}

fn dedup(values: Vec<String>) -> Vec<String> {
    let mut seen = BTreeSet::new();
    values
        .into_iter()
        .filter(|value| seen.insert(value.clone()))
        .collect()
}

fn oneliner(docs: &str) -> String {
    let first = docs
        .split("\n\n")
        .next()
        .unwrap_or("")
        .lines()
        .map(str::trim)
        .collect::<Vec<_>>()
        .join(" ");
    strip_markdown(&first)
}

fn strip_markdown(text: &str) -> String {
    text.replace('`', "")
        .replace('[', "")
        .replace(']', "")
        .replace('*', "")
        .replace('_', "")
        .trim()
        .to_string()
}

fn join_path(prefix: &str, name: &str) -> String {
    if prefix.is_empty() {
        name.to_string()
    } else {
        format!("{prefix}.{name}")
    }
}

fn route_for_func(category: Category, path: &str) -> String {
    let parts = path.split('.').collect::<Vec<_>>();
    let page = if parts.len() == 1 {
        parts[0]
    } else if category_slug(category) == parts[0] && parts.len() > 1 {
        parts[1]
    } else {
        parts[0]
    };
    format!("/reference/{}/{}/", category_slug(category), page)
}

fn route_for_top_level(category: Category, path: &str) -> String {
    let first = path.split('.').next().unwrap_or(path);
    let page = if category_slug(category) == first {
        path.split('.').nth(1).unwrap_or(first)
    } else {
        first
    };
    format!("/reference/{}/{}/", category_slug(category), page)
}

fn symbol_route(path: &str) -> String {
    if path.starts_with("emoji.") {
        "/reference/symbols/emoji/".to_string()
    } else {
        "/reference/symbols/sym/".to_string()
    }
}

fn category_slug(category: Category) -> &'static str {
    category.name()
}

fn category_title(category: Category) -> &'static str {
    match category {
        Category::Foundations => "Foundations",
        Category::Introspection => "Introspection",
        Category::Layout => "Layout",
        Category::DataLoading => "Data Loading",
        Category::Math => "Math",
        Category::Model => "Model",
        Category::Symbols => "Symbols",
        Category::Text => "Text",
        Category::Visualize => "Visualize",
        Category::Pdf => "PDF",
        Category::Html => "HTML",
        Category::Svg => "SVG",
        Category::Png => "PNG",
        Category::Bundle => "Bundle",
    }
}

fn category_weight(category: Category) -> f64 {
    match category {
        Category::Foundations
        | Category::Introspection
        | Category::Layout
        | Category::DataLoading
        | Category::Math
        | Category::Model
        | Category::Text
        | Category::Visualize => 1.5,
        Category::Symbols => 1.0,
        Category::Pdf => 0.5,
        Category::Html => 0.3,
        Category::Svg | Category::Png | Category::Bundle => 1.0,
    }
}
