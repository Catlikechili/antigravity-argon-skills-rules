---
name: planning-and-task-breakdown
description: Chỉ đọc khi cần lập kế hoạch tái cấu trúc lớn liên quan >= 5 module phức tạp.
---

# Phân rã Bài toán & Lập Kế hoạch (Task Breakdown)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

1. **Impact Scope:** Liệt kê rõ các file cần đọc/sửa/tạo mới và vùng cấm chạm tới.
2. **Atomic Batch Steps:** Chia thành các bước kiểm chứng được ngay; gộp các thao tác độc lập vào cùng 1 lượt (Batch).
3. **Edge Cases:** Kiểm tra trước đường dẫn có dấu cách, encoding `utf-8`/`cp1252`, dữ liệu rỗng và chế độ offline.
