---
name: systematic-debugging
description: Quy trình gỡ lỗi Root-Cause 4 bước (Observe-Isolate-Fix-Verify) — chỉ đọc khi gặp lỗi phức tạp lặp lại >= 2 lần.
---

# Gỡ lỗi Hệ thống tại Gốc (Systematic Root-Cause Debugging)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

1. **No Shotgun Debugging:** Cấm sửa mò; nếu sai 2 lần liên tiếp phải dừng lại đo đạc trạng thái thực tế.
2. **Observe -> Isolate -> Root Fix -> Verify:** Đọc đúng dòng `Traceback/Error` $\rightarrow$ cô lập dữ liệu/môi trường tại điểm gãy $\rightarrow$ sửa tại gốc $\rightarrow$ chạy kiểm chứng `Exit Code = 0`.
