# CodeVault AI - Setup Script (PowerShell)
# Run this once: Right-click > Run with PowerShell

Write-Host ""
Write-Host "  ╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║     CodeVault AI - First Time Setup  ║" -ForegroundColor Cyan 
Write-Host "  ╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python 
try { 
    $pyver = python --version 2>&1
    Write-Host "  [OK] $pyver found" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python not found. Install from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
 
# Install packages
Write-Host ""
Write-Host "  Installing required packages..." -ForegroundColor Yellow

python -m pip install --upgrade pip --quiet
python -m pip install pygments matplotlib --quiet

Write-Host "  [OK] pygments installed" -ForegroundColor Green
Write-Host "  [OK] matplotlib installed" -ForegroundColor Green

Write-Host ""
Write-Host "  Setup complete! You can now:" -ForegroundColor Cyan
Write-Host "  1. Double-click launch.bat to run CodeVault AI" -ForegroundColor White
Write-Host "  2. Or open a terminal here and run: python main.py" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to launch CodeVault AI now"
Set-Location $PSScriptRoot
python main.py
