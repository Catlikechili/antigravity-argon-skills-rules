---
trigger: always_on
description: Tự động đề xuất và sử dụng kho giao diện cục bộ tại d:\UI (ưu tiên số 1: React Shadcn Codex) mỗi khi người dùng cần thiết kế, code hoặc nâng cấp giao diện.
---

# Quy tắc Đề xuất & Truy xuất Giao diện Toàn Hệ thống từ Kho Cục bộ (`d:\UI`)

Mỗi khi người dùng yêu cầu thiết kế, tạo mới, cập nhật, tìm kiếm mẫu hoặc làm việc với giao diện (UI/UX, Frontend, Web, Dashboard, Component, Figma, Design-to-Code), **LUÔN LUÔN** ưu tiên kho mặc định **`[2] React Shadcn Codex`** hoặc đề xuất người dùng chọn kết hợp trong **5 kho giao diện đã tải sẵn trên máy** tại `d:\UI`:

1. **`[1] shadcn/ui` & `Magic UI` (`d:\UI\components\shadcn-magicui\`)**
   - **Phù hợp khi:** Cần dựng giao diện ứng dụng thực tế (Dashboard, SaaS, Landing Page, hiệu ứng động Framer Motion, Dark/Light mode) bằng **React + Tailwind CSS v4 + Radix UI**.
2. **`[2] React Shadcn Codex` (`d:\UI\datasets\react-shadcn-codex\react_shadcn_codex.json`) — [CHUẨN MẶC ĐỊNH HỆ THỐNG]**
   - **Phù hợp khi:** Cần tra cứu nhanh hoặc lấy mẫu từ **3,181 component React** kết hợp sẵn `shadcn/ui`, `framer-motion` và `lucide-react` (~34 MB JSON).
3. **`[3] UIGEN-T2 & UIGEN-T3` (`d:\UI\datasets\uigen\`)**
   - **Phù hợp khi:** Cần tập dữ liệu SFT/Prompt-to-UI hiện đại (`UIGEN-T2.parquet` ~294 MB & `Hunter-Alpha-UIGEN-T3.jsonl` ~180 MB) để sinh giao diện Tailwind CSS / React / HTML từ mô tả.
4. **`[4] Design2Code Standard & HARD` (`d:\UI\datasets\design2code\`)**
   - **Phù hợp khi:** Cần các cặp **Screenshot `.png` ↔ `.html`/CSS** thực tế (484 trang Standard trong Parquet ~74 MB + 80 trang GitHub Pages độ khó cao giải nén sẵn tại `d:\UI\datasets\design2code\hard\`).
5. **`[5] ReDesign-Figma909` (`d:\UI\datasets\redesign-figma909\`)**
   - **Phù hợp khi:** Cần thiết kế phân tách **Layer chuẩn Figma** (`valid_frames/*.json`), ảnh giao diện tái tạo (`reconstructed_images/*.png`) và tọa độ Bounding Box (`*_bbox.png`).

## Lệnh Tra cứu 0-Token (Bắt buộc dùng CLI thay vì đọc trực tiếp file JSON 34 MB)
- Kiểm tra trạng thái kho: `python "d:\UI\ui_manager.py"`
- Xem danh mục loại component: `python "d:\UI\ui_manager.py" types`
- Tìm kiếm mẫu theo từ khóa: `python "d:\UI\ui_manager.py" search "<từ_khóa>" --limit 5`
- Lấy mã nguồn đầy đủ của 1 component: `python "d:\UI\ui_manager.py" get <ID>`
