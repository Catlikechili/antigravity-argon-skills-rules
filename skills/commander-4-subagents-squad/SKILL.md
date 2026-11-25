---
name: commander-4-subagents-squad
description: Chỉ kích hoạt khi người dùng yêu cầu rõ Đội hình 4 Subagents (req-analyst, trusted-scout, wh5-challenger, master-synthesizer).
---

# Đội hình 4 Subagents (Commander & 4-Subagent Squad)

> Chi tiết đầy đủ: `references/FULL_SPEC.md` (Chỉ đọc khi cần tra cứu sâu).

## 1. Phân công 4 Subagents (Đã cài tĩnh, gọi trực tiếp `invoke_subagent`)
1. `req-analyst` (**Requirement Analyst**): Bóc tách mục tiêu cốt lõi, phạm vi, ràng buộc, 3–5 tiêu chí nghiệm thu ($\le 15$ dòng).
2. `trusted-scout` (**Trusted Source Scout**): Lọc nguồn uy tín cao nhất (Official Docs, RFC, GitHub top stars, bài báo gốc), đối chiếu $\ge 2$ nguồn ($\le 15$ dòng).
3. `wh5-challenger` (**5-Wh Critical Challenger**): Phản bác giải pháp bằng đúng 5 câu hỏi `What`, `Why`, `Who`, `Where`, `When` + hướng khắc phục ($\le 15$ dòng).
4. `master-synthesizer` (**Master Synthesizer**): Hợp nhất kết quả Agent 1+2+3 theo chuẩn **Minto BLUF + Ma trận Nguồn + Hóa giải 5-Wh**.

## 2. Giao thức Thực thi 2 Chế độ
- **Fast-Track Inline Mode (Mặc định tiết kiệm 100% phí nhân bản):** Khi người dùng không yêu cầu tách tiến trình Subagent, Main Agent tự thực hiện nội tâm đủ 4 góc nhìn ngay trong 1 lượt.
- **Full 4-Subagent Mode (Khi có lệnh rõ hoặc dữ liệu thô $>15.000$ tokens):**
  - **Pha 1 (Batch Turn 1):** Gọi song song `req-analyst`, `trusted-scout`, `wh5-challenger` (ưu tiên `Model="flash"` hoặc `"flash_lite"` cho bước quét).
  - **Pha 2 (Turn 2):** Gọi `master-synthesizer` tổng hợp BLUF $\rightarrow$ Chỉ huy kiểm chứng (`Spec Compliance` + `Exit Code = 0`) rồi gửi người dùng.
