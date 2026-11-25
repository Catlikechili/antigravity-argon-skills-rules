---
name: self-improving-harness
description: Hệ thống Tự Tiến Hóa Kỹ Năng & Bộ Nhớ Kinh Nghiệm 0-Token (ACE + Agentic Harness Engineering). Kích hoạt ở đầu phiên để nạp ngữ cảnh nhẹ, khi gặp lỗi lặp lại để tra cứu 0-token, hoặc cuối phiên để đúc kết bài học và đề xuất nâng cấp Skill (Shadow Proposals) có kiểm toán bảo mật.
---

# Hệ Thống Tự Cải Tiến Khép Kín (Self-Improving Harness — ACE & AHE)

> Dựa trên **Agentic Context Engineering (ACE)** và **Agentic Harness Engineering (Lilian Weng)**: 3 trụ cột quan sát (*Component*, *Experience*, *Decision*), chống *Context Collapse* (trần $\le 30$ bài học), chống *Reward Hacking* (Verifier độc lập + Read-Only Core Guard).

## 1. Khởi động Đầu Phiên (0-Token Bootstrap — `< 0.5s`)
Chạy ngay bằng `run_command` khi bắt đầu tác vụ kỹ thuật phức tạp:
```powershell
python "d:\Gravity\.agents\self_harness\tools_0token\env_health_guard.py"
python "d:\Gravity\.agents\self_harness\ace_miner.py" show --top 15
```

## 2. Tra Cứu Lỗi Tức Thì Khi Gặp Sự Cố (0-Token Error Lookup)
Trước khi gọi LLM suy đoán hoặc thử-sai (Shotgun Debugging), tra cứu ngay lỗi từ Sổ tay & Lịch sử:
```powershell
python "d:\Gravity\.agents\self_harness\tools_0token\fast_error_lookup.py" "<thông_báo_lỗi>" --deep
```

## 3. Vòng Lặp Tiến Hóa Cuối Phiên (Experience -> Shadow Proposals -> Verifier)
1. **Khai thác bài học từ Transcript (`ace_miner.py`):**
   ```powershell
   python "d:\Gravity\.agents\self_harness\ace_miner.py" scan
   ```
2. **Kiểm toán 18 Skills & Đóng gói công cụ (`skill_evolver.py`):**
   ```powershell
   python "d:\Gravity\.agents\self_harness\skill_evolver.py" audit-skills
   python "d:\Gravity\.agents\self_harness\skill_evolver.py" synthesize-tools
   python "d:\Gravity\.agents\self_harness\skill_evolver.py" propose
   ```
3. **Duyệt & Áp dụng Đề xuất An toàn (Human-in-the-Loop):**
   - Xem bảng tổng hợp tại `d:\Gravity\.agents\self_harness\proposals_manifesto.md`.
   - Áp dụng 1 đề xuất đã kiểm chứng:
     ```powershell
     python "d:\Gravity\.agents\self_harness\skill_evolver.py" apply PROP-001
     ```
4. **Kiểm định Độc lập (Zero-Trust Regression Guard):**
   ```powershell
   python "d:\Gravity\.agents\self_harness\harness_verifier.py"
   ```

## 4. Quy tắc Bất Khả Xâm Phạm (Read-Only Core Guard)
- Mọi đề xuất tự động trong `skill_evolver.py` **tuyệt đối không được** sửa `GEMINI.md` (An toàn dữ liệu Mục 1, Không gia hạn thanh toán Mục 7), `harness_verifier.py`, hoặc đường dẫn ngoài Workspace `d:\Gravity`.
- Mọi thao tác Python trên Windows bắt buộc gọi `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` và PowerShell dùng here-string `@' ... '@ | python -`.
