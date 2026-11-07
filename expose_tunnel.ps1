<#
.SYNOPSIS
    Exposes the local SwitchGuard Agent (port 8080) to the internet with a public HTTPS tunnel.
    Required for Switch AI Console webhooks if running locally.
#>
param(
    [int]$Port = 8080
)

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " SwitchGuard Public HTTPS Tunnel Launcher" -ForegroundColor Cyan
Write-Host " Generates an instant public HTTPS URL for Switch AI Cloud" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Check for cloudflared
if (Get-Command cloudflared -ErrorAction SilentlyContinue) {
    Write-Host "[Tunnel] Using Cloudflare Tunnel (cloudflared)..." -ForegroundColor Green
    cloudflared tunnel --url "http://127.0.0.1:$Port"
    exit 0
}

# 2. Check for ngrok
if (Get-Command ngrok -ErrorAction SilentlyContinue) {
    Write-Host "[Tunnel] Using ngrok..." -ForegroundColor Green
    ngrok http $Port
    exit 0
}

# 3. Check for npx (Cloudflare Untun - Zero Token / Zero Signup)
if (Get-Command npx -ErrorAction SilentlyContinue) {
    Write-Host "[Tunnel] Using Cloudflare quick tunnel via npx untun..." -ForegroundColor Green
    Write-Host "[Tip] Copy the generated https://*.trycloudflare.com URL into Switch AI Console" -ForegroundColor Yellow
    npx untun@latest tunnel "http://127.0.0.1:$Port"
    exit 0
}

Write-Host "[!] No tunneling tool detected." -ForegroundColor Yellow
Write-Host "To expose your local agent with a free public HTTPS URL, run one of:" -ForegroundColor Gray
Write-Host "  Option A (Quick):  npx untun@latest tunnel http://127.0.0.1:$Port" -ForegroundColor White
Write-Host "  Option B (ngrok):  winget install ngrok ; ngrok http $Port" -ForegroundColor White
Write-Host "  Option C (Cloudflare): winget install Cloudflare.cloudflared ; cloudflared tunnel --url http://127.0.0.1:$Port" -ForegroundColor White
