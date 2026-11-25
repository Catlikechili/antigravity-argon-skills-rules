# 🚀 Antigravity Argon Chief Commander — Rules & 21 Specialized Skills

Kho lưu trữ tổng hợp toàn bộ **Hệ thống Quy tắc Điều hành Toàn cục (`GEMINI.md` & Workspace Rules)** và **21 Kỹ năng Chuyên biệt (`Skills`)** dành cho **Google Antigravity IDE**, được thiết kế theo triết lý **Argon Chief Commander**, **Khung phỏng vấn `/grill-me` TCREI (TCRY)** và **Greedy Token ROI (Cực đại hóa Giá trị / Token với 0-Token CPU Offloading)**.

---

## 📌 1. Kiến trúc Cốt lõi & Triết lý Vận hành

- **Lãnh đạo chính `Argon` (`Gemini 4 Argon`):** Điều phối viên trung tâm thực hiện quy trình 4 bước: **(1) Lên Plan sơ bộ** $\rightarrow$ **(2) Phỏng vấn làm rõ theo khung TCREI (TCRY) khi dùng `/grill-me` & Chốt 4 mức Ngân sách Token** $\rightarrow$ **(3) Phân bổ Swarm đa mô hình** $\rightarrow$ **(4) Tự động chuyển tiếp mô hình khi hết tài nguyên (Auto-Escalation Quota Failover)**.
- **Khung câu hỏi `/grill-me` theo chuẩn TCREI (TCRY) của Google:**
  - **`T — Task`**: Nhiệm vụ cốt lõi & định dạng đầu ra.
  - **`C — Context`**: Bối cảnh, đối tượng mục tiêu, giới hạn kỹ thuật & điều kiện biên.
  - **`R — References / Role`**: Tài liệu tham chiếu, mã nguồn mẫu & vai trò chuyên gia.
  - **`E — Evaluate`**: Tiêu chí nghiệm thu thực tế (`Exit Code = 0`, test case, benchmark).
  - **`I — Iterate`**: Giả định ngầm cần thử lửa & chu kỳ tinh chỉnh tiếp theo.
- **Greedy Token ROI (Tham lam có kỷ luật):** Ưu tiên công cụ 0-token cục bộ (Python AST, `ctx_optimizer.py`, `Ollama` local) trước khi gọi LLM, gộp lệnh tối đa trong 1 lượt (Batch Tool Calls), và giữ cứng 3 ranh giới chất lượng (*Zero Placeholders*, *Zero-Trust Verification*, *Adaptive Compute Allocation*).

---

## 📜 2. Danh mục Rules (`rules/`)

| Tên Rule | Phạm vi áp dụng | Đường dẫn | Mô tả chức năng |
| :--- | :--- | :--- | :--- |
| **GEMINI.md (Global Rules)** | Global (`~/.gemini/config/GEMINI.md`) | [`rules/global/GEMINI.md`](rules/global/GEMINI.md) | Quy tắc điều hành tối cao của Lãnh đạo chính Argon (Gemini 4 Argon), khung hỏi xoáy `/grill-me` theo chuẩn TCREI (TCRY) của Google, kỷ luật Greedy Token ROI, 4 mức ngân sách Token, thang leo thang Quota Failover và Luật Không Gia Hạn Thanh Toán. |
| **paper-triage-workspace.md** | Workspace `d:\Research_Papers` | [`rules/workspaces/paper-triage-workspace.md`](rules/workspaces/paper-triage-workspace.md) | Quy chuẩn quét, phân loại bài báo khoa học Tier-1/Tier-2 và giải phẫu đối kháng 3 vòng (3-Pass Adversarial Review). |
| **ui-dataset-selector.md** | Workspace `d:\UI` | [`rules/workspaces/ui-dataset-selector.md`](rules/workspaces/ui-dataset-selector.md) | Quy tắc chọn mẫu giao diện chuẩn từ 5 bộ dữ liệu UI cục bộ (mặc định React Shadcn Codex 3,181 components). |

---

## 🧠 3. Danh mục 20 Skills Chuyên Biệt (`skills/`)

