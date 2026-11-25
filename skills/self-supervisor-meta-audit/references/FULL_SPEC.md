---
name: self-supervisor-meta-audit
description: >-
  Hệ thống tự giám sát nhận thức và kiểm toán đối kháng (Meta-Cognitive Self-Supervisor & Red-Team Audit).
  Sử dụng để phát hiện điểm mù tư duy, chống ảo giác hoàn thành sớm (premature completion),
  ép buộc kiểm thử điều kiện khắc nghiệt (offline/edge-case) và giám sát kỷ luật thực thi của AI.
---

# Hệ Thống Tự Giám Sát & Kiểm Toán Đối Kháng (Self-Supervisor Meta-Audit)

Tách biệt vai trò **"Người Thực Thi (Builder)"** và **"Kiểm Toán Đối Kháng (Red-Team Auditor)"** để triệt tiêu 5 điểm mù cấu trúc của LLM mà không làm phát sinh bước thừa.

## 1. Bản Đồ 5 Điểm Mù & Cơ Chế Khắc Chế Tức Thì

| Điểm mù của AI | Cơ chế Khắc chế Bắt buộc |
| :--- | :--- |
| **1. Thiên kiến tự xác nhận (Confirmation Bias)** | **Assumption Inversion:** Tự hỏi *"Điều kiện thực tế nào sẽ làm code/giải pháp này sập ngay khi chạy?"* |
| **2. Pha loãng sự chú ý (Attention Dilution)** | **PreInvocation Hook + Rolling State:** Giữ ngữ cảnh gọn, gộp lệnh vào 1 lượt (Batch Tool Calls). |
| **3. Ảo giác hoàn thành sớm (Reward Hacking)** | **Hostile Test:** Test cả ca khắc nghiệt (chặn mạng nếu yêu cầu offline, truyền dữ liệu rỗng/sai kiểu). |
| **4. Mù môi trường (Environment Blindness)** | **Zero-Trust Check:** Kiểm tra phụ thuộc ngầm (network call ẩn, biến môi trường, quyền đường dẫn). |
| **5. Đốt Token vô ích (Unchecked Token Burn)** | **0-Token CPU First:** Dùng script cục bộ kiểm tra tự động thay vì bật Subagent hay đọc toàn bộ file. |

## 2. Quy Trình 3 Chốt Chặn Kỷ Luật (3-Gate Discipline)

1. **Chốt 1 — Trước Khi Hành Động (Pre-Action Gate):**
   - **An toàn:** Thao tác có chạm file ngoài Workspace hay xóa dữ liệu người dùng không? (Có -> **DỪNG NGAY**).
   - **Tối ưu Chi phí:** Đã dùng `StartLine`/`EndLine` hoặc script cục bộ (`ctx_optimizer.py`) và gộp toàn bộ lệnh độc lập vào **cùng 1 lượt** chưa?
2. **Chốt 2 — Trong Khi Thực Thi (Adversarial Red-Team Gate):**
   - Kiểm tra **bẫy phụ thuộc ngầm** (thư viện tự gọi Internet tải model/config), **bẫy trạng thái cũ** (cache/file tạm từ lần chạy trước) và **bẫy Windows** (encoding `utf-8` vs `cp1252`, đường dẫn có khoảng trắng).
3. **Chốt 3 — Trước Khi Báo Cáo (Proof-of-Work Gate):**
   - **Không bằng chứng = Chưa xong:** Gộp lệnh chạy thử thực tế (`Exit Code = 0`) ngay trong lượt sửa cuối cùng.
