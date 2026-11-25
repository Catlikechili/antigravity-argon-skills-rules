---
name: idle-free-model-runner
description: >-
  Tối ưu hiệu suất Token bằng cách tự động điều phối các Model AI Miễn Phí / Siêu Nhẹ
  (Local Ollama Qwen 7B, Subagent flash_lite/flash, OpenRouter :free, Gemini/Groq Free Tier,
  và bộ nén AST 0-Token) để xử lý tức thì các tác vụ có PHẠM VI RỘNG nhưng MỨC ĐỘ DỄ
  (quét hàng loạt file, tóm tắt thư mục lớn, dịch thuật, viết docstring, trích xuất metadata,
  lọc thô Map-Reduce) giúp tiết kiệm 85–95% hạn mức Token của Model chính.
---

# Điều Phối Model Miễn Phí Cho Tác Vụ Phạm Vi Rộng & Mức Độ Dễ (Broad-Scope Free-Model Token Offloader)

Skill này thiết lập cơ chế **Phân tầng Độ khó – Phạm vi (Complexity-Scope Triage)** và **Thuật toán Map-Reduce Đa Mô Hình**, cho phép Agent chính **gọi ngay lập tức các Model Miễn Phí / Siêu Nhẹ** để gánh toàn bộ các tác vụ có **phạm vi rộng (nhiều file, dữ liệu lớn) nhưng độ phức tạp đơn lẻ thấp**, giữ cho ngữ cảnh của Model chính luôn siêu nhẹ và chỉ tập trung vào suy luận thuật toán khó.

---

## 1. Ma Trận Phân Loại Tác Vụ: Khi Nào Gọi Model Miễn Phí? (Scope vs. Complexity Matrix)

Không chờ máy rảnh — ngay trong phiên làm việc, mỗi khi gặp tác vụ mới, Agent đối chiếu ma trận sau để định tuyến tức thì:

| Phân Loại Tác Vụ | Đặc Điểm Nhận Diện (`Scope` & `Complexity`) | Bộ Thực Thi Chỉ Định | Tỷ Lệ Tiết Kiệm Token Chính |
| :--- | :--- | :--- | :-: |
| **1. Phạm Vi Rộng + Mức Độ Dễ**<br>*(Broad Scope, Low Complexity)* | • Quét/tóm tắt $\ge 3$ file hoặc cả thư mục lớn<br>• Dịch thuật tài liệu, biên tập `summary_vi` hàng loạt<br>• Viết/bổ sung docstring, comment, README, câu hỏi ôn tập<br>• Chuẩn hóa JSON/CSV/Markdown, kiểm tra quy ước đặt tên<br>• Tìm kiếm sơ bộ tọa độ hàm/biến trên nhiều module | **THEO THỨ TỰ ƯU TIÊN:**<br>1. CLI `idle_free_runner.py --batch-scan` (0-Quota)<br>2. MCP `ask_local_ollama_qwen` (0-Quota)<br>3. `invoke_subagent(Model="flash_lite")` *(Chỉ bật khi văn bản thô $>15.000$ token hoặc cần tự chủ nhiều bước)* | **Tiết kiệm 85% – 100%**<br>*(Model chính không cần đọc file thô)* |
| **2. Phạm Vi Rộng + Mức Độ Khó**<br>*(Broad Scope, High Complexity)* | • Tái cấu trúc kiến trúc liên thông nhiều module<br>• Tìm bug tiềm ẩn (race condition, memory leak) trên dự án lớn<br>• Đối chiếu hàng chục bài báo khoa học để thiết kế thuật toán | **PIPELINE LAI `MAP-REDUCE`:**<br>• **Bước Map (Model Miễn Phí):** Quét rộng toàn bộ file, nén AST và lọc ra đúng 3–5 tọa độ `[Lstart-Lend]` nghi vấn.<br>• **Bước Reduce (Model Chính):** Chỉ đọc đúng đoạn dòng đã lọc để giải thuật toán sâu. | **Tiết kiệm 75% – 90%** |
| **3. Phạm Vi Hẹp + Mức Độ Khó**<br>*(Narrow Scope, High Complexity)* | • Viết/sửa hàm toán học nặng (FOC, MPC, Kalman, CORDIC)<br>• Cấu hình thanh ghi DMA/MPU/Cache sát phần cứng (`1–2` file) | **MODEL CHÍNH TRỰC TIẾP XỬ LÝ**<br>*(Kết hợp `read_file` phẫu thuật đúng dòng)* | Giữ nguyên 100% chiều sâu tư duy |

---

## 2. Ba Kênh Gọi Model Miễn Phí Tức Thì (Instant Zero-Cost Execution Channels)

Khi xác định tác vụ thuộc nhóm **Phạm vi rộng – Mức độ dễ** (hoặc bước **Map** của bài toán lớn), ưu tiên sử dụng 3 kênh sau:

