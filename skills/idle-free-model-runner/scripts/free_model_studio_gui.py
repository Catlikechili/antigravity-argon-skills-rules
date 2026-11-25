#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Antigravity Broad-Scope Free-Model Token Offloader Studio GUI (free_model_studio_gui.py)
========================================================================================
Chương trình giao diện đồ họa tương tác (Desktop App Window / Local Web Studio tại http://127.0.0.1:8788)
giúp người dùng thao tác trực quan:
  1. Chọn File / Thư mục bằng hộp thoại Windows Explorer gốc hoặc cây thư mục nhanh.
  2. Chấm điểm tự động Phạm vi & Độ khó (Scope & Complexity Triage) kèm biểu đồ tiết kiệm Token.
  3. Chạy Quét Rộng Đa Luồng (Batch Map-Reduce) hoặc Chạy Đơn Lẻ trên các Model Miễn Phí
     (Local Ollama Qwen 7B / DeepSeek, OpenRouter :free, Gemini Free, Groq Free, AST 0-Token Engine).
  4. Xem trước bộ khung AST Skeleton [Lstart-Lend], quản lý lịch sử báo cáo và Copy 1-chạm.
"""

import argparse
import datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from typing import Any

# Đảm bảo UTF-8 an toàn trên Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = Path(r"d:\Gravity")

for p in (
    SCRIPT_DIR,
    WORKSPACE_ROOT / ".agents" / "skills" / "idle-free-model-runner" / "scripts",
    WORKSPACE_ROOT / ".agents" / "skills" / "context-engineering-search-first" / "scripts",
    WORKSPACE_ROOT / "03_Tham_Khao" / "04_AI_Tools_Configs" / "tools",
    Path.home() / ".gemini" / "config" / "scripts",
):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from idle_free_runner import (
    HAS_CTX_OPTIMIZER,
    OUTPUT_DIR,
    build_ast_compressed_prompt,
    check_ollama_status,
    detect_cloud_free_providers,
    execute_on_best_free_model,
    resolve_target_files,
    run_broad_batch_scan,
    save_single_task_output,
    select_best_local_model,
    triage_task_scope_and_complexity,
    try_start_ollama_service,
)

# Danh sách thư mục gợi ý nhanh trong Workspace d:\Gravity
QUICK_TARGETS = [
    {
        "label": "🔬 30 Bài Lab C11 STM32 Nâng Cao (Lab06 -> Lab35)",
        "path": "01_Hoc_Tap/Embedded_Offline_Academy/07_STM32_Mastery_Lab_Va_Mo_Phong/Bai_Tap_C_Thuc_Chien_Nang_Cao",
        "glob": "Lab*.c",
    },
    {
        "label": "📘 56 Bài Giảng STM32 Mastery (Jupyter / HTML)",
        "path": "01_Hoc_Tap/Embedded_Offline_Academy/07_STM32_Mastery_Lab_Va_Mo_Phong/Bai_Giang_Jupyter",
        "glob": "*.py",
    },
    {
        "label": "🛰️ Dự Án Vũ Trụ PCDU ↔ PMU STM32H753 HIL Sim",
        "path": "02_Nghien_Cuu/02_Code_Projects/PCDU_PMU_HIL_Sim",
        "glob": "*",
    },
    {
        "label": "⚡ Phòng Lab Điện Tử Công Suất & Điều Khiển Lưới",
        "path": "02_Nghien_Cuu/02_Code_Projects/Power_Electronics_And_Grid_Control_SimLab",
        "glob": "*",
    },
    {
        "label": "📈 Trạm Định Lượng Cổ Phiếu VN30 AI Predictor",
        "path": "02_Nghien_Cuu/02_Code_Projects/VN30_AI_Predictor",
        "glob": "*.py",
    },
    {
        "label": "🤖 Học Viện Robot Vision Academy",
        "path": "01_Hoc_Tap/Robot_Vision_Academy",
        "glob": "*.py",
    },
    {
        "label": "📡 Hệ Thống GitHub AI Radar & Summaries",
        "path": "03_Tham_Khao/02_GitHub_AI_Radar",
        "glob": "*.md",
    },
    {
        "label": "🛠️ Bộ Công Cụ AI Agent & Harvester Configs",
        "path": "03_Tham_Khao/04_AI_Tools_Configs",
        "glob": "*.py",
    },
]


def open_native_windows_picker(mode: str = "folder") -> str:
    """Mở hộp thoại chọn File hoặc Thư mục gốc của Windows (tkinter)."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        initial_dir = str(WORKSPACE_ROOT) if WORKSPACE_ROOT.exists() else str(Path.home())
        if mode == "file":
            chosen = filedialog.askopenfilename(
                title="Chọn File Mục Tiêu Cần Xử Lý Bằng Model Miễn Phí",
                initialdir=initial_dir,
            )
        else:
            chosen = filedialog.askdirectory(
                title="Chọn Thư Mục Phạm Vi Rộng Cần Quét Bằng Model Miễn Phí",
                initialdir=initial_dir,
            )
        root.destroy()
        if not chosen:
            return ""
        chosen_path = Path(chosen).resolve()
        if chosen_path.is_relative_to(WORKSPACE_ROOT):
            return str(chosen_path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")
        return str(chosen_path).replace("\\", "/")
    except Exception:
        return ""


def list_history_reports(limit: int = 30) -> list[dict[str, Any]]:
    """Lấy danh sách các báo cáo đã chạy trong idle_free_outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(OUTPUT_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    items = []
    for f in files:
        st = f.stat()
        items.append({
            "filename": f.name,
            "path": str(f),
            "size_kb": round(st.st_size / 1024.0, 1),
            "modified": dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return items


STUDIO_GUI_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>⚡ Trung Tâm Điều Phối Model Miễn Phí — Tác Vụ Phạm Vi Rộng & Mức Độ Dễ</title>
  <style>
    :root {
      --bg-main: #090d16;
      --bg-panel: #111827;
      --bg-card: #1e293b;
      --bg-card-hover: #26354d;
      --bg-input: #0b1120;
      --text-main: #f8fafc;
      --text-sub: #cbd5e1;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.2);
      --emerald: #10b981;
      --amber: #f59e0b;
      --rose: #f43f5e;
      --violet: #a855f7;
      --border: #334155;
      --radius: 10px;
    }
    body.light-mode {
      --bg-main: #f1f5f9;
      --bg-panel: #ffffff;
      --bg-card: #f8fafc;
      --bg-card-hover: #e2e8f0;
      --bg-input: #ffffff;
      --text-main: #0f172a;
      --text-sub: #334155;
      --text-muted: #64748b;
      --accent: #0284c7;
      --accent-glow: rgba(2, 132, 199, 0.15);
      --border: #cbd5e1;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', Inter, system-ui, -apple-system, sans-serif;
      background: var(--bg-main);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    /* HEADER */
    header {
      background: var(--bg-panel);
      border-bottom: 1px solid var(--border);
      padding: 10px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-shrink: 0;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-icon {
      width: 36px; height: 36px;
      border-radius: 9px;
      background: linear-gradient(135deg, #0ea5e9, #10b981);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.2rem; font-weight: bold; color: #fff;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    .brand-title { font-size: 1.02rem; font-weight: 800; letter-spacing: -0.2px; }
    .brand-sub { font-size: 0.75rem; color: var(--text-muted); }
    .header-controls {
      display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    }
    .pill {
      padding: 5px 11px;
      border-radius: 999px;
      font-size: 0.76rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--border);
      background: var(--bg-card);
    }
    .pill.ok {
      background: rgba(16, 185, 129, 0.14);
      color: var(--emerald);
      border-color: rgba(16, 185, 129, 0.4);
    }
    .pill.warn {
      background: rgba(245, 158, 11, 0.14);
      color: var(--amber);
      border-color: rgba(245, 158, 11, 0.4);
    }
    .pill.savings {
      background: rgba(168, 85, 247, 0.15);
      color: #c084fc;
      border-color: rgba(168, 85, 247, 0.4);
    }
    /* LAYOUT 3 COLUMNS */
    .workspace {
      flex: 1;
      display: grid;
      grid-template-columns: 330px 440px 1fr;
      overflow: hidden;
    }
    .col {
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--border);
      overflow: hidden;
      background: var(--bg-panel);
    }
    .col:last-child { border-right: none; background: var(--bg-main); }
    .col-header {
      padding: 11px 14px;
      border-bottom: 1px solid var(--border);
      font-size: 0.82rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--accent);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(255, 255, 255, 0.015);
    }
    .col-body {
      padding: 14px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    /* FORM ELEMENTS */
    label {
      display: block;
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--text-sub);
      margin-bottom: 5px;
    }
    input[type="text"], input[type="number"], select, textarea {
      width: 100%;
      background: var(--bg-input);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 8px 10px;
      border-radius: 7px;
      font-size: 0.84rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s;
    }
    input:focus, select:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent-glow);
    }
    textarea { resize: vertical; min-height: 92px; line-height: 1.45; }
    .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .row-3 { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 8px; }
    /* BUTTONS */
    .btn {
      cursor: pointer;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: var(--text-main);
      padding: 8px 12px;
      border-radius: 7px;
      font-size: 0.81rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.15s;
    }
    .btn:hover { background: var(--bg-card-hover); border-color: var(--accent); }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-primary {
      background: linear-gradient(135deg, #0284c7, #0ea5e9);
      color: #fff;
      border: none;
      padding: 10px 14px;
      font-size: 0.86rem;
      box-shadow: 0 3px 10px rgba(14, 165, 233, 0.3);
    }
    .btn-primary:hover { filter: brightness(1.08); }
    .btn-emerald {
      background: linear-gradient(135deg, #059669, #10b981);
      color: #fff;
      border: none;
      padding: 10px 14px;
      font-size: 0.86rem;
      box-shadow: 0 3px 10px rgba(16, 185, 129, 0.3);
    }
    .btn-emerald:hover { filter: brightness(1.08); }
    /* QUICK TARGET CARDS */
    .quick-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .quick-item {
      padding: 8px 10px;
      border-radius: 7px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      cursor: pointer;
      transition: all 0.14s;
      text-align: left;
    }
    .quick-item:hover, .quick-item.active {
      border-color: var(--accent);
      background: var(--bg-card-hover);
    }
    .quick-item-title { font-size: 0.8rem; font-weight: 700; color: var(--text-main); }
    .quick-item-path { font-size: 0.71rem; color: var(--text-muted); font-family: Consolas, monospace; margin-top: 2px; word-break: break-all; }
    /* PRESET CHIPS */
    .preset-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }
    .preset-btn {
      padding: 7px 9px;
      border-radius: 7px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-sub);
      font-size: 0.76rem;
      font-weight: 600;
      text-align: left;
      cursor: pointer;
      transition: all 0.14s;
    }
    .preset-btn:hover {
      border-color: var(--accent);
      color: var(--text-main);
      background: var(--bg-card-hover);
    }
    /* TRIAGE CARD */
    .triage-box {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .triage-route {
      font-size: 0.86rem;
      font-weight: 800;
      color: var(--emerald);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .progress-bar-wrap {
      background: var(--bg-input);
      border-radius: 999px;
      height: 10px;
      overflow: hidden;
      border: 1px solid var(--border);
    }
    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #10b981, #38bdf8);
      width: 92%;
      transition: width 0.3s ease;
    }
    /* RIGHT COLUMN TABS & CONTENT */
    .tabs {
      display: flex;
      border-bottom: 1px solid var(--border);
      background: var(--bg-panel);
      padding: 0 14px;
      gap: 6px;
    }
    .tab-btn {
      padding: 11px 14px;
      background: transparent;
      border: none;
      border-bottom: 3px solid transparent;
      color: var(--text-muted);
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
    }
    .tab-btn.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
    }
    .tab-pane {
      display: none;
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      flex-direction: column;
      gap: 14px;
    }
    .tab-pane.active { display: flex; }
    .output-viewer {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 16px;
      font-family: 'Cascadia Code', Consolas, monospace;
      font-size: 0.83rem;
      line-height: 1.55;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--text-main);
      flex: 1;
      min-height: 280px;
    }
    table.stats-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8rem;
      background: var(--bg-panel);
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--border);
    }
    table.stats-table th, table.stats-table td {
      padding: 8px 10px;
      border-bottom: 1px solid var(--border);
      text-align: left;
    }
    table.stats-table th {
      background: var(--bg-card);
      color: var(--accent);
      font-weight: 700;
    }
    .status-toast {
      font-size: 0.78rem;
      color: var(--emerald);
      font-weight: 700;
    }
  </style>
</head>
<body>
  <!-- HEADER -->
  <header>
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div>
        <div class="brand-title">ANTIGRAVITY FREE-MODEL TOKEN OFFLOADER STUDIO</div>
        <div class="brand-sub">Điều phối Model Miễn Phí & Nén AST cho Tác Vụ Phạm Vi Rộng – Mức Độ Dễ (Tiết kiệm 85–95% Token)</div>
      </div>
    </div>
    <div class="header-controls">
      <span id="ollamaBadge" class="pill warn">⏳ Đang kiểm tra Ollama...</span>
      <button class="btn" onclick="bootOllama()" title="Khởi động dịch vụ Local Ollama">🚀 Bật Ollama</button>
      <span id="totalSavedBadge" class="pill savings">💎 Đã tiết kiệm: 0 Tokens</span>
      <button class="btn" onclick="toggleTheme()">🌗 Giao diện</button>
    </div>
  </header>

  <!-- MAIN 3-COLUMN WORKSPACE -->
  <div class="workspace">
    <!-- COLUMN 1: TARGET & FILE SCOPE -->
    <div class="col">
      <div class="col-header">
        <span>1. Chọn Phạm Vi File / Thư Mục</span>
        <span id="matchedFilesBadge" style="font-size:0.74rem;color:var(--emerald)">0 files</span>
      </div>
      <div class="col-body">
        <div class="row-2">
          <button class="btn" onclick="pickNative('folder')">📂 Chọn Thư Mục...</button>
          <button class="btn" onclick="pickNative('file')">📄 Chọn 1 File...</button>
        </div>

        <div>
          <label>Đường dẫn Mục tiêu (`Target` tương đối hoặc tuyệt đối):</label>
          <input type="text" id="targetInput" value="01_Hoc_Tap/Embedded_Offline_Academy/07_STM32_Mastery_Lab_Va_Mo_Phong/Bai_Tap_C_Thuc_Chien_Nang_Cao" oninput="autoTriageDebounced()" />
        </div>

        <div class="row-3">
          <div>
            <label>Bộ lọc `Glob`:</label>
            <input type="text" id="globInput" value="Lab2*.c" oninput="autoTriageDebounced()" />
          </div>
          <div>
            <label>Số file tối đa:</label>
            <input type="number" id="maxFilesInput" value="6" min="1" max="100" onchange="autoTriageDebounced()" />
          </div>
          <div>
            <label>Luồng (`Workers`):</label>
            <input type="number" id="workersInput" value="4" min="1" max="8" />
          </div>
        </div>

        <div>
          <label>Khoảng dòng cắt phẫu thuật (Tùy chọn cho 1 file, VD: `1-90`):</label>
          <input type="text" id="linesInput" placeholder="Để trống nếu quét toàn bộ AST..." />
        </div>

        <div>
          <label>📌 Danh Mục Nhanh Trong Workspace (`d:\Gravity`):</label>
          <div id="quickTargetsList" class="quick-list"></div>
        </div>
      </div>
    </div>

    <!-- COLUMN 2: MODEL SELECTION, PROMPT PRESETS & LIVE TRIAGE -->
    <div class="col">
      <div class="col-header">
        <span>2. Cấu Hình Model Miễn Phí & Tác Vụ</span>
        <button class="btn" style="padding:3px 8px;font-size:0.72rem" onclick="runTriage()">🔍 Chấm Triage</button>
      </div>
      <div class="col-body">
        <div class="row-2">
          <div>
            <label>Nguồn Model Miễn Phí (`Provider`):</label>
            <select id="providerSelect" onchange="onProviderChange()">
              <option value="auto">🤖 Tự động tối ưu (Auto)</option>
              <option value="ollama">💻 Local Ollama (Offline Free)</option>
              <option value="openrouter-free">🌐 OpenRouter (:free Models)</option>
              <option value="gemini-free">✨ Gemini Free Tier</option>
              <option value="groq-free">⚡ Groq Free Tier</option>
            </select>
          </div>
          <div>
            <label>Tên Model cụ thể (Tùy chọn):</label>
            <input type="text" id="modelInput" placeholder="qwen7b-antigravity" />
          </div>
        </div>

        <div>
          <label>⚡ 8 Mẫu Tác Vụ Phạm Vi Rộng – Mức Độ Dễ (1-Click Presets):</label>
          <div class="preset-grid">
            <button class="preset-btn" onclick="setPreset('Tóm tắt chức năng & các hàm chính', 'Liệt kê mục tiêu của file, ngoại vi/thư viện sử dụng và danh sách các hàm chính kèm tọa độ dòng [Lstart-Lend].')">📋 1. Tóm tắt Đa File (Map-Reduce)</button>
            <button class="preset-btn" onclick="setPreset('Trích xuất Bản đồ AST & Struct', 'Trích xuất toàn bộ struct, class, hằng số #define quan trọng và chữ ký hàm kèm tọa độ dòng.')">🧬 2. Bản đồ AST & Struct</button>
            <button class="preset-btn" onclick="setPreset('Viết Docstring & Comment chuẩn', 'Sinh bộ Docstring và giải thích ngắn gọn tham số đầu vào/đầu ra cho các hàm chính trong file.')">📝 3. Viết Docstring / Comment</button>
            <button class="preset-btn" onclick="setPreset('Dịch thuật & Biên tập Tiếng Việt', 'Dịch và tóm tắt nội dung kỹ thuật cốt lõi sang tiếng Việt chuyên ngành rõ ràng, cô đọng.')">🌐 4. Dịch & Tóm tắt Tiếng Việt</button>
            <button class="preset-btn" onclick="setPreset('Quét TODO, Magic Numbers & Naming', 'Kiểm tra các điểm TODO/FIXME, hằng số cứng (magic numbers) và nhận xét quy ước đặt tên hàm/biến.')">🔍 5. Quét Quy Ước & TODO</button>
            <button class="preset-btn" onclick="setPreset('Tạo Câu hỏi Quiz Ôn tập', 'Tạo 3 câu hỏi trắc nghiệm kiểm tra hiểu biết sâu về cơ chế hoạt động của đoạn code/tài liệu này kèm đáp án.')">🎓 6. Tạo Câu Hỏi Trắc Nghiệm</button>
            <button class="preset-btn" onclick="setPreset('Kiểm tra Bề mặt An toàn Bộ nhớ', 'Kiểm tra nhanh các vị trí dùng con trỏ, mảng tĩnh, ép kiểu hoặc tràn bộ đệm tiềm ẩn kèm tọa độ dòng.')">🛡️ 7. Quét Bề Mặt Bộ Nhớ</button>
            <button class="preset-btn" onclick="setPreset('Lập Chỉ mục Danh mục (Catalog)', 'Tạo bảng danh mục Markdown gồm: Tên File, Chức năng chính, Độ phức tạp và Tọa độ hàm entry-point.')">📊 8. Lập Danh Mục Catalog</button>
          </div>
        </div>

        <div>
          <label>Yêu cầu xử lý gửi tới Model Miễn Phí (`Prompt`):</label>
          <textarea id="promptInput" oninput="autoTriageDebounced()">Liệt kê mục tiêu của file, ngoại vi/thư viện sử dụng và danh sách các hàm chính kèm tọa độ dòng [Lstart-Lend].</textarea>
        </div>

        <!-- LIVE TRIAGE GAUGE -->
        <div class="triage-box">
          <div class="triage-route">
            <span id="triageRouteText">⚡ FREE_MODEL_DIRECT_BATCH</span>
            <span id="triageSavingsBadge" class="pill ok" style="font-size:0.72rem">-92% Token chính</span>
          </div>
          <div style="font-size:0.76rem;color:var(--text-sub)" id="triageDescText">
            Đang phân tích phạm vi file và độ khó tác vụ...
          </div>
          <div class="progress-bar-wrap">
            <div id="triageBar" class="progress-bar-fill" style="width:92%"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:var(--text-muted)">
            <span id="triageRawTokens">Raw: 0 tokens</span>
            <span id="triageAstTokens">Sau nén AST: 0 tokens</span>
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div style="display:flex;flex-direction:column;gap:8px;margin-top:auto">
          <button id="btnBatchScan" class="btn btn-emerald" onclick="runBatchScan()">
            🚀 CHẠY QUÉT RỘNG ĐA FILE (BATCH MAP-REDUCE)
          </button>
          <div class="row-2">
            <button id="btnRunSingle" class="btn btn-primary" onclick="runSingleNow()">
              ⚡ Chạy 1 Mục Tiêu (`--run-now`)
            </button>
            <button class="btn" onclick="previewAstSkeleton()">
              🧬 Xem Nén AST (0-Token)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- COLUMN 3: RESULTS, TOKEN TABLE & HISTORY -->
    <div class="col">
      <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('tabResult', this)">📊 Kết Quả & Bảng Tiết Kiệm Token</button>
        <button class="tab-btn" onclick="switchTab('tabAst', this)">🧬 Bộ Khung AST Skeleton (`[Lstart-Lend]`)</button>
        <button class="tab-btn" onclick="switchTab('tabHistory', this); loadHistory();">🗂️ Lịch Sử Báo Cáo Đã Xuất</button>
      </div>

      <!-- TAB 1: RESULT -->
      <div id="tabResult" class="tab-pane active">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap">
          <span id="runStatusText" class="status-toast">Sẵn sàng điều phối tác vụ phạm vi rộng trên Model Miễn Phí.</span>
          <div style="display:flex;gap:6px">
            <button class="btn" onclick="copyOutput()">📋 Copy Kết Quả</button>
            <button class="btn" onclick="copyForMainAgent()">🤖 Copy Gói Gọn Cho Agent Chính</button>
            <button class="btn" onclick="openOutputFolder()">📂 Mở Thư Mục Báo Cáo</button>
          </div>
        </div>

        <div id="batchTableContainer" style="display:none">
          <table class="stats-table">
            <thead>
              <tr>
                <th>#</th>
                <th>File Mục Tiêu</th>
                <th>Token Gốc (Raw)</th>
                <th>Sau Nén AST</th>
                <th>Tiết Kiệm</th>
              </tr>
            </thead>
            <tbody id="batchTableBody"></tbody>
          </table>
        </div>

        <div id="mainOutputViewer" class="output-viewer">Chọn thư mục/file ở Cột 1, chọn mẫu tác vụ ở Cột 2 và nhấn [🚀 CHẠY QUÉT RỘNG ĐA FILE] hoặc [⚡ Chạy 1 Mục Tiêu].</div>
      </div>

      <!-- TAB 2: AST PREVIEW -->
      <div id="tabAst" class="tab-pane">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span id="astMetaText" class="status-toast">Bộ khung AST Skeleton giúp giảm 85–95% Token trước khi đưa vào Model.</span>
          <button class="btn" onclick="copyAstPreview()">📋 Copy AST Skeleton</button>
        </div>
        <div id="astOutputViewer" class="output-viewer">Nhấn nút [🧬 Xem Nén AST (0-Token)] để trích xuất tức thì bộ khung hàm/class kèm tọa độ dòng [Lstart-Lend].</div>
      </div>

      <!-- TAB 3: HISTORY -->
      <div id="tabHistory" class="tab-pane">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="status-toast">Danh sách các báo cáo Digest đã lưu trong `idle_free_outputs\`:</span>
          <button class="btn" onclick="loadHistory()">🔄 Làm mới</button>
        </div>
        <div id="historyList" class="quick-list"></div>
      </div>
    </div>
  </div>

  <script>
    let totalSavedTokensSession = 0;
    let triageTimer = null;

    async function apiPost(path, payload) {
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload || {})
      });
      return await res.json();
    }

    function toggleTheme() {
      document.body.classList.toggle('light-mode');
    }

    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).classList.add('active');
      if (btn) btn.classList.add('active');
    }

    function setPreset(title, promptText) {
      document.getElementById('promptInput').value = promptText;
      runTriage();
    }

    function autoTriageDebounced() {
      clearTimeout(triageTimer);
      triageTimer = setTimeout(runTriage, 250);
    }

    async function loadStatus() {
      const data = await apiPost('/api/status', {});
      const badge = document.getElementById('ollamaBadge');
      if (data.ollama_online) {
        badge.className = 'pill ok';
        badge.textContent = `🟢 Ollama ONLINE (${data.best_local_model})`;
      } else {
        badge.className = 'pill warn';
        badge.textContent = `⚡ Chế độ AST 0-Token (Ollama đang tắt)`;
      }
      const qList = document.getElementById('quickTargetsList');
      qList.innerHTML = '';
      (data.quick_targets || []).forEach(item => {
        const div = document.createElement('div');
        div.className = 'quick-item';
        div.innerHTML = `<div class="quick-item-title">${item.label}</div><div class="quick-item-path">${item.path} (${item.glob})</div>`;
        div.onclick = () => {
          document.getElementById('targetInput').value = item.path;
          document.getElementById('globInput').value = item.glob;
          runTriage();
        };
        qList.appendChild(div);
      });
    }

    async function bootOllama() {
      document.getElementById('ollamaBadge').textContent = '⏳ Đang bật Ollama...';
      await apiPost('/api/boot-ollama', {});
      await loadStatus();
    }

    async function pickNative(mode) {
      const res = await apiPost('/api/pick-path', { mode });
      if (res.chosen) {
        document.getElementById('targetInput').value = res.chosen;
        if (mode === 'file') {
          document.getElementById('globInput').value = '*';
        }
        runTriage();
      }
    }

    async function runTriage() {
      const payload = {
        target: document.getElementById('targetInput').value.trim(),
        glob: document.getElementById('globInput').value.trim() || '*',
        max_files: parseInt(document.getElementById('maxFilesInput').value || '10', 10),
        prompt: document.getElementById('promptInput').value.trim()
      };
      const res = await apiPost('/api/triage', payload);
      document.getElementById('matchedFilesBadge').textContent = `${res.file_count} files khớp`;
      document.getElementById('triageRouteText').textContent = `⚡ ${res.route} (${res.scope} / ${res.complexity})`;
      document.getElementById('triageSavingsBadge').textContent = `Tiết kiệm ~${res.estimated_main_token_savings_pct}% Token`;
      document.getElementById('triageDescText').textContent = res.recommendation;
      document.getElementById('triageBar').style.width = `${Math.min(100, Math.max(15, res.estimated_main_token_savings_pct))}%`;
      document.getElementById('triageRawTokens').textContent = `Raw: ${(res.estimated_raw_tokens || 0).toLocaleString()} tokens`;
      document.getElementById('triageAstTokens').textContent = `Sau nén AST: ~${(res.estimated_ast_compressed_tokens || 0).toLocaleString()} tokens`;
    }

    async function runBatchScan() {
      const btn = document.getElementById('btnBatchScan');
      btn.disabled = true;
      btn.textContent = '⏳ ĐANG QUÉT RỘNG ĐA LUỒNG TRÊN MODEL MIỄN PHÍ...';
      document.getElementById('runStatusText').textContent = '⏳ Đang nén AST và chạy Map-Reduce song song...';
      try {
        const payload = {
          target: document.getElementById('targetInput').value.trim(),
          glob: document.getElementById('globInput').value.trim() || '*',
          max_files: parseInt(document.getElementById('maxFilesInput').value || '8', 10),
          workers: parseInt(document.getElementById('workersInput').value || '4', 10),
          provider: document.getElementById('providerSelect').value,
          model: document.getElementById('modelInput').value.trim(),
          prompt: document.getElementById('promptInput').value.trim()
        };
        const res = await apiPost('/api/batch-scan', payload);
        if (!res.ok) {
          document.getElementById('mainOutputViewer').textContent = `[LỖI] ${res.error || 'Không tìm thấy file phù hợp.'}`;
          return;
        }
        const savedNow = Math.max(0, (res.total_raw_tokens || 0) - (res.total_compressed_tokens || 0));
        totalSavedTokensSession += savedNow;
        document.getElementById('totalSavedBadge').textContent = `💎 Đã tiết kiệm: ${totalSavedTokensSession.toLocaleString()} Tokens`;

        document.getElementById('runStatusText').textContent =
          `✅ Hoàn tất ${res.files_processed} files trong ${res.elapsed_seconds}s | Giảm từ ${(res.total_raw_tokens||0).toLocaleString()} -> ${(res.total_compressed_tokens||0).toLocaleString()} tokens (-${res.overall_token_savings_pct}%)`;

        const tbody = document.getElementById('batchTableBody');
        tbody.innerHTML = '';
        (res.items || []).forEach((it, idx) => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${idx + 1}</td>
            <td style="font-family:Consolas,monospace">${it.file.split('/').pop()}</td>
            <td>${(it.raw_tokens || 0).toLocaleString()}</td>
            <td>${(it.compressed_tokens || 0).toLocaleString()}</td>
            <td style="color:var(--emerald);font-weight:700">-${it.savings_pct}%</td>
          `;
          tbody.appendChild(tr);
        });
        document.getElementById('batchTableContainer').style.display = 'block';
        document.getElementById('mainOutputViewer').textContent = res.digest_markdown || '';
      } finally {
        btn.disabled = false;
        btn.textContent = '🚀 CHẠY QUÉT RỘNG ĐA FILE (BATCH MAP-REDUCE)';
      }
    }

    async function runSingleNow() {
      const btn = document.getElementById('btnRunSingle');
      btn.disabled = true;
      btn.textContent = '⏳ Đang xử lý...';
      document.getElementById('runStatusText').textContent = '⏳ Đang gửi yêu cầu tới Model Miễn Phí...';
      try {
        const payload = {
          target: document.getElementById('targetInput').value.trim(),
          lines: document.getElementById('linesInput').value.trim(),
          provider: document.getElementById('providerSelect').value,
          model: document.getElementById('modelInput').value.trim(),
          prompt: document.getElementById('promptInput').value.trim()
        };
        const res = await apiPost('/api/run-single', payload);
        const ast = res.ast_compression || {};
        const savedNow = Math.max(0, (ast.raw_tokens || 0) - (ast.compressed_tokens || 0));
        totalSavedTokensSession += savedNow;
        document.getElementById('totalSavedBadge').textContent = `💎 Đã tiết kiệm: ${totalSavedTokensSession.toLocaleString()} Tokens`;
        document.getElementById('batchTableContainer').style.display = 'none';
        document.getElementById('runStatusText').textContent =
          `✅ Model (${res.provider}:${res.model}) xử lý xong trong ${res.elapsed_seconds}s | Tiết kiệm ${ast.savings_pct || 0}% Token`;
        document.getElementById('mainOutputViewer').textContent = res.response_text || '';
      } finally {
        btn.disabled = false;
        btn.textContent = '⚡ Chạy 1 Mục Tiêu (--run-now)';
      }
    }

    async function previewAstSkeleton() {
      const payload = {
        target: document.getElementById('targetInput').value.trim(),
        lines: document.getElementById('linesInput').value.trim(),
        prompt: document.getElementById('promptInput').value.trim()
      };
      const res = await apiPost('/api/preview-ast', payload);
      const m = res.meta || {};
      document.getElementById('astMetaText').textContent =
        `🧬 Nén AST: ${(m.raw_tokens||0).toLocaleString()} tokens gốc -> ${(m.compressed_tokens||0).toLocaleString()} tokens (Tiết kiệm ${m.savings_pct || 0}%)`;
      document.getElementById('astOutputViewer').textContent = res.full_prompt || '';
      switchTab('tabAst', document.querySelectorAll('.tab-btn')[1]);
    }

    async function loadHistory() {
      const res = await apiPost('/api/history', {});
      const list = document.getElementById('historyList');
      list.innerHTML = '';
      (res.reports || []).forEach(r => {
        const div = document.createElement('div');
        div.className = 'quick-item';
        div.innerHTML = `
          <div class="quick-item-title">📄 ${r.filename}</div>
          <div class="quick-item-path">🕒 ${r.modified} | Dung lượng: ${r.size_kb} KB</div>
        `;
        div.onclick = async () => {
          const detail = await apiPost('/api/read-report', { filename: r.filename });
          document.getElementById('batchTableContainer').style.display = 'none';
          document.getElementById('runStatusText').textContent = `📂 Đang xem báo cáo: ${r.filename}`;
          document.getElementById('mainOutputViewer').textContent = detail.content || '';
          switchTab('tabResult', document.querySelectorAll('.tab-btn')[0]);
        };
        list.appendChild(div);
      });
    }

    function copyOutput() {
      const txt = document.getElementById('mainOutputViewer').textContent;
      navigator.clipboard.writeText(txt);
      document.getElementById('runStatusText').textContent = '✅ Đã copy toàn bộ nội dung báo cáo vào Clipboard!';
    }

    function copyForMainAgent() {
      const txt = document.getElementById('mainOutputViewer').textContent;
      const wrapped = `[BẢN TÓM TẮT ĐÃ LỌC QUA MODEL MIỄN PHÍ & NÉN AST]:\n${txt}\n\n---\nHãy dựa trên bản tóm tắt tọa độ trên để xử lý bước tiếp theo mà không cần đọc lại toàn bộ file thô.`;
      navigator.clipboard.writeText(wrapped);
      document.getElementById('runStatusText').textContent = '🤖 Đã copy gói Prompt tinh gọn (Map-Reduce) để dán vào khung chat Agent chính!';
    }

    function copyAstPreview() {
      const txt = document.getElementById('astOutputViewer').textContent;
      navigator.clipboard.writeText(txt);
      document.getElementById('astMetaText').textContent = '✅ Đã copy bộ khung AST Skeleton vào Clipboard!';
    }

    async function openOutputFolder() {
      await apiPost('/api/open-folder', {});
    }

    window.addEventListener('DOMContentLoaded', async () => {
      await loadStatus();
      await runTriage();
    });
  </script>
</body>
</html>
"""


class FreeModelStudioHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        raw_bytes = STUDIO_GUI_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw_bytes)))
        self.end_headers()
        self.wfile.write(raw_bytes)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body_raw = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else "{}"
        try:
            payload = json.loads(body_raw)
        except Exception:
            payload = {}

        path = urllib.parse.urlparse(self.path).path

        if path == "/api/status":
            online, models, _ = check_ollama_status()
            cloud = detect_cloud_free_providers()
            self._send_json({
                "ollama_online": online,
                "ollama_models": models,
                "best_local_model": select_best_local_model(models) if online else "qwen7b-antigravity",
                "cloud_providers": [p["provider"] for p in cloud],
                "has_ctx_optimizer": HAS_CTX_OPTIMIZER,
                "quick_targets": QUICK_TARGETS,
            })
            return

        if path == "/api/boot-ollama":
            ok = try_start_ollama_service()
            self._send_json({"ok": ok})
            return

        if path == "/api/pick-path":
            mode = payload.get("mode", "folder")
            chosen = open_native_windows_picker(mode=mode)
            self._send_json({"chosen": chosen})
            return

        if path == "/api/triage":
            res = triage_task_scope_and_complexity(
                prompt=payload.get("prompt", ""),
                target=payload.get("target", ""),
                glob_pattern=payload.get("glob", "*"),
                max_files=int(payload.get("max_files", 15)),
            )
            self._send_json(res)
            return

        if path == "/api/batch-scan":
            summary = run_broad_batch_scan(
                target=payload.get("target", ""),
                prompt=payload.get("prompt", "Tóm tắt mục tiêu và các hàm chính"),
                glob_pattern=payload.get("glob", "*"),
                max_files=int(payload.get("max_files", 10)),
                workers=int(payload.get("workers", 4)),
                provider=payload.get("provider", "auto"),
                model=payload.get("model", ""),
            )
            if summary.get("ok") and summary.get("digest_file"):
                try:
                    summary["digest_markdown"] = Path(summary["digest_file"]).read_text(encoding="utf-8", errors="replace")
                except Exception:
                    summary["digest_markdown"] = ""
            self._send_json(summary)
            return

        if path == "/api/run-single":
            prompt = payload.get("prompt", "Tóm tắt cấu trúc file")
            target = payload.get("target", "")
            lines = payload.get("lines", "")
            ok, ans, meta = execute_on_best_free_model(
                prompt=prompt,
                target=target or None,
                lines=lines or None,
                preferred_provider=payload.get("provider", "auto"),
                preferred_model=payload.get("model", ""),
                try_boot_ollama=True,
            )
            out_file = save_single_task_output(
                title="GUI Single Task",
                prompt=prompt,
                target=target,
                response_text=ans,
                run_meta=meta,
            )
            self._send_json({
                "ok": ok,
                "provider": meta.get("provider"),
                "model": meta.get("model"),
                "elapsed_seconds": meta.get("elapsed_seconds"),
                "ast_compression": meta.get("ast_compression"),
                "output_file": str(out_file),
                "response_text": ans,
            })
            return

        if path == "/api/preview-ast":
            full_prompt, meta = build_ast_compressed_prompt(
                prompt=payload.get("prompt", ""),
                target=payload.get("target") or None,
                lines=payload.get("lines") or None,
            )
            self._send_json({"full_prompt": full_prompt, "meta": meta})
            return

        if path == "/api/history":
            self._send_json({"reports": list_history_reports()})
            return

        if path == "/api/read-report":
            fname = Path(payload.get("filename", "")).name
            f_path = OUTPUT_DIR / fname
            content = f_path.read_text(encoding="utf-8", errors="replace") if f_path.is_file() else "[Không tìm thấy báo cáo]"
            self._send_json({"filename": fname, "content": content})
            return

        if path == "/api/open-folder":
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            if os.name == "nt":
                subprocess.Popen(["explorer", str(OUTPUT_DIR)])
            self._send_json({"ok": True})
            return

        self._send_json({"error": "Not found"}, status=404)


