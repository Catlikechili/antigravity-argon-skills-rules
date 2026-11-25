---
name: fullstack-clean-architecture
description: >-
  Chuẩn mực thiết kế phần mềm sạch, tối ưu hiệu năng và bảo mật đa ngôn ngữ
  (Python, JS/TS, C#, C++, Go, SQL, PowerShell). Sử dụng khi viết mới hoặc tối ưu mã nguồn,
  API, cơ sở dữ liệu và script tự động hóa.
---

# Kiến trúc Mã nguồn Sạch, Hiệu năng & Bảo mật (Fullstack Clean Architecture)

## 1. Cấu trúc Code Rõ ràng & Dễ Bảo trì (Clean & Modular Code)
- **Single Responsibility:** Mỗi hàm/module chỉ đảm nhận một nhiệm vụ rõ ràng, tên hàm và biến phản ánh đúng bản chất dữ liệu.
- **Early Return (Guard Clauses):** Xử lý các điều kiện biên và lỗi ngay đầu hàm để tránh lồng ghép `if/else` quá sâu.

## 2. Tối ưu Hiệu năng & Tài nguyên (Performance & Resource Safety)
- Tránh vòng lặp truy vấn lặp lại ($N+1$ queries) hoặc đọc toàn bộ file гигабайт vào RAM khi có thể đọc theo dòng/luồng (streaming/chunking).
- Luôn đóng kết nối file/mạng hoặc dùng cấu trúc tự giải phóng tài nguyên (`with` trong Python, `using` trong C#, `try/finally`).

## 3. An toàn & Bảo mật Mặc định (Security by Default)
- Không bao giờ hardcode mật khẩu, token hoặc API key trực tiếp vào mã nguồn; luôn sử dụng biến môi trường hoặc file cấu hình riêng.
- Kiểm tra và làm sạch đường dẫn, tham số đầu vào để chống lỗi tiêm lệnh (Command/SQL Injection) và lỗi ghi đè ngoài ý muốn.
