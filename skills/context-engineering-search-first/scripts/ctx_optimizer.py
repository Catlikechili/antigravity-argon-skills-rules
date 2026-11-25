#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Antigravity AST Codebase Map & Context Optimizer (ctx_optimizer.py)
-------------------------------------------------------------------
Inspired by Aider RepoMap, Repomix (--compress), and Tree-sitter AST Skeletons.
100% Local, Zero-Dependency (Python Standard Library), Cross-Platform, UTF-8/cp1252 Safe.
Reduces codebase context tokens by 80% - 95% for Free & Small-Context LLMs.

Usage:
  python ctx_optimizer.py --root "d:/Gravity" --mode map --out "d:/Gravity/CODEBASE_MAP.md" --budget 3000
  python ctx_optimizer.py --root "d:/Gravity" --mode skeleton --target "path/to/file_or_dir"
  python ctx_optimizer.py --root "d:/Gravity" --mode search --query "function_or_class_name"
"""

import argparse
import ast
import fnmatch
import io
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Force UTF-8 on Windows stdio to prevent cp1252 UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_IGNORE_DIRS = {
    ".git", ".svn", ".hg", ".vscode", ".idea", "__pycache__",
    "node_modules", "bower_components", "venv", ".venv", "env",
    "dist", "build", "out", "target", "bin", "obj", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "brain", "conversations", "crashes",
    "daemon", "cache", "presence", "annotations"
}

DEFAULT_IGNORE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".dylib", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp4", ".mp3", ".wav", ".ogg", ".zip", ".tar", ".gz", ".7z", ".rar",
    ".pdf", ".docx", ".xlsx", ".pptx", ".db", ".sqlite", ".sqlite3",
    ".pb", ".pbtxt", ".woff", ".woff2", ".ttf", ".eot", ".lock", ".map"
}

SECRET_PATTERNS = [
    "*secret*", "*credential*", "*oauth*", "*.pem", "*.key", ".env", ".env.*"
]

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs",
    ".cs", ".cpp", ".c", ".h", ".hpp", ".java", ".go", ".rs",
    ".ps1", ".sh", ".bat", ".sql", ".tex", ".md", ".json", ".yaml", ".yml"
}


def safe_read_text(file_path: Path, max_bytes: int = 512_000) -> Optional[str]:
    """Safely read text file across UTF-8, UTF-8-SIG, UTF-16, and CP1252 without crashing."""
    try:
        size = file_path.stat().st_size
        if size == 0 or size > max_bytes:
            return None
        raw = file_path.read_bytes()
        if b"\x00" in raw[:1024]:
            # Check if UTF-16
            try:
                return raw.decode("utf-16")
            except Exception:
                return None  # Binary file
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return None


def estimate_tokens(text: str) -> int:
    """Fast token approximation (~4 chars per token)."""
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def load_ignore_patterns(root: Path) -> List[str]:
    """Load ignore globs from .gitignore and .contextignore."""
    patterns: List[str] = list(SECRET_PATTERNS)
    for ignore_file in (".gitignore", ".contextignore", ".repomixignore", ".cursorignore"):
        p = root / ignore_file
        if p.is_file():
            content = safe_read_text(p)
            if content:
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line.rstrip("/"))
    return patterns


def is_ignored(rel_path: str, name: str, is_dir: bool, patterns: List[str], include_agents: bool = False) -> bool:
    """Check if path should be excluded from context indexing."""
    if is_dir:
        if name in DEFAULT_IGNORE_DIRS:
            return True
        if name == ".agents" and not include_agents:
            return True
    else:
        ext = os.path.splitext(name)[1].lower()
        if ext in DEFAULT_IGNORE_EXTS or name.endswith(".min.js") or name.endswith(".min.css"):
            return True
        if name in ("CODEBASE_MAP.md", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"):
            return True

    rel_norm = rel_path.replace("\\", "/")
    for pat in patterns:
        if pat == ".agents" and include_agents:
            continue
        if fnmatch.fnmatch(name.lower(), pat.lower()) or fnmatch.fnmatch(rel_norm.lower(), pat.lower()):
            return True
        if "/" in pat and rel_norm.lower().startswith(pat.lower().lstrip("/") + "/"):
            return True
    return False


class SymbolItem:
    def __init__(self, kind: str, name: str, signature: str, start_line: int, end_line: int, doc: str = ""):
        self.kind = kind
        self.name = name
        self.signature = signature
        self.start_line = start_line
        self.end_line = end_line
        self.doc = doc

    def format_compact(self) -> str:
        loc = f"L{self.start_line}-L{self.end_line}" if self.end_line > self.start_line else f"L{self.start_line}"
        doc_part = f"  # {self.doc}" if self.doc else ""
        return f"[{loc}] {self.signature}{doc_part}"


def _format_py_args(args: ast.arguments) -> str:
    parts = []
    total_pos = len(args.args)
    num_defaults = len(args.defaults)
    for i, arg in enumerate(args.args):
        s = arg.arg
        if arg.annotation:
            try:
                s += f": {ast.unparse(arg.annotation)}"
            except Exception:
                pass
        if i >= total_pos - num_defaults:
            s += "=..."
        parts.append(s)
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return ", ".join(parts)


def parse_python_ast(content: str) -> Tuple[List[str], List[SymbolItem]]:
    """Extract imports and class/function AST skeletons with exact line ranges from Python code."""
    imports: List[str] = []
    symbols: List[SymbolItem] = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return parse_generic_regex(content, ".py")

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports.append(mod)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            arg_str = _format_py_args(node.args)
            ret_str = ""
            if node.returns:
                try:
                    ret_str = f" -> {ast.unparse(node.returns)}"
                except Exception:
                    pass
            doc = (ast.get_docstring(node) or "").strip().splitlines()[0][:70] if ast.get_docstring(node) else ""
            sig = f"{prefix} {node.name}({arg_str}){ret_str}: ..."
            end_l = getattr(node, "end_lineno", node.lineno)
            symbols.append(SymbolItem("function", node.name, sig, node.lineno, end_l, doc))
        elif isinstance(node, ast.ClassDef):
            bases = []
            for b in node.bases:
                try:
                    bases.append(ast.unparse(b))
                except Exception:
                    pass
            base_str = f"({', '.join(bases)})" if bases else ""
            doc = (ast.get_docstring(node) or "").strip().splitlines()[0][:70] if ast.get_docstring(node) else ""
            sig = f"class {node.name}{base_str}:"
            end_l = getattr(node, "end_lineno", node.lineno)
            symbols.append(SymbolItem("class", node.name, sig, node.lineno, end_l, doc))
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    prefix = "async def" if isinstance(sub, ast.AsyncFunctionDef) else "def"
                    arg_str = _format_py_args(sub.args)
                    ret_str = ""
                    if sub.returns:
                        try:
                            ret_str = f" -> {ast.unparse(sub.returns)}"
                        except Exception:
                            pass
                    sub_doc = (ast.get_docstring(sub) or "").strip().splitlines()[0][:55] if ast.get_docstring(sub) else ""
                    sub_sig = f"  .{sub.name}({arg_str}){ret_str}"
                    sub_end = getattr(sub, "end_lineno", sub.lineno)
                    symbols.append(SymbolItem("method", f"{node.name}.{sub.name}", sub_sig, sub.lineno, sub_end, sub_doc))
    return imports[:15], symbols


REGEX_PATTERNS = {
    "js_ts": [
        ("import", re.compile(r'^\s*import\s+.*?from\s+[\'"]([^\'"]+)[\'"]')),
        ("class", re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_$]+)(?:[^{]*)')),
        ("interface", re.compile(r'^\s*(?:export\s+)?(?:interface|type)\s+([A-Za-z0-9_$]+)')),
        ("function", re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\([^)]*\)')),
        ("const_fn", re.compile(r'^\s*(?:export\s+)?const\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z0-9_$]+)\s*=>')),
    ],
    "c_family": [
        ("import", re.compile(r'^\s*(?:#include|using|import|package)\s+([<"\'A-Za-z0-9_./\\]+)')),
        ("class", re.compile(r'^\s*(?:public\s+|private\s+|internal\s+|abstract\s+|sealed\s+|final\s+)*(?:class|struct|interface|enum|trait|impl)\s+([A-Za-z0-9_<>]+)')),
        ("function", re.compile(r'^\s*(?:pub\s+|public\s+|private\s+|protected\s+|static\s+|virtual\s+|async\s+|fn\s+|func\s+)*(?:[A-Za-z0-9_<>:*&]+\s+)+([A-Za-z0-9_]+)\s*\([^;]*\)\s*(?:\{|->|where|$)')),
    ],
    "powershell": [
        ("function", re.compile(r'^\s*(?:function|filter|workflow)\s+([A-Za-z0-9_-]+)', re.IGNORECASE)),
    ],
    "markdown": [
        ("heading", re.compile(r'^(#{1,3})\s+(.+)$')),
    ],
    "latex": [
        ("section", re.compile(r'^\s*\\(part|chapter|section|subsection|subsubsection)\*?\{([^}]+)\}')),
        ("include", re.compile(r'^\s*\\(?:input|include|bibliography)\{([^}]+)\}')),
    ],
}


def parse_generic_regex(content: str, ext: str) -> Tuple[List[str], List[SymbolItem]]:
    """Multi-language structural skeleton parser for JS/TS, C/C++/C#/Go/Rust/Java, PS1, MD, LaTeX."""
    imports: List[str] = []
    symbols: List[SymbolItem] = []
    lines = content.splitlines()

    if ext in (".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs"):
        rules = REGEX_PATTERNS["js_ts"]
    elif ext in (".cs", ".cpp", ".c", ".h", ".hpp", ".java", ".go", ".rs"):
        rules = REGEX_PATTERNS["c_family"]
    elif ext == ".ps1":
        rules = REGEX_PATTERNS["powershell"]
    elif ext == ".md":
        rules = REGEX_PATTERNS["markdown"]
    elif ext == ".tex":
        rules = [
            ("section", re.compile(r'^\s*\\(part|chapter|section|subsection)\*?\{([^}]+)\}')),
            ("import", re.compile(r'^\s*\\(?:input|include|bibliography)\{([^}]+)\}')),
        ]
    else:
        rules = []

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("//") or line.startswith("#!"):
            continue
        for kind, regex in rules:
            m = regex.match(raw_line)
            if m:
                if kind == "import":
                    imports.append(m.group(1).strip())
                elif kind == "heading":
                    hashes, title = m.group(1), m.group(2).strip()
                    symbols.append(SymbolItem("heading", title, f"{hashes} {title}", idx, idx))
                elif kind == "section":
                    sec_type, title = m.group(1), m.group(2).strip()
                    symbols.append(SymbolItem("section", title, f"\\{sec_type}{{{title}}}", idx, idx))
                else:
                    name = m.group(1).strip()
                    sig = re.sub(r"\s+", " ", line.rstrip("{")).strip()
                    if len(sig) > 95:
                        sig = sig[:92] + "..."
                    symbols.append(SymbolItem(kind, name, sig, idx, idx))
                break
    return imports[:15], symbols


