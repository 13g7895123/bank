# Windows Python Setup Script with venv
# Usage: .\setup_env.ps1

$separator = "------------------------------------------------------------"

Write-Host $separator -ForegroundColor Cyan
Write-Host "          Python Environment Setup (venv)" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
$VenvDir = Join-Path $ScriptDir "venv"

Write-Host "[1/6] Checking Python..." -ForegroundColor Blue

# Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[X] Python not found" -ForegroundColor Red
    Write-Host "Please install Python: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create or check venv
Write-Host ""
Write-Host "[2/6] Setting up virtual environment..." -ForegroundColor Blue

if (Test-Path $VenvDir) {
    Write-Host "[OK] venv already exists: $VenvDir" -ForegroundColor Green
} else {
    Write-Host "  Creating venv..." -ForegroundColor Gray
    python -m venv $VenvDir
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] venv created: $VenvDir" -ForegroundColor Green
    } else {
        Write-Host "[X] Failed to create venv" -ForegroundColor Red
        exit 1
    }
}

# Activate venv
Write-Host ""
Write-Host "[3/6] Activating venv..." -ForegroundColor Blue
$activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "[OK] venv activated" -ForegroundColor Green
} else {
    Write-Host "[X] Activate script not found: $activateScript" -ForegroundColor Red
    exit 1
}

# Check requirements.txt
Write-Host ""
Write-Host "[4/6] Checking requirements.txt..." -ForegroundColor Blue
$requirementsFile = Join-Path $ScriptDir "requirements.txt"

if (Test-Path $requirementsFile) {
    Write-Host "[OK] Found requirements.txt" -ForegroundColor Green
    
    $packages = Get-Content $requirementsFile | Where-Object { $_ -notmatch "^#" -and $_.Trim() -ne "" }
    Write-Host ""
    Write-Host "  Required packages:" -ForegroundColor Gray
    foreach ($pkg in $packages) {
        Write-Host "    - $pkg" -ForegroundColor Gray
    }
} else {
    Write-Host "[X] requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Install packages
Write-Host ""
Write-Host "[5/6] Installing packages in venv..." -ForegroundColor Blue

Write-Host "  Upgrading pip..." -ForegroundColor Gray
python -m pip install --upgrade pip 2>&1 | Out-Null

Write-Host "  Installing dependencies..." -ForegroundColor Gray
pip install -r $requirementsFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] All packages installed" -ForegroundColor Green
} else {
    Write-Host "[X] Installation failed" -ForegroundColor Red
    exit 1
}

# Install Playwright browsers (if playwright is installed)
Write-Host ""
Write-Host "[6/6] Checking Playwright browsers..." -ForegroundColor Blue

$playwrightInstalled = pip show playwright 2>&1 | Select-String "Name: playwright"
if ($playwrightInstalled) {
    Write-Host "  Playwright detected, installing browsers..." -ForegroundColor Gray
    playwright install chromium
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Playwright browsers installed" -ForegroundColor Green
    } else {
        Write-Host "[!] Playwright browser installation had issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "[--] Playwright not in requirements, skipping browser install" -ForegroundColor Gray
}

# Verify
Write-Host ""
Write-Host $separator -ForegroundColor Cyan
Write-Host "          Installed Packages (in venv)" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

pip list --format=columns

Write-Host ""
Write-Host $separator -ForegroundColor Green
Write-Host "          Setup Complete!" -ForegroundColor Green
Write-Host $separator -ForegroundColor Green
Write-Host ""
Write-Host "To activate venv manually, run:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To deactivate venv, run:" -ForegroundColor Yellow
Write-Host "  deactivate" -ForegroundColor White
