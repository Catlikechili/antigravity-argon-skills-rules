---
name: self-supervisor-meta-audit
description: Kiểm toán đối kháng (Assumption Inversion, Edge-case test) — đã tích hợp trong GEMINI.md, không cần đọc lại file này.
---

# Tự Giám sát & Kiểm toán Đối kháng (Self-Supervisor Meta-Audit)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

- **Assumption Inversion:** Tự hỏi *"Điều kiện biên nào (offline, cp1252/utf-8, đường dẫn có khoảng trắng, input rỗng) sẽ làm code này sập?"*
- **Zero-Trust Proof:** Kiểm chứng thực tế (`Exit Code = 0`) trước khi kết luận hoàn thành.
