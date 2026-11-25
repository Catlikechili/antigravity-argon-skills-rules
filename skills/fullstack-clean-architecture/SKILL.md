---
name: fullstack-clean-architecture
description: Chỉ đọc khi thiết kế kiến trúc phần mềm đa module mới hoặc kiểm toán bảo mật API/Database.
---

# Kiến trúc Mã nguồn Sạch, Hiệu năng & Bảo mật (Clean Architecture)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

- **Clean & Modular:** Single Responsibility, tên hàm/biến rõ nghĩa, dùng Guard Clauses (Early Return) chống lồng `if/else` sâu.
- **Resource & Performance:** Tránh $N+1$ queries, dùng streaming/chunking cho file lớn, luôn đóng tài nguyên (`with` / `using` / `try-finally`).
- **Security by Default:** Không hardcode API key/mật khẩu; làm sạch tham số chống Command/SQL Injection và Path Traversal.
