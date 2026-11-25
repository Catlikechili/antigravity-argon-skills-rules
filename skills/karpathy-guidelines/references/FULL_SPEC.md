---
name: karpathy-guidelines
description: >-
  Nguyên tắc lập trình và xử lý tác vụ của Andrej Karpathy: chống suy diễn mù quáng,
  không phức tạp hóa vấn đề (No Over-engineering), chỉ chỉnh sửa phẫu thuật đúng chỗ
  (Surgical Edits) và luôn giữ nguyên cấu trúc hiện có.
---

# Nguyên tắc Andrej Karpathy (Karpathy Guidelines for AI Agents)

Áp dụng bộ nguyên tắc này trong mọi tác vụ viết code, sửa tài liệu và xử lý dữ liệu để loại bỏ các lỗi kinh điển của LLM:

## 1. Không Phỏng đoán Mù quáng (Think Before Acting)
- **Không đoán mò yêu cầu mơ hồ:** Nếu yêu cầu có nhiều cách hiểu dẫn đến kết quả khác hẳn nhau, hãy nêu ngắn gọn các phương án và hỏi lại người dùng trước khi sửa hàng loạt.
- **Đọc trước khi sửa:** Luôn kiểm tra đoạn code/văn bản xung quanh để hiểu rõ quy ước đặt tên, định dạng và kiến trúc sẵn có.

## 2. Ưu tiên Sự Đơn giản Tối đa (Simplicity First – No Over-Engineering)
- **Chỉ làm đúng mức được yêu cầu:** Không tự ý thêm class, wrapper, interface, cấu hình dự phòng hoặc tính năng "phòng hờ tương lai" khi người dùng không yêu cầu.
- **Nếu 20 dòng giải quyết xong, tuyệt đối không viết 100 dòng.**

## 3. Phẫu thuật Chính xác (Surgical Changes Only)
- **Chỉ chạm vào đúng dòng cần sửa:** Tuyệt đối không tự ý định dạng lại (reformat), đổi tên biến, xóa comment hoặc viết lại các đoạn code/văn bản lân cận đang hoạt động bình thường.
- **Bảo toàn dữ liệu gốc:** Không lược bỏ hay rút gọn nội dung hiện có của người dùng bằng các dòng chú thích kiểu `// ... giữ nguyên phần còn lại ...`.

## 4. Thực thi Định hướng Mục tiêu (Goal-Driven Execution)
- Chuyển mọi yêu cầu thành tiêu chí kiểm chứng cụ thể (*Input -> Action -> Verification*).
- Tự dọn dẹp các biến thừa, hàm nháp hoặc file tạm do chính mình tạo ra trong phiên làm việc.
