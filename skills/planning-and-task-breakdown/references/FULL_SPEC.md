---
name: planning-and-task-breakdown
description: >-
  Phân rã bài toán phức tạp và lập kế hoạch thực thi từng bước (Task Breakdown & Execution Planning).
  Sử dụng khi xây dựng tính năng mới, tái cấu trúc hệ thống, hoặc xử lý chuỗi công việc đa bước.
---

# Phân rã Bài toán & Lập Kế hoạch Thực thi (Planning & Task Breakdown)

## 1. Khi nào Kích hoạt Lập Kế hoạch?
- Kích hoạt khi tác vụ liên quan đến $\ge 3$ file, thay đổi kiến trúc/luồng dữ liệu, hoặc có nhiều bước phụ thuộc lẫn nhau.
- Với tác vụ nhỏ ($\le 2$ vị trí sửa rõ ràng), bỏ qua bước lập kế hoạch dài dòng và thực thi ngay để tiết kiệm thời gian.

## 2. Cấu trúc Bản Kế hoạch Siêu Gọn (Actionable Micro-Plan)
1. **Phân tích Phạm vi (Impact Scope):** Liệt kê chính xác các file sẽ đọc/sửa/tạo mới và những phần không được phép chạm tới.
2. **Thứ tự Thực thi Độc lập (Atomic Steps):**
   - Chia bài toán thành các bước nhỏ có thể kiểm chứng ngay sau khi chạy.
   - Ưu tiên gộp các bước không phụ thuộc nhau vào cùng một lượt (Batch).
3. **Điểm Kiểm soát Rủi ro (Rollback & Edge Cases):** Xác định trước các trường hợp biên (dữ liệu rỗng, lỗi đường dẫn, xung đột thư viện) trước khi viết code.
