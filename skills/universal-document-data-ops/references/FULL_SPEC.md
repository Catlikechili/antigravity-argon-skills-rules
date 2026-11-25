---
name: universal-document-data-ops
description: >-
  Quy trình xử lý, trích xuất, chuyển đổi và tạo mới đa định dạng tài liệu & dữ liệu
  (PDF, Word .docx, Excel .xlsx, PowerPoint .pptx, LaTeX .tex, CSV, JSON, TXT) bằng script
  tốc độ cao mà không làm tràn bộ nhớ ngữ cảnh.
---

# Xử lý Đa Tài liệu & Dữ liệu Tự động (Universal Document & Data Ops)

## 1. Nguyên tắc Xử lý File Nặng Không Tốn Token (Script-Driven Processing)
- Với các file dữ liệu lớn (`.csv`, `.json`, `.txt`, `.xlsx`, `.pdf`, `.docx`), **không nạp trực tiếp toàn bộ nội dung thô vào cửa sổ chat**.
- Hãy viết hoặc chạy lệnh/script ngắn (Python / PowerShell) để:
  1. Kiểm tra cấu trúc tổng quan (số trang, tên sheet, danh sách cột, số dòng, kích thước).
  2. Trích xuất hoặc biến đổi chính xác phần dữ liệu cần thiết.

## 2. Công cụ Chuẩn cho Từng Định dạng
- **PDF (`.pdf`):** Dùng `pypdf`/`pymupdf` (`fitz`) hoặc `pdfplumber` để trích xuất văn bản/bảng biểu theo đúng số trang cần lấy; dùng `pdflatex`/`xelatex` khi biên dịch từ nguồn `.tex`.
- **Excel / CSV / Bảng số liệu (`.xlsx`, `.csv`, `.tsv`, `.txt`):** Dùng `pandas` hoặc `openpyxl` để lọc, tính toán thống kê, gộp bảng và xuất báo cáo giữ nguyên định dạng.
- **Word & PowerPoint (`.docx`, `.pptx`):** Dùng `python-docx` / `python-pptx` hoặc `pandoc` để trích xuất nội dung. Khi cần **tạo mới báo cáo Word (`.docx` chuẩn Modern / Nghị định 30/2020) hoặc slide thuyết trình PowerPoint (`.pptx` 16:9 chống tràn lề)**, ưu tiên kích hoạt skill chuyên sâu `word-ppt-report-builder` (`scripts/report_engine.py`).
- **Đảm bảo Encoding:** Luôn đọc và ghi file văn bản tiếng Việt với chuẩn `UTF-8` để tránh lỗi font chữ.
