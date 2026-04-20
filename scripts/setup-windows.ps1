# setup-windows.ps1 - Idempotent Windows Environment Setup
$ErrorActionPreference = "Stop"

Write-Host "--- Windows Environment Setup ---" -ForegroundColor Cyan

# 1. Check Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.12."
}

# 2. Create Venv
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# 3. Install Dependencies
Write-Host "Installing dependencies..."
& .\.venv\Scripts\pip install --upgrade pip
& .\.venv\Scripts\pip install -r requirements.txt
& .\.venv\Scripts\pip install torch-directml  # AMD Acceleration for Windows

# 4. Check GPU Drivers
Write-Host "Checking for AMD Adrenaline Drivers..."
if (Get-WmiObject Win32_VideoController | Where-Object { $_.Name -match "AMD" }) {
    Write-Host "AMD GPU detected." -ForegroundColor Green
} else {
    Write-Warning "No AMD GPU detected. System will run on CPU."
}

Write-Host "Setup Complete. Run server with: .\venv\Scripts\fastapi run src\main.py" -ForegroundColor Green
