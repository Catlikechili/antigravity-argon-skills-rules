---
name: ui-ux-pro-max
description: Chỉ đọc khi thiết kế Web App, Dashboard, HTML Widget hoặc tra cứu CLI kho giao diện d:\UI (React Shadcn Codex).
---

# Thiết kế Giao diện & Kho UI Cục bộ `d:\UI` (UI/UX Pro Max)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

## 1. Tra cứu 0-Token từ 5 Kho Giao diện tại `d:\UI` (Mặc định: `[2] React Shadcn Codex`)
```powershell
python "d:\UI\ui_manager.py" types
python "d:\UI\ui_manager.py" search "<từ_khóa>" --limit 5
python "d:\UI\ui_manager.py" get <ID>
```
- **5 Kho sẵn có:** `[1] shadcn-magicui`, `[2] react-shadcn-codex` (3,181 components — Mặc định), `[3] uigen`, `[4] design2code`, `[5] redesign-figma909`.

## 2. Chuẩn Thị giác & Đồ thị Khoa học
- Bố cục CSS Grid/Flexbox rõ phân cấp KPI, chuẩn tương phản WCAG AA, đầy đủ trạng thái `hover/active/loading/empty`.
- Đồ thị (`matplotlib`/`PGFPlots`/Canvas): `300 DPI`, đủ nhãn trục + đơn vị đo, legend không đè dữ liệu.