def launch_app_window(url: str) -> None:
    """Ưu tiên mở giao diện ở chế độ Cửa sổ Ứng dụng Desktop (--app) của Edge/Chrome."""
    if os.name == "nt":
        candidates = [
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        ]
        for exe in candidates:
            if exe.is_file():
                try:
                    subprocess.Popen([str(exe), f"--app={url}", "--window-size=1420,880"])
                    return
                except Exception:
                    pass
    webbrowser.open(url)


def main() -> int:
    parser = argparse.ArgumentParser(description="Antigravity Free-Model Token Offloader Studio GUI")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    parser.add_argument("--no-browser", action="store_true", help="Chỉ khởi chạy Server, không tự bật cửa sổ")
    parser.add_argument("--self-test", action="store_true", help="Chạy kiểm thử tự động các API của GUI rồi thoát (Exit Code = 0)")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), FreeModelStudioHandler)
    url = f"http://{args.host}:{args.port}"

    if args.self_test:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        import urllib.request as ureq
        try:
            with ureq.urlopen(url, timeout=5) as r_html:
                html_len = len(r_html.read())
            req_st = ureq.Request(f"{url}/api/status", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
            with ureq.urlopen(req_st, timeout=5) as r_st:
                st_data = json.loads(r_st.read().decode("utf-8"))
            print(f"[GUI SELF-TEST PASS] URL={url} | HTML={html_len} bytes | QuickTargets={len(st_data.get('quick_targets', []))}")
            server.shutdown()
            return 0
        except Exception as e:
            print(f"[GUI SELF-TEST FAIL] {e}", file=sys.stderr)
            server.shutdown()
            return 1

    print("=" * 78)
    print(f" ⚡ TRUNG TÂM ĐIỀU PHỐI MODEL MIỄN PHÍ (GUI STUDIO): {url}")
    print("    Nhấn Ctrl+C trong cửa sổ này khi muốn đóng hoàn toàn dịch vụ.")
    print("=" * 78)

    if not args.no_browser:
        threading.Timer(0.6, lambda: launch_app_window(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Đã đóng Free-Model Studio GUI.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
