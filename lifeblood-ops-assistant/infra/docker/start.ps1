#!/usr/bin/env pwsh
# Docker Quick Start Script for Windows PowerShell

Write-Host "🐳 Lifeblood Ops Assistant - Docker Quick Start" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "../../.env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from template..." -ForegroundColor Yellow
    Copy-Item "../../env.template" "../../.env"
    Write-Host ""
    Write-Host "✏️  Please edit .env and add your GEMINI_API_KEY:" -ForegroundColor Green
    Write-Host "   notepad ../../.env" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Green
    exit 0
}

# Check if GEMINI_API_KEY is set
$envContent = Get-Content "../../.env" -Raw
if ($envContent -notmatch "GEMINI_API_KEY=.+") {
    Write-Host "⚠️  GEMINI_API_KEY not set in .env file!" -ForegroundColor Red
    Write-Host "Please edit .env and add your API key, then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment configuration found" -ForegroundColor Green
Write-Host ""

# Ask user which mode
Write-Host "Select deployment mode:" -ForegroundColor Cyan
Write-Host "1. Production (optimized builds, nginx)" -ForegroundColor White
Write-Host "2. Development (hot-reload, debug logging)" -ForegroundColor White
Write-Host ""
$mode = Read-Host "Enter choice (1 or 2)"

if ($mode -eq "2") {
    Write-Host ""
    Write-Host "🚀 Starting in DEVELOPMENT mode..." -ForegroundColor Green
    Write-Host ""
    docker compose -f compose.dev.yaml up --build
} else {
    Write-Host ""
    Write-Host "🚀 Starting in PRODUCTION mode..." -ForegroundColor Green
    Write-Host ""
    Write-Host "Building images..." -ForegroundColor Yellow
    docker compose up --build -d
    
    Write-Host ""
    Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host ""
    Write-Host "✅ Services started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Service Status:" -ForegroundColor Cyan
    docker compose ps
    
    Write-Host ""
    Write-Host "🌐 Access Points:" -ForegroundColor Cyan
    Write-Host "   Web UI:   http://localhost:3000" -ForegroundColor Green
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Ingest documents:" -ForegroundColor White
    Write-Host "      Invoke-WebRequest -Method POST http://localhost:8000/ingest" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. View logs:" -ForegroundColor White
    Write-Host "      docker compose logs -f" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   3. Stop services:" -ForegroundColor White
    Write-Host "      docker compose down" -ForegroundColor Gray
}
