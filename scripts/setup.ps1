# HackHub Setup Script for Development

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "        HackHub - Development Setup         " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$prerequisites = @(
    @{Name="Node.js"; Command="node --version"},
    @{Name="npm"; Command="npm --version"},
    @{Name="Python"; Command="python --version"},
    @{Name="Docker"; Command="docker --version"},
    @{Name="Docker Compose"; Command="docker compose version"}
)

$allInstalled = $true
foreach ($prereq in $prerequisites) {
    try {
        $version = Invoke-Expression $prereq.Command
        Write-Host "  [OK] $($prereq.Name): $version" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] $($prereq.Name) is not installed" -ForegroundColor Red
        $allInstalled = $false
    }
}

if (-not $allInstalled) {
    Write-Host "`nPlease install missing prerequisites and try again." -ForegroundColor Red
    exit 1
}

Write-Host "`nAll prerequisites met!" -ForegroundColor Green
Write-Host ""

# Setup environment files
Write-Host "Setting up environment files..." -ForegroundColor Yellow

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "  Created backend\.env from .env.example" -ForegroundColor Green
} else {
    Write-Host "  backend\.env already exists, skipping" -ForegroundColor Gray
}

if (-not (Test-Path "frontend\.env.local")) {
    Copy-Item "frontend\.env.example" "frontend\.env.local"
    Write-Host "  Created frontend\.env.local from .env.example" -ForegroundColor Green
} else {
    Write-Host "  frontend\.env.local already exists, skipping" -ForegroundColor Gray
}

# Install backend dependencies
Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
Set-Location -Path "backend"
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
Set-Location -Path ".."
Write-Host "  Backend dependencies installed" -ForegroundColor Green

# Install frontend dependencies
Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Yellow
Set-Location -Path "frontend"
npm install
Set-Location -Path ".."
Write-Host "  Frontend dependencies installed" -ForegroundColor Green

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "     Setup Complete!                         " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor White
Write-Host "  1. Start Docker services:      docker compose up -d postgres redis" -ForegroundColor Gray
Write-Host "  2. Run data migrations:        cd backend; alembic upgrade head" -ForegroundColor Gray
Write-Host "  3. Start backend:              cd backend; uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "  4. Start frontend:             cd frontend; npm run dev" -ForegroundColor Gray
Write-Host "  5. Full stack with Docker:     docker compose up" -ForegroundColor Gray
Write-Host ""
Write-Host "Access:" -ForegroundColor White
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor Gray
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