class FileAnalysis:
    def __init__(self, rel_path: str, ext: str, lines_count: int, raw_tokens: int, imports: List[str], symbols: List[SymbolItem]):
        self.rel_path = rel_path
        self.ext = ext
        self.lines_count = lines_count
        self.raw_tokens = raw_tokens
        self.imports = imports
        self.symbols = symbols
        self.score = 1.0


def scan_workspace(root: Path, include_agents: bool = False, max_files: int = 600) -> List[FileAnalysis]:
    """Scan workspace, extract AST skeletons, and rank files by structural importance."""
    patterns = load_ignore_patterns(root)
    results: List[FileAnalysis] = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""

        # Prune ignored directories in-place
        dirnames[:] = [
            d for d in sorted(dirnames)
            if not is_ignored(os.path.join(rel_dir, d) if rel_dir else d, d, True, patterns, include_agents)
        ]

        for fname in sorted(filenames):
            rel_file = os.path.join(rel_dir, fname) if rel_dir else fname
            if is_ignored(rel_file, fname, False, patterns, include_agents):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CODE_EXTENSIONS:
                continue

            fpath = Path(dirpath) / fname
            content = safe_read_text(fpath)
            if content is None:
                continue

            lines_count = len(content.splitlines())
            raw_tokens = estimate_tokens(content)

            if ext == ".py":
                imports, symbols = parse_python_ast(content)
            else:
                imports, symbols = parse_generic_regex(content, ext)

            results.append(FileAnalysis(rel_file.replace("\\", "/"), ext, lines_count, raw_tokens, imports, symbols))
            if len(results) >= max_files:
                break
        if len(results) >= max_files:
            break

    # Compute lightweight centrality score (Aider RepoMap style)
    stem_to_file: Dict[str, str] = {}
    for fa in results:
        stem = os.path.splitext(os.path.basename(fa.rel_path))[0].lower()
        if stem not in ("index", "__init__", "main", "utils"):
            stem_to_file[stem] = fa.rel_path

    inbound_refs: Dict[str, int] = defaultdict(int)
    for fa in results:
        for imp in fa.imports:
            imp_tail = imp.split(".")[-1].split("/")[-1].lower()
            if imp_tail in stem_to_file and stem_to_file[imp_tail] != fa.rel_path:
                inbound_refs[stem_to_file[imp_tail]] += 1

    for fa in results:
        code_bonus = 2.0 if fa.ext not in (".md", ".json", ".yaml", ".yml") else 0.6
        symbol_density = min(3.0, len(fa.symbols) * 0.25)
        ref_bonus = inbound_refs[fa.rel_path] * 1.5
        fa.score = (1.0 + symbol_density + ref_bonus) * code_bonus

    return results


