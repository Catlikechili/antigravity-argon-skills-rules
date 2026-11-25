---
name: context-engineering-search-first
description: Chỉ đọc khi cần tra cứu cú pháp CLI ctx_optimizer.py hoặc MCP nén AST cho codebase lớn.
---

# Nén AST Skeleton & Truy xuất Chọn lọc (Search-First Protocol)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

## 1. Công cụ Nén AST 0-Token (Định vị trước, `read_file` theo dòng sau)
- **MCP (`ast-context-optimizer`):**
  - `ast_repo_map(root="d:/Gravity", budget=2000)`
  - `ast_file_skeleton(root="d:/Gravity", target="path/to/file.py")`
  - `ast_symbol_search(root="d:/Gravity", query="symbol_name")`
- **CLI (`scripts/ctx_optimizer.py`):**
  ```powershell
  python "C:\Users\CVLONG\.gemini\config\scripts\ctx_optimizer.py" --root "d:\Gravity" --mode map --budget 2500
  python "C:\Users\CVLONG\.gemini\config\scripts\ctx_optimizer.py" --root "d:\Gravity" --mode skeleton --target "path/to/file.py"
  python "C:\Users\CVLONG\.gemini\config\scripts\ctx_optimizer.py" --root "d:\Gravity" --mode search --query "ten_ham"
  ```

## 2. Quy tắc Đọc Tối thiểu
- Luôn truyền `StartLine` và `EndLine` khi gọi `read_file` cho file $>200$ dòng; gộp các lệnh độc lập vào cùng 1 lượt.
