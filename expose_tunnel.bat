@echo off
setlocal
set PORT=8080

echo ==================================================================
echo  SwitchGuard Public HTTPS Tunnel Launcher
echo  Generates an instant public HTTPS URL for Switch AI Cloud
echo ==================================================================

where cloudflared >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [Tunnel] Using Cloudflare Tunnel...
    cloudflared tunnel --url http://127.0.0.1:%PORT%
    goto end
)

where ngrok >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [Tunnel] Using ngrok...
    ngrok http %PORT%
    goto end
)

where npx >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [Tunnel] Using Cloudflare quick tunnel via npx untun...
    echo [Tip] Copy the generated https://*.trycloudflare.com URL into Switch AI Console
    npx untun@latest tunnel http://127.0.0.1:%PORT%
    goto end
)

echo [!] No tunneling tool detected.
echo To expose your local agent with a free public HTTPS URL:
echo   Run: npx untun@latest tunnel http://127.0.0.1:%PORT%
echo   Or install ngrok: ngrok http %PORT%

:end