def generate_codebase_map(root: Path, analyses: List[FileAnalysis], token_budget: int = 3000) -> str:
    """Render ultra-compact CODEBASE_MAP.md within token_budget."""
    total_raw_tokens = sum(a.raw_tokens for a in analyses)
    total_lines = sum(a.lines_count for a in analyses)

    out_lines = [
        f"# ⚡ AST CODEBASE MAP (`{root.name}`)",
        f"> **Auto-Generated by `ctx_optimizer.py`** | Files: `{len(analyses)}` | Raw Lines: `{total_lines:,}` | Raw Tokens: `~{total_raw_tokens:,}`",
        "> **How to use (Search-First Protocol):** Read exact `[Lstart-Lend]` coordinates below, then call `read_file` with `StartLine` and `EndLine` instead of reading full files.",
        "",
        "## 1. Directory & File Inventory",
    ]

    # Group by top-level folder
    by_folder: Dict[str, List[FileAnalysis]] = defaultdict(list)
    for fa in analyses:
        parts = fa.rel_path.split("/")
        top = parts[0] if len(parts) > 1 else "(root)"
        by_folder[top].append(fa)

    for folder in sorted(by_folder.keys()):
        files = by_folder[folder]
        folder_tokens = sum(f.raw_tokens for f in files)
        out_lines.append(f"- **`{folder}/`** ({len(files)} files, ~{folder_tokens:,} raw tokens)")

    out_lines.append("")
    out_lines.append("## 2. High-Priority AST Skeletons & Signatures")

    # Sort files by structural importance score descending
    ranked = sorted(analyses, key=lambda x: (-x.score, x.rel_path))
    current_tokens = estimate_tokens("\n".join(out_lines))

    for fa in ranked:
        if not fa.symbols and not fa.imports:
            continue
        header = f"\n### `{fa.rel_path}` ({fa.lines_count}L | ~{fa.raw_tokens}t)"
        block_lines = [header]
        if fa.imports:
            block_lines.append(f"- **deps:** `{', '.join(fa.imports[:8])}`")

        # Limit symbols per file based on remaining budget
        max_syms = 25 if fa.ext != ".md" else 8
        for sym in fa.symbols[:max_syms]:
            block_lines.append(f"  - `{sym.format_compact()}`")
        if len(fa.symbols) > max_syms:
            block_lines.append(f"  - `... (+{len(fa.symbols) - max_syms} more symbols)`")

        block_text = "\n".join(block_lines)
        block_toks = estimate_tokens(block_text)
        if current_tokens + block_toks > token_budget:
            out_lines.append(f"\n> *[Token budget ({token_budget}t) reached. Use `ctx_optimizer.py --mode skeleton --target <file>` for remaining files.]*")
            break
        out_lines.append(block_text)
        current_tokens += block_toks

    map_text = "\n".join(out_lines)
    map_tokens = estimate_tokens(map_text)
    savings_pct = round((1.0 - (map_tokens / max(1, total_raw_tokens))) * 100, 1) if total_raw_tokens > 0 else 0.0
    summary_line = f"\n---\n**⚡ Compression Summary:** Raw `~{total_raw_tokens:,}` tokens -> Compressed Map `~{map_tokens:,}` tokens (**Saved `{savings_pct}%`**)\n"
    return map_text + summary_line


