---
name: context-engineering-search-first
description: >-
  Tối ưu hóa ngữ cảnh, nén AST Skeleton / RepoMap và tăng tốc suy luận theo nguyên tắc Search-First
  (Truy vấn tọa độ trước, đọc tối thiểu sau). Sử dụng khi làm việc với codebase lớn, file dài,
  thư mục nhiều tài liệu hoặc khi dùng các mô hình miễn phí / giới hạn ngữ cảnh nhỏ để giảm 80-95% token.
---

# Kỹ thuật Ngữ cảnh, Nén AST Skeleton & Truy xuất Chọn lọc (Search-First Protocol)

## 1. Công cụ Nén AST Codebase Map & Skeleton (0-Token LLM Parsing)
Khi khảo sát dự án mới hoặc file dài ($>200$ dòng), **CẤM đọc toàn bộ file thô**. Dùng ngay bộ công cụ AST cục bộ để lấy tọa độ chính xác với chi phí 0 token suy luận:

- **Cách 1 (MCP Tools):**
  - `ast_repo_map(root="d:/Gravity", budget=2000)`: Bản đồ dự án kèm thứ hạng file và dòng `[Lstart-Lend]`.
  - `ast_file_skeleton(root="d:/Gravity", target="path/to/file.py")`: Trích xuất khung class/hàm/tham số + tọa độ dòng (tiết kiệm 80–95% token).
  - `ast_symbol_search(root="d:/Gravity", query="ten_ham")`: Định vị nhanh `file:[Lstart-Lend]` của hàm/class.
- **Cách 2 (CLI Script tốc độ cao qua `run_command`):**
  ```powershell
  # Bản đồ dự án siêu nén / Bộ khung AST / Tìm kiếm ký hiệu:
  python "d:\Gravity\.agents\skills\context-engineering-search-first\scripts\ctx_optimizer.py" --root "d:\Gravity" --mode map --out "d:\Gravity\CODEBASE_MAP.md" --budget 2500
  python "d:\Gravity\.agents\skills\context-engineering-search-first\scripts\ctx_optimizer.py" --root "d:\Gravity" --mode skeleton --target "duong_dan_file_hoac_thu_muc"
  python "d:\Gravity\.agents\skills\context-engineering-search-first\scripts\ctx_optimizer.py" --root "d:\Gravity" --mode search --query "tu_khoa"
  ```
  *(Bản toàn cục luôn có sẵn tại `C:\Users\CVLONG\.gemini\config\scripts\ctx_optimizer.py` và `d:\Gravity\03_Tham_Khao\04_AI_Tools_Configs\tools\ctx_optimizer.py`).*

## 2. Quy trình 3 Bước "Định vị Trước – Đọc Tối thiểu Sau"
1. **Locate (0-Token CPU):** Đọc `CODEBASE_MAP.md` hoặc chạy `ctx_optimizer.py` / `Select-String` / `rg` để lấy đúng `Path` và `[Lstart-Lend]`.
2. **Targeted Read:** Gọi `read_file` với `StartLine` và `EndLine` khớp tọa độ vừa tìm ($\pm 30$ dòng).
3. **Batch Execution:** Gộp toàn bộ các lệnh đọc/sửa đã biết tọa độ vào **cùng 1 lượt gọi công cụ**.

## 3. Phân tầng Ngữ cảnh 3 Lớp (3-Tier Context Management)
- **Hot Context (Trong luồng chính):** Mục tiêu hiện tại, cửa sổ `file:StartLine-EndLine` đang sửa, và khối `⚡ COMPACT STATE`.
- **Warm Context (Lưu ra File / Scratch):** Bản đồ `CODEBASE_MAP.md`, kết quả lọc trung gian.
- **Cold Context (0-Token Script trước, Subagent có điều kiện):** Khi cần quét $\ge 3$ file hoặc tài liệu nặng, **ưu tiên số 1 là chạy script Python/PowerShell lọc lấy đúng đoạn cần tìm trong 1 lệnh** (tránh phí nhân bản System Prompt của Subagent). Chỉ đẩy sang Subagent `research` khi khối lượng văn bản trích xuất $>15.000$ token hoặc người dùng yêu cầu rõ.
