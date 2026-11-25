---
name: word-ppt-report-builder
description: >-
  Thiết kế và tạo tự động báo cáo chuyên nghiệp ra file Word (.docx) và slide
  thuyết trình PowerPoint (.pptx) chuẩn định dạng văn bản Việt Nam (Nghị định
  30/2020/NĐ-CP, báo cáo kỹ thuật/khoa học/kinh doanh), tích hợp bảng số liệu,
  biểu đồ độ phân giải cao (300 DPI) và kiểm tra chống tràn lề tự động. Kích
  hoạt khi người dùng yêu cầu làm báo cáo Word, tạo slide PowerPoint, xuất
  thuyết trình (.pptx) hoặc chuyển đổi dữ liệu/mã nguồn thành tài liệu báo cáo.
---

# Quy chuẩn Thiết kế & Tự động hóa Báo cáo Word (`.docx`) & PowerPoint (`.pptx`)

Skill này cung cấp bộ quy chuẩn trình bày, kiến trúc bố cục và công cụ tự động hóa (`report_engine.py`) giúp tạo ra các bản báo cáo Word và bài thuyết trình PowerPoint hoàn chỉnh, chuẩn font tiếng Việt Unicode, sắc nét và không bao giờ bị lỗi vỡ khung hay tràn chữ.

---

## 1. Quy chuẩn Trình bày Báo cáo Word (`.docx`)

### 1.1. Hai Chế độ Định dạng Chuẩn (Preset Modes)
1. **Chế độ Báo cáo Kỹ thuật / Doanh nghiệp (`mode="modern"` - Mặc định):**
   - **Khổ giấy & Căn lề:** A4 (`210 x 297 mm`), Lề Trái `2.8 cm` (đóng gáy), Lề Phải `2.0 cm`, Lề Trên `2.2 cm`, Lề Dưới `2.2 cm`.
   - **Font chữ chuẩn tiếng Việt:** `Times New Roman` hoặc `Arial`/`Segoe UI` đồng bộ cho cả 4 vùng XML (`w:ascii`, `w:hAnsi`, `w:eastAsia`, `w:cs`) để **triệt tiêu 100% lỗi nhảy font chữ có dấu tiếng Việt**.
   - **Hệ thống phân cấp tiêu đề (Heading Hierarchy):**
     - `Title` (Bìa / Đầu trang): `18–22 pt`, Đậm, Màu Navy đậm (`#1B365D`).
     - `Heading 1` (Chương / Phần lớn): `14 pt`, Đậm, IN HOA, Màu Navy (`#1B365D`), khoảng cách trên `12 pt`, dưới `6 pt`.
     - `Heading 2` (Mục lớn): `13 pt`, Đậm, Màu Xanh Slate (`#2C5282`), khoảng cách trên `8 pt`, dưới `4 pt`.
     - `Heading 3` (Tiểu mục): `12 pt`, Đậm Nghiêng, Màu Xám Đậm (`#2D3748`).
     - `Normal` (Nội dung chính): `12 pt` (hoặc `13 pt`), Căn đều 2 bên (`WD_ALIGN_PARAGRAPH.JUSTIFY`), giãn dòng `1.25–1.35`, khoảng cách đoạn `6 pt`.
2. **Chế độ Hành chính / Nhà nước Việt Nam (`mode="nd30"` - Chuẩn Nghị định 30/2020/NĐ-CP):**
   - **Khổ giấy & Căn lề cứng:** A4, Lề Trên `2.0 cm`, Lề Dưới `2.0 cm`, Lề Trái `3.0 cm`, Lề Phải `1.5 cm`.
   - **Font chữ bắt buộc:** `Times New Roman`, cỡ chữ nội dung `13–14 pt`, lùi đầu dòng đoạn văn `1.27 cm` (`1 tab`), giãn dòng `1.2–1.5 lines`.
   - **Quốc hiệu & Tiêu ngữ:** Chia bảng 2 cột không viền ở đầu trang 1 (Cột trái: Cơ quan chủ quản & Số/Ký hiệu; Cột phải: `CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM` / `Độc lập - Tự do - Hạnh phúc`).

### 1.2. Quy tắc Bảng biểu & Hình ảnh trong Word
- **Bảng dữ liệu (Tables):**
  - Luôn đặt `table.autofit = False` và gán độ rộng cột tường minh phù hợp với chiều rộng khả dụng (`16.2 cm` ở chế độ Modern, `16.5 cm` ở chế độ NĐ30).
  - Hàng tiêu đề (Header Row): Nền xanh đậm (`#1B365D`), chữ Trắng Đậm, căn giữa, bật thuộc tính **lặp lại tiêu đề khi sang trang mới** (`w:tblHeader`).
  - Hàng dữ liệu: Kẻ sọc xen kẽ (Zebra striping `#F4F7FA` / `#FFFFFF`), số liệu căn phải (`RIGHT`), mã/trạng thái căn giữa (`CENTER`), diễn giải căn trái (`LEFT`).
  - Không để dòng bảng bị cắt đôi giữa 2 trang (`w:cantSplit`).
