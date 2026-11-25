---
name: rolling-summary-compactor
description: >-
  Rút gọn và nén cuốn chiếu các bản tóm tắt trước đó (Rolling Delta Summary & Context Pruning)
  nhằm loại bỏ ngữ cảnh dư thừa, giảm độ trễ suy luận (Fast-Thinking) và tiết kiệm tối đa token
  khi phiên làm việc kéo dài hoặc khi có nhiều bản tóm tắt/checkpoint nối tiếp nhau.
---

# Kỹ năng Rút gọn Tóm tắt Cuốn chiếu (Rolling Summary Compactor)

Giải quyết triệt để hiện tượng *Summary Bloat* (các bản tóm tắt cũ chồng chất làm loãng cơ chế Self-Attention và tốn token lặp lại qua mỗi bước).

## 1. Quy trình 4 Bước Nén Cuốn Chiếu (Prune – Freeze – Overwrite – Focus)
Khi cập nhật tiến độ hoặc tạo Checkpoint/Artifact, **CẤM chép nối tiếp (append)** vào sau lịch sử cũ:
1. **Cắt tỉa Ngữ cảnh Chết (Dead-Path Pruning):** Xóa bỏ hoàn toàn các lỗi đã sửa xong, phương án nháp đã bỏ, log trung gian và lý giải dài dòng của các bước trước.
2. **Đóng băng Tầng Hoàn tất (1-Line Freezing):** Gom toàn bộ các bước đã xong thành 1 dòng trạng thái theo cú pháp: `[DONE] file:Lstart-Lend -> Kết quả chốt + Thông số kiểm chứng`.
3. **Ghi đè Cuốn chiếu (Rolling Overwrite):** Hợp nhất trạng thái mới trực tiếp vào khung duy nhất (tổng độ dài toàn khối **không quá 6–10 dòng** dù phiên dài 200 bước).
4. **Con trỏ Tác vụ Kế tiếp (Zero-Latency Next Pointer):** Chỉ rõ ngay tọa độ `file:StartLine-EndLine` cần thao tác ở lượt kế tiếp để không phải dò lại từ đầu.

## 2. Khung Mẫu Chuẩn `⚡ COMPACT STATE`
Sử dụng đúng 4 trường siêu cô đọng sau khi kết thúc mốc công việc lớn hoặc trước khi gợi ý `/compact`:

```markdown
### ⚡ COMPACT STATE (Rolling Snapshot)
- **[GOAL]:** <1 câu <=15 từ nêu mục tiêu gốc & ràng buộc bất biến>
- **[DONE]:** <Gộp các phần đã xong: `file:line -> kết quả`; ngăn cách bởi `;`>
- **[WIP]:** <Phần đang xử lý + biến số/vấn đề duy nhất còn tồn đọng>
- **[NEXT]:** <Hành động cụ thể tiếp theo + tọa độ `file:StartLine-EndLine`>
```

## 3. Áp dụng cho Artifact & `/compact`
- Trong `task.md` / `walkthrough.md`: khi một nhóm việc đã hoàn tất (`[x]`), thu gọn các mục con thành 1 dòng kết quả duy nhất.
- Khi phiên làm việc vượt 40–45 bước, xuất khối `⚡ COMPACT STATE` làm mỏ neo bộ nhớ và nhắc người dùng gõ `/compact`.
