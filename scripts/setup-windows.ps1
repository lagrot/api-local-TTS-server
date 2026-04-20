# setup-windows.ps1 - Idempotent Windows Environment Setup med uv
$ErrorActionPreference = "Stop"

Write-Host "--- Windows Environment Setup (uv) ---" -ForegroundColor Cyan

# 1. Kontrollera om uv finns, installera annars
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv saknas, installerar..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

# 2. Skapa venv och synka miljö
if (!(Test-Path ".venv")) {
    Write-Host "Skapar venv med uv..."
    uv venv
}

# 3. Synka beroenden från pyproject.toml
Write-Host "Synkar beroenden..."
uv sync

# 4. Kontrollera GPU
Write-Host "Kontrollerar AMD Adrenaline..."
if (Get-WmiObject Win32_VideoController | Where-Object { $_.Name -match "AMD" }) {
    Write-Host "AMD GPU detekterad." -ForegroundColor Green
} else {
    Write-Warning "Ingen AMD GPU detekterad. Kör på CPU."
}

Write-Host "Setup Complete. Starta med: .\.venv\Scripts\fastapi run src\main.py" -ForegroundColor Green