- **Biểu đồ & Hình ảnh:**
  - Xuất từ `matplotlib` ở độ phân giải tối thiểu **`300 DPI`**, `bbox_inches='tight'`, chèn vào Word với chiều rộng `14.5–15.5 cm` kèm dòng chú thích (*Hình X: ...*) căn giữa nghiêng ngay bên dưới.
- **Khối Callout / Kết luận quan trọng:**
  - Dùng bảng 1 ô có viền trái dày `24 pt` (tương đương `3 pt` hiển thị) màu xanh/cam và nền nhạt (`#EDF2F7`) để làm nổi bật **Executive Summary**, **Cảnh báo kỹ thuật** hoặc **Kiến nghị**.

---

## 2. Quy chuẩn Thiết kế Slide PowerPoint (`.pptx`)

### 2.1. Kích thước & Bố cục Lưới (16:9 Widescreen Grid)
- **Tỷ lệ bắt buộc:** Widescreen 16:9 (`13.333 x 7.5 inches`).
- **Nguyên tắc Tư vấn Chiến lược (McKinsey / BCG Action Titles):**
  - Tiêu đề mỗi slide **không chỉ viết tên mục** (VD: *"Kết quả thử nghiệm"*), mà phải là **một nhận định chứa số liệu cốt lõi** (VD: *"Thuật toán MPPT mới giúp tăng hiệu suất bám điểm công suất cực đại lên 99.4%, giảm 42% dao động"*).
- **Quy tắc Chống Tràn Chữ (Zero-Overflow Rule):**
  - Tối đa **5–6 gạch đầu dòng / khung**, mỗi gạch đầu dòng tối đa **18–22 từ**.
  - Nếu nội dung dài hơn, **bắt buộc chia thành bố cục 2 cột (Two-Column Split)**, **Lưới thẻ KPI (Metric Cards)**, hoặc tách sang slide tiếp theo.
  - Cỡ chữ an toàn: Tiêu đề Slide `24–28 pt` (Đậm), Tiêu đề Khung/Card `16–18 pt` (Đậm), Nội dung chính `14–16 pt`, Chú thích nguồn `10–11 pt`.

### 2.2. Các Mẫu Layout Slide Chủ lực (Slide Archetypes)
1. **Slide Bìa (`Title Cover`):** Nền Navy đậm chủ đạo, thanh điểm nhấn (Accent Bar), tiêu đề lớn, phụ đề, tác giả/đơn vị và ngày báo cáo.
2. **Slide Tổng quan Chỉ số (`KPI Metric Cards + Summary`):** Hàng trên gồm 3–4 thẻ KPI lớn hiển thị con số nổi bật (`28–32 pt` Đậm + nhãn mô tả), hàng dưới là nhận định phân tích hoặc bảng tóm tắt.
3. **Slide So sánh / Phân tích 2 Cột (`Two-Column Comparison / Text + Chart`):** Cột trái trình bày luận điểm kỹ thuật / nguyên nhân; cột phải hiển thị bảng số liệu hoặc biểu đồ trực quan (`300 DPI`).
4. **Slide Bảng Dữ liệu Chi tiết (`Data Table Slide`):** Bảng được tô màu Header và Zebra striping rõ ràng, tự động căn chỉnh kích thước chữ theo số dòng.
5. **Slide Lộ trình / Quy trình (`Process / Roadmap Cards`):** Các bước thực hiện xếp ngang theo luồng công việc rõ ràng.

---

## 3. Quy trình Thực thi Tự động (3-Step Execution Workflow)

Khi người dùng yêu cầu tạo báo cáo Word và/hoặc PowerPoint:

### Bước 1: Chuẩn hóa Nội dung & Biểu đồ (Data & Chart Preparation)
- Nếu có dữ liệu thực tế trong Workspace (`.csv`, `.json`, `.xlsx`, log hệ thống), viết script trích xuất các con số thống kê chính xác (Zero Hallucination).
- Nếu báo cáo có số liệu chuỗi thời gian hoặc so sánh, dùng `matplotlib` xuất biểu đồ `.png` (`dpi=300`, font tiếng Việt rõ ràng) vào thư mục `scratch` hoặc thư mục đầu ra trước khi nhúng vào tài liệu.

### Bước 2: Gọi Engine Tạo Báo cáo (`scripts/report_engine.py`)
- Sử dụng trực tiếp module `report_engine.py` đi kèm trong skill này:
  - Đường dẫn Workspace: `d:\Gravity\.agents\skills\word-ppt-report-builder\scripts\report_engine.py`
  - Đường dẫn Global: `C:\Users\CVLONG\.gemini\config\skills\word-ppt-report-builder\scripts\report_engine.py`
