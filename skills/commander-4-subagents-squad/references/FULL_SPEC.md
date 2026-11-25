---
name: commander-4-subagents-squad
description: >-
  Hệ thống Chỉ huy Đội hình 4 Subagents Chuyên biệt (Commander & 4-Subagent Squad Workflow):
  (1) req-analyst (Phân tích yêu cầu), (2) trusted-scout (Tìm kiếm nguồn đề cử & uy tín cao nhất),
  (3) wh5-challenger (Phản bác sắc bén bằng 5 câu hỏi Wh), và (4) master-synthesizer (Tổng hợp Minto BLUF),
  sau đó Chỉ huy (Main Agent) tổng duyệt lần cuối rồi gửi người dùng.
---

# Quy trình Chỉ huy Đội hình 4 Subagents (Commander & 4-Subagent Squad)

Skill này tích hợp sức mạnh của 8 kỹ năng nền tảng trong hệ thống (`parallel-subagent-orchestrator`, `planning-and-task-breakdown`, `context-engineering-search-first`, `deep-research-and-synthesis`, `socratic-thinking-mentor`, `self-supervisor-meta-audit`, `rolling-summary-compactor`, `verification-before-completion`) thành một **Đội hình 4 Subagents hoạt động dưới quyền Chỉ huy của Main Agent**.

## 1. Kiến trúc Đội hình & Phân công Nhiệm vụ

```
                 [ NGƯỜI DÙNG (USER) ]
                          │
                          ▼
         ╔════════════════════════════════╗
         ║   CHỈ HUY (COMMANDER / MAIN)   ║
         ║  Điều phối & Tổng duyệt Cuối   ║
         ╚════════════════════════════════╝
            │             │             │
   ┌────────┴───┐     ┌───┴────────┐    └───► (Chạy song song hoặc nối tiếp)
   ▼            ▼     ▼            ▼
[Agent 1]    [Agent 2]          [Agent 3]
req-analyst  trusted-scout      wh5-challenger
(Phân tích   (Tìm nguồn đề cử   (Phản bác bằng
 yêu cầu)     & uy tín nhất)     5 câu hỏi Wh)
   │            │                  │
   └────────────┴─────────┬────────┘
                          ▼
                     [Agent 4]
                 master-synthesizer
             (Tổng hợp Minto BLUF sơ bộ)
                          │
                          ▼
         ╔════════════════════════════════╗
         ║   CHỈ HUY TỔNG HỢP LẦN CUỐI    ║
         ║   Kiểm chứng & Gửi Người Dùng  ║
         ╚════════════════════════════════╝
```

| Thứ tự | Tên định danh (`TypeName`) | Vai trò (`Role`) | Kỹ năng nền tảng kết hợp | Nhiệm vụ cốt lõi |
| :--- | :--- | :--- | :--- | :--- |
| **Chỉ huy** | **Main Agent** | **Commander-in-Chief** | `parallel-subagent-orchestrator` + `verification-before-completion` | Tiếp nhận yêu cầu, điều phối 4 Subagents, thẩm định chéo và **tổng hợp bản cuối cùng** gửi người dùng. |
| **Subagent 1** | `req-analyst` | **Requirement Analyst** | `planning-and-task-breakdown` + `context-engineering-search-first` | Bóc tách mục tiêu cốt lõi, phạm vi, ràng buộc, giả định ngầm và tiêu chí nghiệm thu của yêu cầu. |
| **Subagent 2** | `trusted-scout` | **Trusted Source Scout** | `deep-research-and-synthesis` | Tìm kiếm & lọc **các nguồn được đề cử nhiều nhất, có uy tín cao nhất** (Official Docs, chuẩn quốc tế, GitHub top stars, bài báo gốc). |
| **Subagent 3** | `wh5-challenger` | **5-Wh Critical Challenger** | `socratic-thinking-mentor` + `self-supervisor-meta-audit` | Phản bác trực diện yêu cầu/giải pháp bằng **5 câu hỏi Wh (`What`, `Why`, `Who`, `Where`, `When`)** để bắt điểm mù và rủi ro. |
| **Subagent 4** | `master-synthesizer` | **Master Synthesizer** | `rolling-summary-compactor` + `deep-research-and-synthesis` | Hợp nhất kết quả của Agent 1 + 2 + 3 thành bản tổng hợp cấu trúc **Minto BLUF** kèm bảng hóa giải 5 câu hỏi Wh để trình Chỉ huy. |

