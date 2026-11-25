---
name: verification-before-completion
description: >-
  Quy trình tự kiểm thử và xác thực kết quả đầu ra trước khi báo cáo hoàn thành
  (Verification Before Completion). Luôn áp dụng ở bước cuối của mọi tác vụ viết code,
  chỉnh sửa tài liệu hoặc xử lý dữ liệu.
---

# Tự Kiểm chứng Trước khi Hoàn tất (Verification Before Completion)

## 1. Nguyên tắc "Bằng chứng Thực tế Trước khi Báo cáo" (Evidence Before Claims)
- Không bao giờ tuyên bố *"Đã sửa xong"* hoặc *"Hoạt động hoàn hảo"* nếu chưa kiểm tra kết quả đầu ra thực tế sau lần chỉnh sửa cuối cùng.

## 2. Danh sách Kiểm tra Nhanh theo Loại Tác vụ (Fast Verification Checklist)
- **Với Mã nguồn / Script:**
  - Chạy kiểm tra cú pháp (syntax check / linter / build) hoặc chạy thử với dữ liệu mẫu để đảm bảo Exit Code = 0.
- **Với Tài liệu / Báo cáo (LaTeX, Markdown, Word, PDF):**
  - Kiểm tra biên dịch thành công, file đầu ra tồn tại, dung lượng hợp lệ, không còn lỗi cú pháp hay tham chiếu đứt gãy (`??`, `Error`).
- **Với Dữ liệu (CSV, JSON, Excel, Database):**
  - Kiểm tra số dòng, tên cột, encoding (UTF-8) và in thử 3–5 bản ghi đầu/cuối để đảm bảo không bị mất mát hay lệch cột.
