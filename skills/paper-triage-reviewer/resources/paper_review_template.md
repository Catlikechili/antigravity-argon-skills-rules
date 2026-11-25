---
title: "{{TITLE}}"
authors: "{{AUTHORS}}"
year: {{YEAR}}
pub_date: "{{PUB_DATE}}"
venue: "{{VENUE}}"
venue_tier: "{{TIER_BADGE}}" # Tier-1 (IEEE / ScienceDirect / Nature) | Tier-2
doi: "{{DOI}}"
citations: {{CITATIONS}}
citations_per_year: {{CPY}}
track: "{{TRACK}}" # FRONTIER_NEW (Độ mới học thuật) | SEMINAL_CORE (Nền tảng trích dẫn cao)
status: "unread" # unread | pass1_triaged | pass2_structured | pass3_dissected
---

# {{TITLE}}

> **Định vị nhanh (1 câu):** Bài báo thuộc nhánh **[Độ mới SOTA / Nền tảng gốc]** đăng trên **{{VENUE}} ({{YEAR}})**, giải quyết nút thắt `[Nút thắt cũ]` bằng ý tưởng cốt lõi `[Vũ khí đột phá duy nhất]`.

---

## Vòng 1: Thẩm định Nguồn & Tầm vóc Học thuật (5 - 10 phút)

- **Kiểm chứng nguồn xuất bản:**
  - Nhà xuất bản / Tạp chí: `{{VENUE}}` — DOI: `https://doi.org/{{DOI}}`
  - Bậc uy tín: `[ ] ScienceDirect (Elsevier)` | `[ ] IEEE` | `[ ] Nature Portfolio` | `[ ] Nguồn uy tín khác (ACM/Science/Springer)`
- **Lý do bài báo này vượt vòng lọc (Chọn 1 hoặc cả 2):**
  - `[ ]` **Độ mới học thuật (Frontier Novelty):** Đề xuất kiến trúc / công thức / phát hiện mới chưa từng có trong 2-3 năm gần đây. Điểm mới thực sự nằm ở: `...`
  - `[ ]` **Bài báo nền tảng (Seminal Foundation):** Có `{{CITATIONS}}` trích dẫn (`{{CPY}}`/năm), đặt nền móng lý thuyết hoặc chuẩn so sánh (benchmark) cho toàn bộ các bài đời sau.
- **5 chữ C (Five-Cs Check):**
  1. **Category (Thể loại):** Lý thuyết toán học / Thuật toán / Thực nghiệm phần cứng / Survey tổng quan?
  2. **Context (Phả hệ):** Kế thừa trực tiếp từ bài nền tảng nào? Phá vỡ giới hạn nào của hướng cũ?
  3. **Contributions (Đóng góp tuyên bố vs. Thực chất):** Tác giả tuyên bố 3-4 đóng góp, nhưng đóng góp **thực chất đắt giá nhất** là gì?
  4. **Correctness (Tính hợp lý sơ bộ):** Các giả định đầu vào có hợp lý về mặt vật lý/toán học không?
  5. **Clarity (Độ mạch lạc):** Ký hiệu toán và sơ đồ khối có tường minh, đủ thông tin tái lập không?
- **Quyết định sau Vòng 1:** `[ ] Dừng tại đây` | `[ ] Đọc Vòng 2` | `[ ] Giải phẫu Vòng 3`

---

## Vòng 2: Giải mã Kiến trúc, Toán học & Bằng chứng (30 - 60 phút)

### 2.1. Bản chất Đột phá (Core Formulation)
- **Đầu vào $\rightarrow$ Đầu ra & Ràng buộc:** `...`
- **Công thức / Cơ chế hạt nhân** *(Viết lại bằng lời và ký hiệu gọn nhất)*:
  $$...$$
- **Sự khác biệt cốt lõi so với phương pháp tiền nhiệm:** Không chỉ "thêm module", mà tại sao thay đổi này lại giải quyết được bài toán gốc?

### 2.2. Thẩm định Biểu đồ & Số liệu (Che chữ, đọc hình trước)
- **Hình / Bảng đắt giá nhất (Figure/Table số mấy?):** `...`
- **Đối chiếu tuyên bố vs. số liệu thật:** Mức cải thiện thực tế là bao nhiêu %? Có đánh đổi ngầm về độ phức tạp tính toán, dữ liệu huấn luyện hay điều kiện biên không?

---

## Vòng 3: Phản biện Học thuật & Tìm "Điểm Gãy" (Adversarial Critique)

| Khía cạnh soi xét | Tuyên bố của tác giả | Phản biện / Điểm gãy thực tế (Khi nào phương pháp này sập?) |
| :--- | :--- | :--- |
| **Giả định ngầm (Hidden Assumptions)** | ... | Nếu bỏ giả định nhiễu lý tưởng / phân phối chuẩn / đồng bộ hoàn hảo thì sao? |
| **Tính công bằng của Baseline** | ... | Tác giả có so sánh với SOTA mới nhất từ IEEE/Nature/Elsevier cùng thời điểm không, hay chọn baseline cũ/yếu? |
| **Ablation Study (Cắt bỏ thành phần)** | ... | Nếu bỏ khối phức tạp nhất đi, hiệu năng giảm mạnh hay chỉ giảm 0.5% trong sai số thống kê? |
| **Trường hợp biên bị né tránh** | ... | Dữ liệu thưa, nhiễu lớn, kích thước mẫu nhỏ, hoặc độ phức tạp $O(N^2)$ khi mở rộng quy mô. |

---

## 4. Nối dây Tri thức & Khai thác cho Nghiên cứu Riêng

- **Truy nguồn quá khứ (Backward Links — Nền tảng cần đọc thêm):**
  - `[Citation 1]` — Bài gốc tạo ra khái niệm/công thức nền mà bài này dựa vào.
- **Hướng mở tương lai (Forward Gap — Ý tưởng nghiên cứu mới):**
  - Bài báo đã giải quyết xong **Vấn đề A**, nhưng lại làm lộ ra **Vấn đề B**: `...`
- **Tài sản tái sử dụng ngay:** Công thức số `(?)`, bộ tham số chuẩn ở Bảng `(?)`, hoặc link mã nguồn/dataset: `...`
