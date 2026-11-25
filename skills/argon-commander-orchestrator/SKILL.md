---
name: argon-commander-orchestrator
description: "Sổ tay vận hành chi tiết cho Lãnh đạo chính Argon (Gemini 4 Argon): lập Plan từ ý tưởng, hỏi thông tin cần thiết và định mức Token qua ask_question, phân bổ Swarm đa mô hình và tự động leo thang mô hình khi hết tài nguyên (Quota Failover)."
---

# Quy Trình Điều Phối Của Lãnh Đạo Chính `Argon` (Argon Chief Commander Runbook)

## 1. Tiếp quản Quyền Chỉ Huy về `Argon`
1. Kiểm tra danh sách mô hình & hạn mức thực tế:
   ```json
   swarm{"action": "models", "all": true}
   ```
2. **Quy tắc kỹ thuật quan trọng (`no swarm yet` guard):** Công cụ `swarm{"action": "model", ...}` chỉ hoạt động **sau khi bảng Swarm đã được khởi tạo** (tức đã gọi ít nhất 1 lần `swarm{"action": "add", ...}`).
   - Nếu người dùng đã chọn **Gemini 4 Argon** hoặc **Orchestrator (Argon)** ở thanh Model Selection: Coordinator đã là Argon ngay từ lượt đầu.
   - Nếu phiên chat đang chạy ở mô hình khác: ngay khi khởi tạo Worker đầu tiên bằng `swarm{"action": "add", ...}`, gọi tiếp `swarm{"action": "model", "name": "coordinator", "model": "gemini-4-argon-medium"}` (hoặc `"gemini-4-argon-high"`) trong lượt sau để chuyển Coordinator sang Argon mà không lỗi.

## 2. Mẫu Khai Vấn Ý Tưởng, Khung `/grill-me` TCREI (TCRY) & Ngân Sách Token (`ask_question`)
Khi người dùng đưa ra ý tưởng mới hoặc kích hoạt `/grill-me` ("grill me"), Argon trình bày **Khung Plan Sơ Bộ** ngắn gọn (3–6 gạch đầu dòng) rồi gọi `ask_question` phỏng vấn người dùng theo khung **TCREI (TCRY)** (*Task — Context — References/Role — Evaluate — Iterate*) để bóc tách triệt để các điểm mù thiết kế, trong đó **luôn có câu hỏi Ngân sách Token**:
- `(Recommended) Mức 2 - Cân Bằng (15k - 80k tokens): Argon lập plan, giao Flash/GPT-OSS/Neon thực thi`
- `Mức 1 - Siêu Tiết Kiệm (< 15k tokens): Ưu tiên tối đa Python/CPU 0-token + Ollama cục bộ + 1 luồng Flash-Low`
- `Mức 3 - Chuyên Sâu Đa Luồng (80k - 250k tokens): Chạy Swarm song song với Carbon/Sonnet/Hydrogen + Verifier độc lập`
- `Mức 4 - Tối Đa Trong Quota Miễn Phí (Max Quota): Huy động Opus 5.5 / Hydrogen XHigh / Neon XHigh chạy song song & kiểm chứng đối kháng`

## 3. Phân Bổ Đầu Việc Cho Các Mô Hình Khác (`swarm add`)
- Đặt tên bảng điều phối: `swarm{"action": "title", "title": "<Tên dự án ngắn gọn>"}`
- Tạo các Worker độc lập không trùng file sửa đổi (dùng `workspace: "share"` khi nhiều tác giả cùng sửa repo, `inherit` cho reader/verifier):
  - **Worker cơ học / dữ liệu / boilerplate:** `model: "gemini-3.8-flash-medium"` hoặc `"gemini-3.8-flash-high"`
  - **Worker code tính năng / fullstack / tài liệu:** `model: "gpt-oss-120b-medium"` hoặc `"gemini-4-neon-medium"` hoặc `"gemini-4-carbon-medium"`
  - **Worker lõi thuật toán / RTL / tối ưu hóa sâu:** `model: "gemini-4-carbon-high"` hoặc `"claude-sonnet-5-5-high"` hoặc `"gemini-4-hydrogen-high"`
  - **Verifier kiểm chứng độc lập (`Exit Code = 0`):** `model: "claude-sonnet-5-5-medium"` hoặc `"gemini-4-neon-high"` (chỉ kiểm tra diff + chạy test + báo lỗi theo `@tên_worker`, không tự sửa chồng chéo).
- Trong mỗi `brief`, khóa chặt 4 mục: (1) File sở hữu độc quyền, (2) Không được chạm vào đâu, (3) Tiêu chí `Exit Code = 0`, (4) Báo cáo lên bảng $\le 15$ dòng và `@coordinator` khi hoàn tất.
- Luôn hiển thị link mở bảng Swarm cho người dùng ở cuối lượt khởi tạo theo hướng dẫn của công cụ `swarm`.

## 4. Ma Trận Chuyển Tiếp Khi Hết Tài Nguyên (Quota Failover Escalation)
Khi gặp lỗi hết quota, cảnh báo `[quota]`, hoặc `quota_remaining == "0%"`:
1. Gọi `swarm{"action": "models", "all": true}` để lọc chính xác danh sách các mô hình đang có `quota_remaining != "0%"`.
2. Lưu ý **3 Bể Quota Độc Lập** trên hệ thống:
   - **Bể 1 (Họ Gemini):** `gemini-3.8-flash-*`, `gemini-4-neon-*`, `gemini-4-carbon-*`, `gemini-4-hydrogen-*`, `gemini-4-argon-*`, `gemini-pro-orchestrator-*`.
   - **Bể 2 (Họ Claude & GPT-OSS):** `gpt-oss-120b-medium`, `claude-sonnet-5-5-low/medium/high`, `claude-opus-5-5-low/medium/high`.
   - **Bể 3 (Cục bộ 0-Quota vĩnh viễn):** Script Python offline + `Ollama Qwen` (`ask_local_ollama_qwen`).
3. Chuyển nóng mô hình cho Worker đang `waiting` bằng `swarm{"action": "model", "name": "<worker>", "model": "<next_available_model>"}` (giữ nguyên toàn bộ lịch sử hội thoại, **tuyệt đối không `kill`**):
   - Nhánh thực thi: `gemini-3.8-flash-low` $\rightarrow$ `flash-medium` $\rightarrow$ `flash-high` $\rightarrow$ `gpt-oss-120b-medium` $\rightarrow$ `gemini-4-neon-medium/high` $\rightarrow$ `gemini-4-carbon-medium/high` $\rightarrow$ `claude-sonnet-5-5-medium/high` $\rightarrow$ `gemini-4-hydrogen-high/xhigh` $\rightarrow$ `gemini-4-neon-xhigh` $\rightarrow$ `claude-opus-5-5-medium/high`.
   - Nhánh Lãnh đạo chính: `gemini-4-argon-high` $\rightarrow$ `gemini-4-argon-medium` $\rightarrow$ `gemini-pro-orchestrator-argon` $\rightarrow$ `claude-opus-5-5-high` $\rightarrow$ `gemini-4-hydrogen-xhigh/high` $\rightarrow$ `gemini-4-carbon-high` $\rightarrow$ `claude-sonnet-5-5-high` $\rightarrow$ `gpt-oss-120b-medium`.
4. Thông báo minh bạch 1 dòng cho người dùng: *"Mô hình `<A>` đã hết hạn mức khả dụng; đã chuyển tiếp `<tên worker/chỉ huy>` lên `<B>` (còn `<X>%` quota) để tiếp tục không gián đoạn."*
