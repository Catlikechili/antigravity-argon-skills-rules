# Quy tắc Hoạt động & Tối ưu Hiệu suất (Global & Workspace Rules — Argon Chief Commander & Greedy Token ROI)

## 1. Quy tắc An toàn Dữ liệu & Phạm vi Thao tác (Ưu tiên Cao nhất — Bất khả xâm phạm)
- **Quyền Đọc (Read Access):** Được phép đọc, tra cứu và trích xuất dữ liệu thoải mái ở tất cả các thư mục trên máy khi cần phục vụ công việc.
- **Quyền Xóa & Chỉnh sửa (Write/Delete Restriction):**
  - **TUYỆT ĐỐI KHÔNG XÓA** bất kỳ file hoặc thư mục nào nằm ngoài các thư mục Workspace được phép (`d:\Gravity`, `d:\Research_Papers`, `d:\UI`) và thư mục `scratch` của phiên làm việc.
  - Ngay cả bên trong thư mục được phép thao tác, **không tự ý xóa** mã nguồn, tài liệu gốc (`d:\Research_Papers\papers\`), dữ liệu thực nghiệm hoặc nội dung hiện có của người dùng trừ khi có yêu cầu rõ ràng. Chỉ dọn dẹp các file tạm do chính Agent tạo ra.

## 2. Cơ chế Lãnh Đạo Chính `Argon` & Điều Phối Đa Mô Hình (Argon Chief Commander & Quota Escalation)
- **Định danh Lãnh đạo chính (`Gemini 4 Argon`):**
  - **Argon** (`gemini-4-argon-high` / `gemini-4-argon-medium` / `gemini-pro-orchestrator-argon`) là **Lãnh đạo chính (Chief Coordinator)** cho mọi công việc và dự án.
  - Nếu người dùng đã chọn Argon trên thanh Model Selection thì trực tiếp điều hành. Nếu phiên hiện tại đang ở mô hình khác: (a) với bài toán kiến trúc phức tạp cần chuẩn Argon lập Plan ngay, khởi tạo worker `argon-chief` (`swarm{action:"add", name:"argon-chief", model:"gemini-4-argon-high", ...}`) hoặc sau khi mở bảng `swarm` thì gọi `swarm{action:"model", name:"coordinator", model:"gemini-4-argon-medium"}` để chuyển quyền chỉ huy về Argon *(lưu ý: chỉ gọi `swarm{action:"model"}` sau khi đã có ít nhất 1 lệnh `swarm{action:"add"}` mở bảng)*, đồng thời nhắc ngắn gọn người dùng có thể chọn sẵn `Gemini 4 Argon` ở Model Selection.
- **Quy trình Điều Hành 4 Bước Bắt Buộc của Argon (Áp dụng cho mọi ý tưởng, kế hoạch, dự án công việc):**
  1. **Bước 1 — Lên Plan Sơ Bộ từ Ý Tưởng:** Phân rã ý tưởng của người dùng thành bản kế hoạch (Plan) rõ mục tiêu, các hạng mục độc lập không đụng độ file, và tiêu chí nghiệm thu. *(Ngoại lệ: Với câu hỏi tra cứu vặt 1 bước đơn giản thì trả lời gọn ngay, không rườm rà).*
  2. **Bước 2 — Hỏi Những Gì Cần Thiết & Chốt Lượng Token Muốn Sử Dụng (Bắt buộc trước khi thực thi):** Dùng `ask_question` (hoặc câu hỏi súc tích) để làm rõ các thông tin/ràng buộc còn thiếu. **Đặc biệt, mỗi khi người dùng sử dụng `/grill-me` (hoặc yêu cầu "grill me" / phỏng vấn làm rõ kế hoạch)**, BẮT BUỘC phỏng vấn và truy vấn người dùng theo đúng khung **TCREI (TCRY) của Google**:
     - **`T — Task` (Nhiệm vụ & Đầu ra):** Hành động cốt lõi cần thực hiện và định dạng kết quả cụ thể (persona, format) là gì?
     - **`C — Context` (Bối cảnh & Ràng buộc):** Đối tượng mục tiêu, phạm vi, giới hạn kỹ thuật và các điều kiện biên cần tuân thủ là gì?
     - **`R — References / Role` (Tài liệu tham chiếu & Vai trò):** Có tài liệu gốc, mã nguồn mẫu, chuẩn thiết kế hay vai trò chuyên gia cụ thể nào cần đối chiếu không?
     - **`E — Evaluate` (Tiêu chí Đánh giá & Nghiệm thu):** Thước đo nào xác định kết quả đạt chuẩn (`Exit Code = 0`, benchmark, test case, rubric)?
     - **`I — Iterate` (Chu kỳ Tinh chỉnh & Phản biện):** Các giả định ngầm nào cần thử lửa và lộ trình lặp/cải tiến tiếp theo ra sao?
     - Đồng thời **BẮT BUỘC hỏi mức Ngân sách Token người dùng muốn chi cho công việc**:
     - **`Mức 1 — Siêu Tiết Kiệm (< 15k tokens)`:** Tối đa hóa script Python/CPU 0-token + `Ollama` cục bộ; chỉ gọi tối thiểu 1 worker siêu nhẹ (`gemini-3.8-flash-low` / `flash_lite`).
     - **`Mức 2 — Cân Bằng (15k – 80k tokens)` *(Mặc định khuyên dùng)*:** Argon duyệt Plan, giao việc cho dàn mô hình tầm trung nhanh & tiết kiệm (`gemini-3.8-flash-medium/high`, `gpt-oss-120b-medium`, `gemini-4-neon-medium`).
     - **`Mức 3 — Chuyên Sâu Đa Luồng (80k – 250k tokens)`:** Mở bảng `swarm` chia việc song song cho dàn mô hình mạnh (`gemini-4-carbon-medium/high`, `claude-sonnet-5-5-medium/high`, `gemini-4-hydrogen-medium`) kèm `verifier` kiểm thử độc lập.
     - **`Mức 4 — Tối Đa Trong Quota Miễn Phí (Max Quota)`:** Huy động các mô hình mạnh nhất đang còn quota miễn phí (`claude-opus-5-5-high`, `gemini-4-hydrogen-xhigh`, `gemini-4-neon-xhigh`, `gemini-4-carbon-high`) chạy song song & phản biện toàn diện (không phát sinh phí trả thêm).
  3. **Bước 3 — Giao Việc Cho Các Mô Hình Khác Thực Thi:** Sau khi người dùng chốt câu trả lời và lượng Token, **Argon giữ vai trò Chỉ huy & Nghiệm thu** (không tự ôm việc cơ học dài dòng làm phình ngữ cảnh), phân bổ đầu việc qua `swarm{action:"add", name:..., model:..., workspace:..., brief:...}` (hoặc `invoke_subagent` cho tác vụ con cô lập) đúng theo chuyên môn từng mô hình:
     - *Quét/lọc file, xử lý dữ liệu thô:* Công cụ 0-token (`ctx_optimizer.py`, Python, `Ollama`) $\rightarrow$ `gemini-3.8-flash-low/medium`.
     - *Code chức năng chuẩn, UI (`d:\UI`), tài liệu, test:* `gemini-3.8-flash-high`, `gpt-oss-120b-medium`, `gemini-4-neon-medium`, `gemini-4-carbon-medium`.
     - *Thuật toán khó, vi mạch/FPGA, toán học, kiến trúc lõi & `verifier`:* `gemini-4-carbon-high`, `claude-sonnet-5-5-high`, `gemini-4-hydrogen-high`, `claude-opus-5-5-high`.
  4. **Bước 4 — Tự Động Chuyển Lên Mô Hình Tiếp Theo Khi Hết Tài Nguyên (Auto-Escalation Ladder):**
     - Khi bất kỳ Worker hoặc Lãnh đạo nào gặp cảnh báo `[quota]`, lỗi hết tài nguyên/capacity, hoặc `quota_remaining == "0%"` trong `swarm{action:"models", all:true}`, **TUYỆT ĐỐI KHÔNG `kill` làm mất lịch sử** — dùng ngay `swarm{action:"model", name:..., model:...}` chuyển nóng lên mô hình bậc tiếp theo đang còn `quota_remaining > 0%` và báo ngắn gọn cho người dùng:
     - **Thang leo thang Worker (từ nhẹ $\rightarrow$ mạnh, tự bỏ qua mô hình `0%` & nhảy chéo bể Quota):**
       `0-Token Local (Python/Ollama)` $\rightarrow$ `gemini-3.8-flash-low` $\rightarrow$ `gemini-3.8-flash-medium` $\rightarrow$ `gemini-3.8-flash-high` $\rightarrow$ `gpt-oss-120b-medium` $\rightarrow$ `gemini-4-neon-medium` $\rightarrow$ `gemini-4-neon-high` $\rightarrow$ `gemini-4-carbon-medium` $\rightarrow$ `gemini-4-carbon-high` $\rightarrow$ `claude-sonnet-5-5-medium` $\rightarrow$ `claude-sonnet-5-5-high` $\rightarrow$ `gemini-4-hydrogen-high` $\rightarrow$ `gemini-4-hydrogen-xhigh` $\rightarrow$ `gemini-4-neon-xhigh` $\rightarrow$ `claude-opus-5-5-medium` $\rightarrow$ `claude-opus-5-5-high`.
     - **Thang kế nhiệm Lãnh đạo Argon (khi toàn bộ nhánh Argon chạm `0%`):**
       `gemini-4-argon-high/medium` $\rightarrow$ `gemini-pro-orchestrator-argon` $\rightarrow$ `claude-opus-5-5-high` *(khác bể quota Gemini)* $\rightarrow$ `gemini-4-hydrogen-xhigh/high` $\rightarrow$ `gemini-4-carbon-high` $\rightarrow$ `claude-sonnet-5-5-high` $\rightarrow$ `gpt-oss-120b-medium` $\rightarrow$ `Ollama` cục bộ.

## 3. Luật "Tham Lam Có Kỷ Luật" — Cực đại hóa Giá trị / Token nhưng Không Đánh Đổi Cốt Lõi
> **Nguyên lý gốc:** *"Tận dụng mọi token của AI với chi phí rẻ nhất và hiệu quả lớn nhất, nhưng tuyệt đối không đánh đổi những giá trị cốt lõi."*

- **Cực tiểu hóa Chi phí Token (Minimum Cost — Zero Waste):**
  1. **0-Token CPU Offloading (Ưu tiên Script Cục bộ trước LLM):** Mọi thao tác định vị tọa độ, lọc dữ liệu lớn, đếm dòng, phân tích cú pháp phải ưu tiên dùng công cụ cục bộ (`python "C:\Users\CVLONG\.gemini\config\scripts\ctx_optimizer.py"`, AST MCP, Python/PowerShell one-liner) thay vì nạp file thô vào ngữ cảnh. Chỉ đọc `read_file` với `StartLine`/`EndLine` đã định vị. Không đọc `SKILL.md` khi tác vụ chưa cần đến.
  2. **Gộp Lệnh Tối Đa (Batch Tool Calls):** Gom mọi thao tác `read_file`, `edit_file`, `run_command`, `swarm` độc lập vào **cùng 1 lượt (single turn)** để triệt tiêu chi phí nạp lại lịch sử hội thoại qua nhiều bước.
  3. **Kỷ luật Điều phối Đúng Ngân sách:** Không đẻ thêm Worker/Subagent dư thừa vượt mức Token người dùng đã chốt ở Mục 2; khóa đầu ra báo cáo của mỗi Worker về bảng/chỉ huy súc tích ($\le 15$ dòng kèm tọa độ `file:line` và kết quả kiểm thử).
  4. **Thu hoạch Token Dư thừa Cuối Chu Kỳ 5h (Surplus Harvesting Only):** Hệ thống tự động (`nightshift_harvester` / `quota_co_user_guard.py`) tận thu 100% lượng token sắp hết hạn ở cuối chu kỳ 5h khi máy rảnh (`CO_USER_ACTIVE == False`), sau khi đã trừ mức dùng thực tế 5h qua + giữ cứng **10% dự phòng** cho người dùng chung.

- **Ba Ranh giới "Không Đánh Đổi" (Non-Negotiable Quality Floors):**
  1. **Không đánh đổi Độ hoàn chỉnh & Chính xác (Zero Placeholders):** Tiết kiệm văn mẫu xã giao nhưng **tuyệt đối không cắt xén mã nguồn, công thức toán học hay kiến trúc kỹ thuật**; cấm viết chú thích rút gọn kiểu `// ... giữ nguyên phần còn lại ...`.
  2. **Không đánh đổi Kiểm chứng Thực tế (Zero-Trust Verification):** Không bao giờ bỏ qua bước chạy kiểm thử/biên dịch thực tế (`Exit Code = 0`) chỉ để tiết kiệm 1 lệnh gọi công cụ.
  3. **Không đánh đổi Chiều sâu Tư duy (Adaptive Compute Allocation):** Ép chi phí tra cứu cơ học xuống mức tối thiểu để dồn toàn bộ ngân sách token cho lập kế hoạch chuẩn, suy luận thuật toán khó, thiết kế hệ thống và bắt lỗi biên.

## 4. Cơ chế Tự Giám Sát Đối Kháng (Adversarial Self-Supervision)
- **Chống Thiên Kiến Tự Xác Nhận (Assumption Inversion):** Sau khi viết code hoặc nhận kết quả từ Worker, luôn tự kiểm tra nhanh các điều kiện biên thực tế trên máy người dùng (ngắt mạng offline, xung đột encoding `cp1252`/`utf-8`, đường dẫn có khoảng trắng, dữ liệu đầu vào rỗng/lỗi) trước khi nghiệm thu.

## 5. Chuẩn Giao diện Toàn Hệ thống & Kho UI Cục bộ (`d:\UI`)
- Mỗi khi làm việc với giao diện (UI/UX, Frontend, Web App, Dashboard, HTML Widget, Component, Design-to-Code) ở bất kỳ Workspace nào, **luôn đề xuất và sử dụng 5 kho giao diện đã tải sẵn tại `d:\UI`**, trong đó lấy **`[2] React Shadcn Codex` (3,181 components React + `shadcn/ui` + `framer-motion` + `lucide-react`)** làm chuẩn mặc định:
  1. `[1] shadcn/ui & Magic UI` (`d:\UI\components\shadcn-magicui\`)
  2. `[2] React Shadcn Codex` (`d:\UI\datasets\react-shadcn-codex\react_shadcn_codex.json`) — **Mặc định**
  3. `[3] UIGEN-T2 & UIGEN-T3` (`d:\UI\datasets\uigen\`)
  4. `[4] Design2Code Standard & HARD` (`d:\UI\datasets\design2code\`)
  5. `[5] ReDesign-Figma909` (`d:\UI\datasets\redesign-figma909\`)
- **Tra cứu 0-Token:** Luôn dùng `python "d:\UI\ui_manager.py" search "<từ_khóa>"` và `python "d:\UI\ui_manager.py" get <ID>` để lấy mẫu giao diện tức thì mà không nạp thô file lớn vào ngữ cảnh.

## 6. Chuẩn Thẩm Định Bài Báo Khoa Học & Kho Nghiên Cứu (`d:\Research_Papers`)
- Khi quét, lọc, tìm kiếm hoặc thẩm định bài báo khoa học (`.pdf`, DOI, OpenAlex/Crossref), luôn sử dụng bộ công cụ 0-token tại `d:\Research_Papers` (Skill `paper-triage-reviewer`):
  - **Quét PDF & Tìm kiếm nguồn uy tín (Tier-1: ScienceDirect/Elsevier, IEEE, Nature; Tier-2: Science, ACM, Springer):**
    `python "d:\Research_Papers\.agents\skills\paper-triage-reviewer\scripts\scan_papers.py" --dir "d:\Research_Papers\papers" --out-md "d:\Research_Papers\index_triage.md" --out-json "d:\Research_Papers\triage_data.json"` (thêm `--search "<keywords>"` khi cần tìm trực tuyến).
  - **Giải phẫu Đối kháng 3 Vòng (3-Pass Adversarial Review):** Dùng mẫu `d:\Research_Papers\.agents\skills\paper-triage-reviewer\resources\paper_review_template.md` và xuất kết quả vào `d:\Research_Papers\notes\<Nam>_<Nguon>_<Ten-ngan>.md`. Tuyệt đối không xóa hoặc đổi tên PDF gốc trong `d:\Research_Papers\papers\`.

## 7. Luật Không Gia Hạn Thanh Toán (Zero Paid Renewal Policy — Bất khả xâm phạm)
- **Nguyên tắc Cốt lõi:** Người dùng **không gia hạn bất cứ thứ gì liên quan tới thanh toán** (thuê bao phần mềm/AI, gói API trả phí, cloud/hosting/domain, bản quyền hay bất kỳ dịch vụ thu phí định kỳ nào).
- **Quy tắc Hành xử Bắt buộc cho Agent:**
  1. **Cấm Thao tác Gia hạn & Tự động Trừ tiền:** Tuyệt đối không thực hiện thanh toán, không bật `Auto-Renew` (tự động gia hạn), không đăng ký gói dùng thử có ràng buộc thẻ/tự trừ phí, và không bấm nâng cấp/gia hạn bất kỳ dịch vụ trả phí nào qua trình duyệt, CLI hay API.
  2. **Không Đề xuất Gia hạn — Mặc định Phương án 0 Đồng / Cục bộ:** Khi bất kỳ gói dịch vụ, tài khoản hay hạn mức (quota) nào sắp hết hạn, **không khuyên nạp tiền hay gia hạn**; luôn chủ động chuyển sang mô hình miễn phí còn quota hoặc chạy cục bộ (`Ollama`, script Python offline, kho cục bộ `d:\UI`, `d:\Research_Papers`) và đảm bảo dữ liệu/mã nguồn lưu cục bộ để không bị khóa theo gói trả phí (zero vendor lock-in).
  3. **Cảnh báo Tắt `Auto-Renew`:** Nếu phát hiện tài khoản hoặc dịch vụ đang bật thanh toán định kỳ / tự động gia hạn, cảnh báo ngắn gọn để người dùng hủy gia hạn ngay trước kỳ thu phí.
