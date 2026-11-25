---
name: ui-ux-pro-max
description: >-
  Tiêu chuẩn thiết kế giao diện người dùng hiện đại, trực quan hóa dữ liệu và biểu đồ
  chuyên nghiệp (UI/UX Pro Max & Data Visualization). Sử dụng khi xây dựng Web App,
  Dashboard, HTML Widget, đồ thị khoa học hoặc trình bày bảng biểu.
---

# Thiết kế Giao diện & Trực quan hóa Chuyên nghiệp (UI/UX Pro Max)

## 1. Thẩm mỹ Hiện đại & Bố cục Rõ ràng (Visual Hierarchy & Aesthetics)
- **Phân cấp Thị giác:** Sử dụng hệ thống lưới (CSS Grid / Flexbox), khoảng trắng hợp lý và độ tương phản rõ ràng giữa tiêu đề, chỉ số chính (KPI) và nội dung chi tiết.
- **Bảng màu & Typography:** Ưu tiên bảng màu hài hòa (HSL/Tailwind), hỗ trợ tốt chế độ Sáng/Tối (Light/Dark mode) với độ tương phản dễ đọc (chuẩn WCAG AA).

## 2. Trải nghiệm Tương tác Mượt mà (Responsive & Interactive UX)
- Mọi thành phần tương tác (nút bấm, bộ lọc, bảng dữ liệu, tab) phải có trạng thái phản hồi rõ ràng (`hover`, `active`, `loading`, `empty state`).
- Tối ưu hiển thị trên cả màn hình máy tính lẫn kích thước thu nhỏ (Responsive Layout).

## 3. Trực quan hóa Dữ liệu & Đồ thị Khoa học (Data Visualization)
- Khi vẽ biểu đồ (HTML Canvas/SVG, Python Matplotlib/Seaborn, hoặc PGFPlots/TikZ): luôn có đầy đủ nhãn trục kèm đơn vị đo, chú giải (legend) không che khuất dữ liệu, và bảng màu phân biệt rõ ngay cả khi in đen trắng.

## 4. Kho Giao diện Cục bộ Toàn Hệ thống (`d:\UI`) & Chuẩn Mặc định `React Shadcn Codex`
- Khi thiết kế, tạo mới hoặc nâng cấp bất kỳ giao diện nào trên hệ thống, **luôn đề xuất người dùng chọn từ 5 kho giao diện tại `d:\UI`** và ưu tiên sử dụng **`[2] React Shadcn Codex` (`d:\UI\datasets\react-shadcn-codex\react_shadcn_codex.json`)** làm chuẩn mặc định (gồm **3,181 components** kết hợp `shadcn/ui`, `framer-motion` và `lucide-react`).
- **Quy trình Tra cứu Mẫu 0-Token (Không đọc thô file JSON 34 MB):**
  1. Thống kê nhóm component sẵn có:
     ```powershell
     python "d:\UI\ui_manager.py" types
     ```
  2. Tìm kiếm mẫu component phù hợp với yêu cầu:
     ```powershell
     python "d:\UI\ui_manager.py" search "<từ_khóa_giao_diện>" --limit 5
     ```
  3. Trích xuất mã nguồn đầy đủ của component theo ID:
     ```powershell
     python "d:\UI\ui_manager.py" get <ID>
     ```
- **Các kho bổ trợ tại `d:\UI`:**
  - `[1]` `d:\UI\components\shadcn-magicui\` (Full source `shadcn/ui` & `Magic UI`)
  - `[3]` `d:\UI\datasets\uigen\` (`UIGEN-T2.parquet` & `Hunter-Alpha-UIGEN-T3.jsonl`)
  - `[4]` `d:\UI\datasets\design2code\` (564 cặp `.png` ↔ `.html`/CSS Standard & HARD)
  - `[5]` `d:\UI\datasets\redesign-figma909\` (Layer JSON chuẩn Figma & Bounding Box)