def generate_target_skeleton(root: Path, target: str) -> str:
    """Generate full AST skeleton for a single file or sub-directory."""
    tpath = (root / target).resolve() if not os.path.isabs(target) else Path(target).resolve()
    if not tpath.exists():
        return f"[ERROR] Path not found: {target}"

    if tpath.is_file():
        content = safe_read_text(tpath, max_bytes=2_000_000)
        if content is None:
            return f"[ERROR] Unable to read text from: {tpath}"
        ext = tpath.suffix.lower()
        imports, symbols = parse_python_ast(content) if ext == ".py" else parse_generic_regex(content, ext)
        raw_t = estimate_tokens(content)
        lines = [f"# AST Skeleton: `{tpath.name}` ({len(content.splitlines())}L | ~{raw_t} raw tokens)"]
        if imports:
            lines.append(f"**Imports/Deps:** `{', '.join(imports)}`")
        for s in symbols:
            lines.append(f"- `{s.format_compact()}`")
        if not symbols:
            lines.append("*(No structural symbols extracted; inspect targeted line ranges directly)*")
        skel = "\n".join(lines)
        skel_t = estimate_tokens(skel)
        sav = round((1.0 - skel_t / max(1, raw_t)) * 100, 1)
        return skel + f"\n\n> Skeleton Tokens: `~{skel_t}` (Saved `{sav}%`)"
    else:
        analyses = scan_workspace(tpath, include_agents=True)
        return generate_codebase_map(tpath, analyses, token_budget=2500)


