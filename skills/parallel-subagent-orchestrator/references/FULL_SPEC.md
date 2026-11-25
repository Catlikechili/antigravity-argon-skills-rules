---
name: parallel-subagent-orchestrator
description: >-
  Điều phối Worker/Subagent chạy song song theo ngân sách Token dưới quyền Lãnh đạo
  chính Argon, kết hợp tự động chuyển tiếp mô hình khi hết tài nguyên.
---

# Điều phối Worker / Subagent & Quản lý Ngân Sách Token Dưới Quyền `Argon`

## 1. Quy tắc Cổng Ngân Sách Token (Token Budget Gate)
- Trước khi phân bổ đội hình thực thi, Lãnh đạo chính **Argon** phải chốt với người dùng định mức Token mong muốn:
  - **Mức 1 (`< 15k` tokens):** Xử lý bằng `Batch Tool Calls` + script 0-token (`ctx_optimizer.py`, Python, `Ollama`) và tối đa 1 luồng `flash_lite` / `gemini-3.8-flash-low`.
  - **Mức 2 (`15k – 80k` tokens):** Giao việc qua `swarm` cho các mô hình tầm trung (`gemini-3.8-flash-medium/high`, `gpt-oss-120b-medium`, `gemini-4-neon-medium`).
  - **Mức 3 (`80k – 250k` tokens):** Chạy `swarm` song song đa module với `gemini-4-carbon-medium/high`, `claude-sonnet-5-5-medium/high`, `gemini-4-hydrogen-medium` + `verifier`.
  - **Mức 4 (`Max Quota`):** Huy động các mô hình đỉnh cao còn quota miễn phí (`claude-opus-5-5-high`, `gemini-4-hydrogen-xhigh`, `gemini-4-neon-xhigh`).

## 2. Giao thức Giao việc & Chuyển tiếp Hết Tài Nguyên (Compact Handshake & Failover)
- Gộp các lệnh `swarm{action:"add"}` hoặc `invoke_subagent` độc lập vào **cùng 1 lượt**.
- Luôn khóa đầu ra trong `brief` / `Prompt` giao việc:
  > *"Chỉ trả về kết quả cuối cùng kèm tọa độ `file:line` và trạng thái kiểm thử `Exit Code = 0` trong tối đa 10–15 dòng, tuyệt đối không chép lại nội dung file thô hay log trung gian."*
- Khi Worker hết quota, chuyển nóng bằng `swarm{action:"model", name:"<worker>", model:"<next_model>"}` theo thang leo thang tại `GEMINI.md` Mục 2.4 (tuyệt đối không `kill` rồi tạo mới).