---

## 2. Giao thức Điều phối 2 Pha (2-Phase Execution)

*(Lưu ý: Cả 4 Subagents `req-analyst`, `trusted-scout`, `wh5-challenger`, `master-synthesizer` đã được cài đặt tĩnh trong `.agents/agents/`, gọi trực tiếp bằng `invoke_subagent` mà **không cần** gọi lại `define_subagent`).*

### Pha 1: Tung Mũi Giáp Công Ba Cánh Song Song (`Batch Turn 1`)
Gọi đồng thời (`invoke_subagent` trong cùng 1 lượt):
1. **`req-analyst`**: Phân tích yêu cầu của người dùng.
2. **`trusted-scout`**: Truy tìm các nguồn uy tín & được đề cử nhiều nhất cho bài toán.
3. **`wh5-challenger`**: Đặt 5 câu hỏi phản bác Wh (`What`, `Why`, `Who`, `Where`, `When`) đối với bài toán và các hướng tiếp cận phổ biến.

### Pha 2: Tổng hợp Cấp Subagent & Chỉ Huy Chốt Hạ (`Turn 2`)
1. Sau khi nhận báo cáo từ 3 Subagents đầu, gọi **`master-synthesizer`** để gom và đóng gói thành khung **BLUF + Ma trận Nguồn Uy Tín + Hóa giải 5-Wh**.
2. **Chỉ huy (Main Agent)** rà soát lần cuối, bổ sung kiểm chứng thực tế, cắt bỏ toàn bộ chi tiết thừa và xuất **Bản Tổng Hợp Cuối Cùng** gửi Người dùng.

---

## 3. Tinh Hoa Nâng Cấp & Kỷ Luật Ngân Sách Token (Hybrid Upgrades)
Kế thừa chọn lọc từ `obra/superpowers`, `BMAD-METHOD` và `wshobson/agents` nhưng loại bỏ hoàn toàn bệnh đốt token (*Theater of Agents*):
1. **Complexity Gate & Dual-Mode (Khớp 100% Luật 2.3 của `GEMINI.md`):**
   - **Full 4-Subagent Mode (Đa tiến trình):** Bật 4 tiến trình Subagent chạy song song khi **người dùng yêu cầu rõ** (gọi đội hình 4 subagent / đa tác tử), trong ca thu hoạch cuối chu kỳ 5h, hoặc khi bài toán nghiên cứu cần cô lập $>15.000$ token dữ liệu thô.
   - **Fast-Track Inline Mode (Mặc định tiết kiệm 100% phí nhân bản):** Trong tương tác thường khi người dùng không yêu cầu tách tiến trình Subagent, Chỉ huy tự đóng vai thực hiện nội tâm đủ 4 góc nhìn (`req-analyst` + `trusted-scout` + `wh5-challenger` + `master-synthesizer`) ngay trong 1 lượt phản hồi.
2. **2-Stage Verification Gate (Kế thừa từ `obra/superpowers`):** Trước khi Chỉ huy gửi bản tổng hợp cuối cho các tác vụ code/kỹ thuật, bắt buộc kiểm tra 2 chốt: **(a) Spec Compliance** (đúng tiêu chí của `req-analyst`) và **(b) Execution Proof** (`Exit Code = 0` thực tế).
3. **Ultra-Compact Artifact Checkpoint (Kế thừa từ `BMAD` + `rolling-summary-compactor`):** Với dự án kéo dài nhiều phiên, Subagent 4 xuất thêm khối `⚡ COMPACT STATE` ($\le 10$ dòng) để lưu trạng thái xuyên phiên mà không cần sinh hàng ngàn dòng PRD/Story rườm rà.