### Kênh 1: Quét Rộng & Xử Lý Hàng Loạt Bằng Script Đa Luồng (`--batch-scan` / `--run-now`)
Sử dụng công cụ [`scripts/idle_free_runner.py`](file:///d:/Gravity/.agents/skills/idle-free-model-runner/scripts/idle_free_runner.py) để tự động nén AST Skeleton hàng chục file và đẩy song song vào **Local Ollama (`qwen7b-antigravity` / `qwen2.5-coder:7b`)** hoặc **Cloud Free APIs (`OpenRouter :free`, `Gemini Free`, `Groq Free`)**:

```powershell
# 1. Phân loại nhanh (Triage) xem tác vụ nên giao cho Model Miễn Phí hay Model Chính:
python "d:\Gravity\.agents\skills\idle-free-model-runner\scripts\idle_free_runner.py" --triage --target "01_Hoc_Tap/Embedded_Offline_Academy/07_STM32_Mastery_Lab_Va_Mo_Phong/Bai_Tap_C_Thuc_Chien_Nang_Cao" --prompt "Tóm tắt mục tiêu và các hàm chính của toàn bộ các bài Lab C" --json

# 2. Quét rộng hàng loạt (Batch Map-Reduce) trên cả thư mục bằng Model Miễn Phí (chạy tức thì):
python "d:\Gravity\.agents\skills\idle-free-model-runner\scripts\idle_free_runner.py" --batch-scan --target "01_Hoc_Tap/Embedded_Offline_Academy/07_STM32_Mastery_Lab_Va_Mo_Phong/Bai_Tap_C_Thuc_Chien_Nang_Cao" --glob "Lab*.c" --max-files 10 --workers 4 --prompt "Liệt kê tên bài Lab, ngoại vi STM32 sử dụng và hàm kiểm thử chính trong 3 dòng"

# 3. Giao 1 tác vụ đơn lẻ mức độ dễ cho Model Miễn Phí xử lý ngay:
python "d:\Gravity\.agents\skills\idle-free-model-runner\scripts\idle_free_runner.py" --run-now --target "duong_dan_file_hoac_thu_muc" --prompt "Viết docstring chuẩn và tóm tắt luồng dữ liệu"
```

### Kênh 2: Gọi Trực Tiếp MCP Tool `ask_local_ollama_qwen` (Offline 0-Token)
Khi cần hỏi nhanh mô hình cục bộ `qwen7b-antigravity` về cấu trúc 1 file hoặc thư mục mà không muốn nạp nội dung thô vào luồng chính:
- Gọi `call_mcp_tool` với `ServerName="ast-context-optimizer"`, `ToolName="ask_local_ollama_qwen"`, truyền `root`, `target`, và `prompt`.

### Kênh 3: Điều Phối Subagent Hạng Nhẹ (`Model="flash_lite"` hoặc `Model="flash"`) — Có Điều Kiện Hòa Vốn
Tuân thủ nghiêm ngặt ngưỡng hòa vốn của `parallel-subagent-orchestrator` và `GEMINI.md`: **CHỈ gọi Kênh 3** khi tác vụ có khối lượng văn bản thô **$>15.000$ token** (mà Kênh 1 & Kênh 2 không xử lý thay được) và cần khả năng gọi công cụ đọc/ghi file tự chủ, hoặc khi người dùng yêu cầu rõ:
- Gọi `invoke_subagent(TypeName="self", Model="flash_lite", Role="Broad-Scope Easy Task Worker", Prompt="...")`.
- **Quy tắc khóa đầu ra (Compact Output Contract):** Luôn yêu cầu Subagent `flash_lite` ghi trực tiếp kết quả hoàn chỉnh ra file đích trên ổ cứng và **chỉ trả về cho Agent chính bảng tóm tắt $\le 15$ dòng kèm tọa độ `file:line`**.

---

## 3. Giao Thức `Map-Reduce` Tiết Kiệm Token Cực Đại (2-Stage Token Optimization Protocol)

Đối với mọi yêu cầu chạm tới **$\ge 4$ files** (dùng CLI Kênh 1/2) hoặc **$>15.000$ tokens** (dùng CLI Kênh 1 hoặc Subagent Kênh 3):
1. **Giai đoạn 1 — `FREE-MODEL MAP` (Quét Rộng Chi Phí 0):**
   - Chạy `idle_free_runner.py --batch-scan` (kết hợp nén AST `-90%` token) để các model miễn phí đọc lướt toàn bộ tập file, trích xuất danh sách hàm, cấu trúc dữ liệu, hoặc dịch/tóm tắt từng phần vào 1 file báo cáo tổng hợp (`batch_digest.md`).
2. **Giai đoạn 2 — `MAIN-MODEL REDUCE` (Suy Luận Tinh Hoa):**
   - Agent chính chỉ đọc bản tóm tắt siêu gọn từ Giai đoạn 1 (tốn `< 500` tokens thay vì `50.000` tokens) để đưa ra quyết định kiến trúc hoặc sửa đúng dòng code quan trọng.

---

## 4. Kỷ Luật Chất Lượng (Non-Negotiable Quality Floor)

- **Không dùng Model Miễn Phí cho tác vụ vượt quá năng lực:** Tuyệt đối không giao việc chứng minh toán học phức tạp, thiết kế bộ điều khiển thời gian thực hay sửa lỗi đồng bộ phần cứng cấp thấp cho model nhỏ mà không có bước kiểm tra (`Verification`) của Agent chính.
- **Tự động Fallback Mượt Mà (`Zero-Crash Routing`):** Thứ tự ưu tiên tự động trong `idle_free_runner.py` là: `Local Ollama (qwen7b-antigravity / qwen2.5-coder:7b)` $\rightarrow$ `Cloud Free APIs (OpenRouter :free / Gemini Free / Groq Free)` $\rightarrow$ `Local AST Deterministic Analyzer (ctx_optimizer.py 0-token engine)`. Đảm bảo lệnh luôn thành công (`Exit Code = 0`) trong `< 1–5s` ngay cả khi máy ngắt mạng hoặc chưa bật Ollama.