| # | Tên Skill | Thành phần đi kèm | Mô tả & Khi nào kích hoạt |
| :---: | :--- | :--- | :--- |
| 1 | **[`antigravity-custom-theme`](skills/antigravity-custom-theme/SKILL.md)** | `scripts/`, `references/resources` (115 files) | Use when the user wants to design, customize, install, update, or troubleshoot an Antigravity IDE or Manager visual theme from a wallpaper image, color palette, aesthetic mood, or preset. |
| 2 | **[`argon-commander-orchestrator`](skills/argon-commander-orchestrator/SKILL.md)** | `SKILL.md` (1 files) | Sổ tay vận hành chi tiết cho Lãnh đạo chính Argon (Gemini 4 Argon): lập Plan từ ý tưởng, hỏi thông tin cần thiết và định mức Token qua ask_question, phân bổ Swarm đa mô hình và tự động leo thang mô hình khi hết tài nguyên (Quota Failover). |
| 3 | **[`commander-4-subagents-squad`](skills/commander-4-subagents-squad/SKILL.md)** | `references/resources` (2 files) | Chỉ kích hoạt khi người dùng yêu cầu rõ Đội hình 4 Subagents (req-analyst, trusted-scout, wh5-challenger, master-synthesizer). |
| 4 | **[`context-engineering-search-first`](skills/context-engineering-search-first/SKILL.md)** | `scripts/`, `references/resources` (3 files) | Chỉ đọc khi cần tra cứu cú pháp CLI ctx_optimizer.py hoặc MCP nén AST cho codebase lớn. |
| 5 | **[`deep-research-and-synthesis`](skills/deep-research-and-synthesis/SKILL.md)** | `references/resources` (2 files) | Chỉ kích hoạt khi người dùng yêu cầu nghiên cứu chuyên sâu, tổng hợp tài liệu khoa học hoặc đối chiếu đa nguồn phức tạp. |
| 6 | **[`fullstack-clean-architecture`](skills/fullstack-clean-architecture/SKILL.md)** | `references/resources` (2 files) | Chỉ đọc khi thiết kế kiến trúc phần mềm đa module mới hoặc kiểm toán bảo mật API/Database. |
| 7 | **[`idle-free-model-runner`](skills/idle-free-model-runner/SKILL.md)** | `scripts/`, `references/resources` (4 files) | Chỉ kích hoạt khi cần chạy CLI idle_free_runner.py hoặc Ollama Qwen cục bộ để quét/tóm tắt hàng loạt file (Map-Reduce 0-Quota). |
| 8 | **[`karpathy-guidelines`](skills/karpathy-guidelines/SKILL.md)** | `references/resources` (2 files) | Nguyên tắc Karpathy (No Over-engineering, Surgical Edits) — đã tích hợp trong GEMINI.md, không cần đọc lại file này. |
| 9 | **[`paper-triage-reviewer`](skills/paper-triage-reviewer/SKILL.md)** | `scripts/`, `references/resources` (3 files) | Scans local PDF folders (default d:\Research_Papers\papers) or queries OpenAlex/Crossref to filter reputable academic venues (ScienceDirect/Elsevier, IEEE, Nature, Science, ACM, Springer), ranks papers by academic recency (Newest First) alongside high-citation seminal foundations, and writes 3-pass adversarial reviews into d:\Research_Papers\notes. Trigger whenever the user asks to scan papers, filter recent/novel or highly-cited foundational papers, rank literature, or review/dissect scientific PDFs. |
| 10 | **[`parallel-subagent-orchestrator`](skills/parallel-subagent-orchestrator/SKILL.md)** | `references/resources` (2 files) | Kỷ luật phân bổ Worker/Subagent theo ngân sách Token của Lãnh đạo chính Argon — đã tích hợp trong GEMINI.md, không cần đọc lại file này. |
| 11 | **[`planning-and-task-breakdown`](skills/planning-and-task-breakdown/SKILL.md)** | `references/resources` (2 files) | Chỉ đọc khi cần lập kế hoạch tái cấu trúc lớn liên quan >= 5 module phức tạp. |
| 12 | **[`rolling-summary-compactor`](skills/rolling-summary-compactor/SKILL.md)** | `references/resources` (2 files) | Chỉ kích hoạt khi người dùng yêu cầu nén ngữ cảnh cuốn chiếu hoặc xuất khối COMPACT STATE. |
| 13 | **[`self-improving-harness`](skills/self-improving-harness/SKILL.md)** | `SKILL.md` (1 files) | Hệ thống Tự Tiến Hóa Kỹ Năng & Bộ Nhớ Kinh Nghiệm 0-Token (ACE + Agentic Harness Engineering). Kích hoạt ở đầu phiên để nạp ngữ cảnh nhẹ, khi gặp lỗi lặp lại để tra cứu 0-token, hoặc cuối phiên để đúc kết bài học và đề xuất nâng cấp Skill (Shadow Proposals) có kiểm toán bảo mật. |
| 14 | **[`self-supervisor-meta-audit`](skills/self-supervisor-meta-audit/SKILL.md)** | `references/resources` (2 files) | Kiểm toán đối kháng (Assumption Inversion, Edge-case test) — đã tích hợp trong GEMINI.md, không cần đọc lại file này. |
| 15 | **[`socratic-thinking-mentor`](skills/socratic-thinking-mentor/SKILL.md)** | `references/resources` (2 files) | Chỉ kích hoạt khi người dùng yêu cầu khảo bài, hỏi xoáy Socratic, quiz kiểm tra kiến thức hoặc đóng vai giám khảo phản biện. |
| 16 | **[`systematic-debugging`](skills/systematic-debugging/SKILL.md)** | `references/resources` (2 files) | Quy trình gỡ lỗi Root-Cause 4 bước (Observe-Isolate-Fix-Verify) — chỉ đọc khi gặp lỗi phức tạp lặp lại >= 2 lần. |
| 17 | **[`ui-ux-pro-max`](skills/ui-ux-pro-max/SKILL.md)** | `references/resources` (2 files) | Chỉ đọc khi thiết kế Web App, Dashboard, HTML Widget hoặc tra cứu CLI kho giao diện d:\UI (React Shadcn Codex). |
| 18 | **[`universal-document-data-ops`](skills/universal-document-data-ops/SKILL.md)** | `references/resources` (2 files) | Chỉ đọc khi cần quy trình xử lý/chuyển đổi file dữ liệu lớn (PDF, Excel, CSV, JSON, LaTeX) bằng script 0-token. |
| 19 | **[`verification-before-completion`](skills/verification-before-completion/SKILL.md)** | `references/resources` (2 files) | Quy tắc kiểm chứng thực tế trước khi báo cáo (Exit Code = 0) — đã tích hợp trong GEMINI.md, không cần đọc lại file này. |
| 20 | **[`word-ppt-report-builder`](skills/word-ppt-report-builder/SKILL.md)** | `scripts/`, `references/resources` (3 files) | Chỉ kích hoạt khi người dùng yêu cầu tạo/xuất báo cáo Word (.docx) hoặc slide PowerPoint (.pptx). |

