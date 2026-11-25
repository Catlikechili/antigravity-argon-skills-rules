---
trigger: always_on
description: Quy tắc tự động phân loại, xếp hạng và giải phẫu bài báo khoa học 3 vòng tại d:\Research_Papers.
---

# Quy tắc Thẩm định & Giải phẫu Bài báo Khoa học (`d:\Research_Papers`)

1. **0-Token PDF Triage (Cấm đọc thô toàn bộ thư mục `papers/`):**
   - Luôn chạy `python "d:\Research_Papers\.agents\skills\paper-triage-reviewer\scripts\scan_papers.py" --dir "d:\Research_Papers\papers" --out-md "d:\Research_Papers\index_triage.md" --out-json "d:\Research_Papers\triage_data.json"` để quét, trích xuất DOI/Title/Year và tra cứu OpenAlex/Crossref tự động.
   - Khi cần trích xuất văn bản của 1 bài PDF cụ thể để đọc sâu: dùng cờ `--extract "d:\Research_Papers\papers\<ten_file>.pdf"`.
2. **Phân luồng Uy tín & Độ mới:**
   - **Tier 1 (Ưu tiên cốt lõi):** ScienceDirect / Elsevier (`10.1016`), IEEE (`10.1109`), Nature Portfolio (`10.1038`).
   - **Tier 2 (Uy tín mở rộng):** Science / AAAS (`10.1126`), ACM (`10.1145`), Springer (`10.1007`), Wiley, OUP, CUP, APS, SIAM, AIAA.
   - **Tách bạch Preprint:** `arXiv` / `TechRxiv` chưa có DOI tạp chí chính thức phải tách riêng xuống khu vực cảnh báo.
3. **Giải phẫu Đối kháng 3 Vòng (3-Pass Adversarial Review):**
   - Sử dụng mẫu chuẩn tại `d:\Research_Papers\.agents\skills\paper-triage-reviewer\resources\paper_review_template.md`.
   - Lưu kết quả phân tích chuẩn UTF-8 vào `d:\Research_Papers\notes\<Nam>_<Nguon>_<Ten-ngan>.md`.
4. **An toàn Dữ liệu:**
   - Tuyệt đối không xóa, đổi tên hoặc di chuyển các file PDF gốc trong `d:\Research_Papers\papers\`.
