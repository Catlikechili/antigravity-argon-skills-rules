---
name: parallel-subagent-orchestrator
description: Kỷ luật phân bổ Worker/Subagent theo ngân sách Token của Lãnh đạo chính Argon — đã tích hợp trong GEMINI.md, không cần đọc lại file này.
---

# Điều phối Worker / Subagent Theo Ngân Sách Token Của Lãnh Đạo `Argon`

> Chi tiết đầy đủ: `references/FULL_SPEC.md` và skill `argon-commander-orchestrator`.

- **Lãnh đạo chính `Argon` lập Plan & hỏi ngân sách Token trước** khi khởi chạy đội hình Worker/Subagent.
- **Đúng mức Token đã chốt:**
  - *Mức 1 (`< 15k` tokens):* Ưu tiên script cục bộ 0-token + tối đa 1 luồng `flash_lite` / `gemini-3.8-flash-low`.
  - *Mức 2–4 (`>= 15k` tokens):* Phân bổ `swarm` đa mô hình theo đúng bậc chuyên môn; khi hết tài nguyên dùng `swarm{action:"model"}` leo thang lên mô hình tiếp theo.
- **Giao thức:** Gộp lệnh khởi tạo vào 1 lượt, ép khóa đầu ra trả về $\le 15$ dòng kèm `file:line` và kết quả kiểm thử `Exit Code = 0`.