---

## 📂 4. Cấu trúc Thư mục

```text
antigravity-argon-skills-rules/
├── GEMINI.md                     # Bản sao nhanh Global Rules ở thư mục gốc
├── install.ps1                   # Script cài đặt 1-click vào ~/.gemini/config
├── rules/
│   ├── global/
│   │   └── GEMINI.md             # Quy tắc Toàn cục Argon Chief Commander & TCREI (/grill-me)
│   └── workspaces/
│       ├── paper-triage-workspace.md
│       └── ui-dataset-selector.md
└── skills/                       # 21 Skills chuyên biệt (kèm scripts 0-token & FULL_SPEC)
    ├── antigravity-custom-theme/
    ├── argon-commander-orchestrator/
    ├── commander-4-subagents-squad/
    ├── context-engineering-search-first/
    ├── deep-research-and-synthesis/
    ├── fullstack-clean-architecture/
    ├── idle-free-model-runner/
    ├── karpathy-guidelines/
    ├── paper-triage-reviewer/
    ├── parallel-subagent-orchestrator/
    ├── planning-and-task-breakdown/
    ├── rolling-summary-compactor/
    ├── self-improving-harness/
    ├── self-supervisor-meta-audit/
    ├── socratic-thinking-mentor/
    ├── systematic-debugging/
    ├── ui-ux-pro-max/
    ├── universal-document-data-ops/
    ├── verification-before-completion/
    └── word-ppt-report-builder/
```

---

## ⚡ 5. Hướng dẫn Cài đặt Nhanh (1-Click Install)

Mở **PowerShell** và chạy lệnh sau để tải về và tự động đồng bộ toàn bộ Rules & Skills vào `~/.gemini/config`:

```powershell
git clone https://github.com/Catlikechili/antigravity-argon-skills-rules.git
cd antigravity-argon-skills-rules
.\install.ps1
```
