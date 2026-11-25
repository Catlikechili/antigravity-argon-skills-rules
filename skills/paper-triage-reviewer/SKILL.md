---
name: paper-triage-reviewer
description: Scans local PDF folders (default d:\Research_Papers\papers) or queries OpenAlex/Crossref to filter reputable academic venues (ScienceDirect/Elsevier, IEEE, Nature, Science, ACM, Springer), ranks papers by academic recency (Newest First) alongside high-citation seminal foundations, and writes 3-pass adversarial reviews into d:\Research_Papers\notes. Trigger whenever the user asks to scan papers, filter recent/novel or highly-cited foundational papers, rank literature, or review/dissect scientific PDFs.
---

# Paper Triage & Adversarial Reviewer (Antigravity Skill)

Quy trình tự động thẩm định bài báo khoa học cho workspace `d:\Research_Papers` (và toàn hệ thống **Google Antigravity**): lọc nghiêm ngặt nguồn xuất bản uy tín, xếp hạng theo độ mới học thuật (Newest First), giữ lại các bài nền tảng trích dẫn cao (Seminal), và giải phẫu "điểm gãy" từng bài theo 3 vòng.

## 1. Quy tắc Nguồn Uy Tín & Phân Luồng

- **Tier 1 (Ưu tiên cốt lõi):** **ScienceDirect / Elsevier** (`10.1016`), **IEEE** (`10.1109`), **Nature Portfolio** (`10.1038`).
- **Tier 2 (Uy tín quốc tế mở rộng):** **Science / AAAS** (`10.1126`), **ACM** (`10.1145`), **Springer** (`10.1007`), **Wiley**, **Oxford/Cambridge Press**, **APS**, **SIAM**, **AIAA**.
- **Tách bạch nguồn chưa bình duyệt:** Bản nháp `arXiv` / `TechRxiv` chưa có DOI tạp chí chính thức hoặc nguồn lạ phải đưa xuống khu vực kiểm chứng riêng.
- **Sắp xếp & Phân nhãn kép:**
  - Bảng chính (`index_triage.md`) luôn xếp **giảm dần theo ngày/năm xuất bản (bài mới nhất lên đầu)**.
  - Gắn nhãn tách biệt: **`FRONTIER_NEW` / `FRONTIER_STAR`** (Độ mới 3 năm gần nhất) và **`SEMINAL_CORE`** (Bài nền tảng $\ge 100$ trích dẫn hoặc $\ge 15$ trích dẫn/năm).

## 2. Quy trình Thực thi 0-Token trên Antigravity

### Bước 1: Chạy Script Quét & Xếp Hạng (Black-box Script)

Không đọc thô hàng loạt file PDF vào ngữ cảnh. Chạy trực tiếp script (hoạt động từ mọi thư mục trên máy):

- **Quét các file PDF trong thư mục `d:\Research_Papers\papers`:**

  ```powershell
  python "d:\Research_Papers\.agents\skills\paper-triage-reviewer\scripts\scan_papers.py" --dir "d:\Research_Papers\papers" --out-md "d:\Research_Papers\index_triage.md" --out-json "d:\Research_Papers\triage_data.json"
  ```

- **Quét kèm tìm kiếm trực tuyến theo chủ đề từ nguồn uy tín (OpenAlex/Crossref, không cần API key):**

  ```powershell
  python "d:\Research_Papers\.agents\skills\paper-triage-reviewer\scripts\scan_papers.py" --dir "d:\Research_Papers\papers" --search "<English topic keywords>" --max-results 25 --out-md "d:\Research_Papers\index_triage.md" --out-json "d:\Research_Papers\triage_data.json"
  ```

- **Chế độ Offline (khi mất mạng):** Thêm cờ `--offline`.

### Bước 2: Báo cáo Bảng Điều Phối

Đọc `d:\Research_Papers\index_triage.md` và `d:\Research_Papers\triage_data.json` để tóm tắt cho người dùng:
1. Danh sách các bài đạt chuẩn **IEEE / ScienceDirect / Nature / Tier-2** theo thứ tự mới nhất.
2. Đề xuất **Top 3 bài Mới nhất (Frontier)** và **Top 3 bài Nền tảng nhiều trích dẫn nhất (Seminal)**.
3. Cảnh báo các file bị đẩy xuống nhóm *Preprint / Chưa xác thực nguồn* (nếu có) và hỏi người dùng chọn bài nào để giải phẫu sâu.

### Bước 3: Giải phẫu Bài báo 3 Lượt (Adversarial Review)

Khi người dùng chọn bài cần mổ xẻ chi tiết:
1. Đọc mẫu chuẩn tại `d:\Research_Papers\.agents\skills\paper-triage-reviewer\resources\paper_review_template.md`.
2. Trích xuất nội dung PDF bằng script 0-token (`--extract "<đường_dẫn_pdf>" --max-pages 30`) hoặc đọc trực tiếp file PDF và điền đầy đủ 3 vòng thẩm định:
   - **Vòng 1:** Xác thực nguồn, vị thế học thuật (Frontier vs. Seminal) và 5 chữ C.
   - **Vòng 2:** Công thức hạt nhân và đối chiếu biểu đồ/số liệu thực tế.
   - **Vòng 3:** Phản biện giả định ngầm, tính công bằng của baseline, Ablation Study và điểm gãy điều kiện biên.
3. Xuất file kết quả chuẩn UTF-8 vào `d:\Research_Papers\notes\<Nam>_<Nguon>_<Ten-ngan>.md`.

## 3. An toàn Dữ liệu

- Tuyệt đối không xóa, đổi tên hoặc di chuyển file PDF gốc trong `d:\Research_Papers\papers` khi chưa được yêu cầu rõ ràng.
