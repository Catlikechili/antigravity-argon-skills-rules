---
name: verification-before-completion
description: Quy tắc kiểm chứng thực tế trước khi báo cáo (Exit Code = 0) — đã tích hợp trong GEMINI.md, không cần đọc lại file này.
---

# Tự Kiểm chứng Trước khi Hoàn tất (Verification Before Completion)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

- **Evidence Before Claims:** Chạy kiểm tra cú pháp/thực thi thực tế (`Exit Code = 0`), kiểm tra file đầu ra tồn tại (`> 0 bytes`), đúng encoding `UTF-8` và không đứt gãy tham chiếu trước khi báo cáo hoàn tất.