def search_symbols(analyses: List[FileAnalysis], query: str) -> str:
    """Locate exact symbol coordinates across all analyzed files."""
    q = query.lower().strip()
    matches = []
    for fa in analyses:
        if q in fa.rel_path.lower():
            matches.append(f"- **File Match:** `{fa.rel_path}` ({fa.lines_count}L)")
        for s in fa.symbols:
            if q in s.name.lower() or q in s.signature.lower():
                matches.append(f"- **`{fa.rel_path}`** -> `{s.format_compact()}`")
    if not matches:
        return f"No AST symbol matches found for query: `{query}`"
    return f"# 🔍 Symbol Coordinates for `{query}` ({len(matches)} matches)\n" + "\n".join(matches[:50])


def main():
    parser = argparse.ArgumentParser(description="Antigravity AST Codebase Map & Skeleton Optimizer")
    parser.add_argument("--root", type=str, default=".", help="Workspace root directory")
    parser.add_argument("--mode", type=str, choices=["map", "skeleton", "search"], default="map", help="Execution mode")
    parser.add_argument("--target", type=str, default="", help="Target file/folder for skeleton mode")
    parser.add_argument("--query", type=str, default="", help="Symbol query for search mode")
    parser.add_argument("--out", type=str, default="", help="Output file path (optional)")
    parser.add_argument("--budget", type=int, default=2500, help="Max token budget for map output")
    parser.add_argument("--include-agents", action="store_true", help="Include .agents skill folders in scan")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[ERROR] Root path does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "skeleton":
        if not args.target:
            print("[ERROR] --target is required for --mode skeleton", file=sys.stderr)
            sys.exit(1)
        output = generate_target_skeleton(root, args.target)
    elif args.mode == "search":
        if not args.query:
            print("[ERROR] --query is required for --mode search", file=sys.stderr)
            sys.exit(1)
        analyses = scan_workspace(root, include_agents=args.include_agents)
        output = search_symbols(analyses, args.query)
    else:
        analyses = scan_workspace(root, include_agents=args.include_agents)
        output = generate_codebase_map(root, analyses, token_budget=args.budget)

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"[OK] Saved AST Context output to: {out_path} (~{estimate_tokens(output)} tokens)")
    else:
        print(output)


if __name__ == "__main__":
    main()
