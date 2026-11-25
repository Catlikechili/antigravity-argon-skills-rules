---
name: word-ppt-report-builder
description: Chỉ kích hoạt khi người dùng yêu cầu tạo/xuất báo cáo Word (.docx) hoặc slide PowerPoint (.pptx).
---

# Tạo Tự động Báo cáo Word (`.docx`) & Slide PowerPoint (`.pptx`)

> Quy chuẩn chi tiết (cỡ chữ, lề A4, Nghị định 30/2020, bảng biểu): xem `references/FULL_SPEC.md`.

## 1. Sử dụng Engine Tự động (`scripts/report_engine.py`)
Luôn dùng `WordReportBuilder`, `PPTReportBuilder`, và `verify_outputs` từ `report_engine.py` (đã tích hợp sẵn font tiếng Việt 4 vùng XML, bảng Zebra, thẻ KPI, chống tràn slide 16:9):

```python
import sys
sys.path.append(r"C:\Users\CVLONG\.gemini\config\skills\word-ppt-report-builder\scripts")
from report_engine import WordReportBuilder, PPTReportBuilder, verify_outputs

# 1. Word (.docx): mode="modern" (Kỹ thuật/Doanh nghiệp) hoặc mode="nd30" (Nghị định 30/2020)
doc = WordReportBuilder(title="TIÊU ĐỀ", subtitle="Phụ đề", author="Tác giả", mode="modern")
doc.add_cover_header(org_name="ĐƠN VỊ", doc_code="BC-2026")
doc.add_callout("TÓM TẮT ĐIỀU HÀNH", "Nội dung cốt lõi...", tone="info")
doc.add_heading("1. Mục lớn", level=1)
doc.add_paragraph("Nội dung đoạn văn...")
doc.add_kpi_summary([("Chỉ số 1", "99.2%", "+4.2%"), ("Thời gian", "1.8 ms", "-35%")])
doc.add_styled_table(headers=["Cột 1", "Cột 2"], rows=[["A", "100"]], col_widths_cm=[8.0, 8.2], caption="Bảng 1: ...")
doc.save("output.docx")

# 2. PowerPoint (.pptx): Widescreen 16:9, Action Titles, Zero-Overflow
ppt = PPTReportBuilder(title="TIÊU ĐỀ", subtitle="Phụ đề", author="Tác giả")
ppt.add_title_slide()
ppt.add_kpi_slide(
    action_title="Nhận định có số liệu cốt lõi (Action Title)",
    section_tag="01 | TỔNG QUAN",
    kpis=[("99.2%", "Nhãn KPI", "Ghi chú")],
    takeaways=["Luận điểm chính 1 (<= 20 từ).", "Luận điểm chính 2."]
)
ppt.save("output.pptx")
print(verify_outputs("output.docx", "output.pptx"))
```
- Hoặc gọi qua CLI JSON: `python "C:\Users\CVLONG\.gemini\config\skills\word-ppt-report-builder\scripts\report_engine.py" --spec report_spec.json`
