---
name: idle-free-model-runner
description: Chỉ kích hoạt khi cần chạy CLI idle_free_runner.py hoặc Ollama Qwen cục bộ để quét/tóm tắt hàng loạt file (Map-Reduce 0-Quota).
---

# Điều phối Model Miễn phí cho Tác vụ Rộng & Dễ (Free-Model Offloader)

> Chi tiết đầy đủ: `references/FULL_SPEC.md`.

## 1. Ba Kênh Thực Thi 0-Token / Chi Phí Cực Thấp
1. **CLI Đa luồng (`scripts/idle_free_runner.py`):**
   ```powershell
   # Phân loại tác vụ (Triage):
   python "C:\Users\CVLONG\.gemini\config\skills\idle-free-model-runner\scripts\idle_free_runner.py" --triage --target "<path>" --prompt "<yêu_cầu>" --json
   # Quét hàng loạt (Batch Map-Reduce):
   python "C:\Users\CVLONG\.gemini\config\skills\idle-free-model-runner\scripts\idle_free_runner.py" --batch-scan --target "<dir>" --glob "*.py" --max-files 10 --workers 4 --prompt "<yêu_cầu>"
   # Chạy đơn lẻ ngay:
   python "C:\Users\CVLONG\.gemini\config\skills\idle-free-model-runner\scripts\idle_free_runner.py" --run-now --target "<path>" --prompt "<yêu_cầu>"
   ```
2. **MCP Local Ollama:** Gọi `call_mcp_tool(ServerName="ast-context-optimizer", ToolName="ask_local_ollama_qwen", Arguments={"root": "...", "target": "...", "prompt": "..."})`.
3. **Subagent Hạng Nhẹ (Chỉ khi dữ liệu thô $>15.000$ tokens):** `invoke_subagent(TypeName="self", Model="flash_lite", Role="Batch Worker", Prompt="...")` — ép ghi kết quả ra ổ cứng và chỉ trả về $\le 15$ dòng.
