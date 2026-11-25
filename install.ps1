# Script cài đặt đồng bộ bộ Rules & 21 Skills chuẩn Argon vào Antigravity (~/.gemini/config)
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetConfig = Join-Path $env:USERPROFILE ".gemini\config"

Write-Host "==> Đang đồng bộ Rules và Skills vào: $TargetConfig" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TargetConfig | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $TargetConfig "skills") | Out-Null

# 1. Copy Global Rule (GEMINI.md)
Copy-Item -Path (Join-Path $RepoRoot "rules\global\GEMINI.md") -Destination (Join-Path $TargetConfig "GEMINI.md") -Force
Write-Host "  [+] Đã cài đặt Global Rule: GEMINI.md" -ForegroundColor Green

# 2. Copy toàn bộ Skills
Copy-Item -Path (Join-Path $RepoRoot "skills\*") -Destination (Join-Path $TargetConfig "skills") -Recurse -Force
Write-Host "  [+] Đã cài đặt toàn bộ Skills vào $TargetConfig\skills" -ForegroundColor Green

Write-Host "==> Hoàn tất cài đặt bộ Antigravity Argon Skills & Rules!" -ForegroundColor Yellow
