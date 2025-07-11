# SDF工具启动脚本
# 自动激活虚拟环境并启动应用程序

Write-Host "正在激活虚拟环境..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

Write-Host "正在启动SDF工具..." -ForegroundColor Green
python quick_start.py

Write-Host "程序已退出" -ForegroundColor Yellow