- Bạn có thể:
  1. **Import trực tiếp** các lớp `WordReportBuilder` và `PPTReportBuilder` trong script Python để tùy biến linh hoạt.
  2. **Hoặc truyền file cấu hình JSON** qua CLI:
     ```powershell
     python "C:\Users\CVLONG\.gemini\config\skills\word-ppt-report-builder\scripts\report_engine.py" --spec path/to/report_spec.json
     ```

### Bước 3: Kiểm định Chất lượng Trước khi Bàn giao (Zero-Trust Verification)
- Chạy hàm `verify_outputs(docx_path, pptx_path)` (đã tích hợp sẵn trong `report_engine.py`) để kiểm tra:
  - File tồn tại, dung lượng `> 0 bytes`, mở lại được bằng `python-docx` / `python-pptx` không lỗi XML.
  - Kiểm tra số trang/mục trong Word và số slide trong PowerPoint.
  - Cảnh báo tự động nếu có bất kỳ khung văn bản nào trong Slide vượt ngưỡng ký tự gây nguy cơ tràn lề.
- Luôn xử lý ngoại lệ `PermissionError` (khi người dùng đang mở file Word/PPT trên máy): tự động lưu sang tên dự phòng hoặc thông báo rõ ràng.

---

## 4. Mẫu Code Gọi Nhanh (`WordReportBuilder` & `PPTReportBuilder`)

```python
import sys
sys.path.append(r"C:\Users\CVLONG\.gemini\config\skills\word-ppt-report-builder\scripts")
from report_engine import WordReportBuilder, PPTReportBuilder, verify_outputs

# 1. Tạo Báo cáo Word (.docx)
doc = WordReportBuilder(
    title="BÁO CÁO KẾT QUẢ THỬ NGHIỆM HỆ THỐNG",
    subtitle="Đánh giá hiệu năng thuật toán điều khiển và độ ổn định thời gian thực",
    author="Phòng Nghiên cứu & Phát triển (R&D)",
    mode="modern"  # hoặc "nd30" cho chuẩn hành chính Nghị định 30/2020
)
doc.add_cover_header(org_name="CÔNG TY CÔNG NGHỆ CAO", doc_code="BC-KT/2026-01")
doc.add_callout(
    "TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)",
    "Hệ thống đạt hiệu suất trung bình 99.2%, vượt chỉ tiêu thiết kế 4.2% và hoạt động ổn định liên tục.",
    tone="info"
)
doc.add_heading("1. Tổng quan & Mục tiêu Đánh giá", level=1)
doc.add_paragraph("Báo cáo này tổng hợp số liệu đo đạc thực nghiệm trên mô hình phần cứng...")
doc.add_kpi_summary([
    ("Hiệu suất TB", "99.2%", "+4.2% so với chuẩn"),
    ("Thời gian đáp ứng", "1.8 ms", "Nhanh hơn 35%"),
    ("Độ ổn định", "100%", "0 lỗi phát sinh")
])
doc.add_styled_table(
    headers=["Thông số", "Đơn vị", "Giá trị Đo", "Đánh giá"],
    rows=[
        ["Điện áp đầu vào", "V", "24.05", "Đạt"],
        ["Dòng điện cực đại", "A", "12.40", "Đạt"]
    ],
    col_widths_cm=[6.0, 2.5, 3.7, 4.0],
    caption="Bảng 1: Kết quả đo kiểm các thông số chính."
)
doc.save("Bao_Cao_Ky_Thuat.docx")

# 2. Tạo Slide PowerPoint (.pptx)
ppt = PPTReportBuilder(
    title="BÁO CÁO KẾT QUẢ THỬ NGHIỆM HỆ THỐNG",
    subtitle="Đánh giá Hiệu năng & Độ ổn định Thời gian thực",
    author="Phòng R&D | Tháng 11/2026"
)
ppt.add_title_slide()
ppt.add_kpi_slide(
    action_title="Hệ thống vượt toàn bộ chỉ tiêu kỹ thuật với hiệu suất đạt 99.2%",
    section_tag="01 | TỔNG QUAN KẾT QUẢ",
    kpis=[
        ("99.2%", "Hiệu suất Bám MPPT", "+4.2% so với mục tiêu"),
        ("1.8 ms", "Thời gian Đáp ứng", "Giảm 35% độ trễ"),
        ("0 lỗi", "Độ tin cậy Vận hành", "Chạy liên tục 1000 chu kỳ")
    ],
    takeaways=[
        "Thuật toán điều khiển vòng kín hội tụ nhanh trong mọi kịch bản tải.",
        "Biên độ dao động quanh điểm làm việc giảm xuống dưới 0.15%."
    ]
)
ppt.save("Slide_Bao_Cao_Ky_Thuat.pptx")

# 3. Kiểm tra đầu ra
print(verify_outputs("Bao_Cao_Ky_Thuat.docx", "Slide_Bao_Cao_Ky_Thuat.pptx"))
```
