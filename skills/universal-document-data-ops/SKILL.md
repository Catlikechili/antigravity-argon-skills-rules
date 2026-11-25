---
name: universal-document-data-ops
description: Chỉ đọc khi cần quy trình xử lý/chuyển đổi file dữ liệu lớn (PDF, Excel, CSV, JSON, LaTeX) bằng script 0-token.
---

# Xử lý Đa Tài liệu & Dữ liệu bằng Script (Document & Data Ops)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

- **Cấm nạp thô file lớn vào chat:** Luôn chạy Python one-liner (`pypdf`/`fitz`, `pandas`/`openpyxl`, `python-docx`, `python-pptx`, `json`) với `sys.stdout.reconfigure(encoding='utf-8')` để kiểm tra cấu trúc (số trang, tên cột, số dòng) và trích xuất đúng phần cần lấy.
- Khi cần **tạo mới báo cáo `.docx` / `.pptx` chuyên nghiệp**, dùng `word-ppt-report-builder`.
