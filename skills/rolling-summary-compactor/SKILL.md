---
name: rolling-summary-compactor
description: Chỉ kích hoạt khi người dùng yêu cầu nén ngữ cảnh cuốn chiếu hoặc xuất khối COMPACT STATE.
---

# Nén Tóm tắt Cuốn chiếu (Rolling Summary Compactor)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

## Quy tắc 4 Bước (Prune – Freeze – Overwrite – Focus)
Không chép nối tiếp (append) lịch sử cũ; ghi đè vào 1 khối duy nhất ($\le 8$ dòng):
```markdown
### ⚡ COMPACT STATE
- **Done:** `[DONE] file:Lstart-Lend -> Kết quả + Exit Code = 0`
- **Decisions/Constraints:** Ràng buộc kỹ thuật đang giữ.
- **Next Pointer:** `file:StartLine-EndLine` cần xử lý tiếp theo.
```
