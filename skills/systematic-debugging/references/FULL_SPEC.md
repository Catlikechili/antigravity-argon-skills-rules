---
name: systematic-debugging
description: >-
  Chẩn đoán lỗi hệ thống và phục hồi sự cố theo phương pháp tìm nguyên nhân gốc (Root-Cause Debugging).
  Sử dụng ngay khi gặp lỗi biên dịch, lỗi runtime, script thất bại hoặc kết quả sai lệch để sửa dứt điểm
  trong 1 lượt mà không thử-sai mù quáng.
---

# Gỡ lỗi Hệ thống & Tìm Nguyên nhân Gốc (Systematic Root-Cause Debugging)

## 1. Quy tắc Thép: Cấm Thử-Sai Mù Quáng (No Shotgun Debugging)
- **Tuyệt đối không** sửa mò liên tiếp nhiều lần khi chưa đọc thông báo lỗi chính xác và chưa hiểu tại sao lỗi xảy ra.
- Nếu một hướng sửa đã thất bại 2 lần liên tiếp, **DỪNG LẠI NGAY**, thu thập thêm thông tin trạng thái thực tế thay vì tiếp tục thử cách tương tự.

## 2. Quy trình 4 Bước Chẩn đoán Nhanh (Observe – Isolate – Fix – Verify)
1. **Đọc Tọa độ Lỗi Chính xác (Observe):** Trích xuất đúng dòng báo lỗi (`Error`, `Exception`, `Line X`) từ log hoặc terminal thay vì đọc toàn bộ log dài.
2. **Khoanh vùng Nguyên nhân Gốc (Isolate):** Kiểm tra dữ liệu đầu vào, kiểu dữ liệu, đường dẫn file hoặc phiên bản môi trường ngay tại điểm gãy.
3. **Sửa Tối thiểu tại Gốc (Root Fix):** Sửa đúng nguyên nhân gây lỗi gốc thay vì chỉ che giấu triệu chứng (như bọc `try/catch` rỗng).
4. **Kiểm chứng Lại (Verify):** Chạy lại lệnh/test ngay trong cùng lượt để xác nhận lỗi đã biến mất hoàn toàn.
