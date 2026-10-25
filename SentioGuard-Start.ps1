
param(
    [switch]$Backend,
    [switch]$Tunnel
)

$ErrorActionPreference = 'Stop'

$project = $PSScriptRoot
$portable = $env:COMFY_PORTABLE_ROOT
$cloudflared = $env:CLOUDFLARED_PATH
$website = 'https://sentioguard-ai-web.pages.dev/'

if (-not $portable) {
    Write-Host 'Set COMFY_PORTABLE_ROOT to your portable ComfyUI folder.' -ForegroundColor Red
    exit 1
}

if (-not $cloudflared) {
    Write-Host 'Set CLOUDFLARED_PATH to your cloudflared executable.' -ForegroundColor Red
    exit 1
}

$python = Join-Path $portable 'python_embeded\python.exe'

if ($Backend) {
    Set-Location -LiteralPath $project
    & $python '.\backend\app\run.py'
    exit $LASTEXITCODE
}

if ($Tunnel) {
    & $cloudflared tunnel --protocol http2 --url 'http://127.0.0.1:8000'
    exit $LASTEXITCODE
}

if (-not (Test-Path -LiteralPath $project)) {
    throw "Project folder not found: $project"
}

if (-not (Test-Path -LiteralPath $python)) {
    throw "Embedded Python not found: $python"
}

if (-not (Test-Path -LiteralPath $cloudflared)) {
    throw "cloudflared executable not found: $cloudflared"
}

$script = $PSCommandPath

Start-Process -FilePath 'powershell.exe' -ArgumentList @(
    '-NoExit', '-ExecutionPolicy', 'Bypass',
    '-File', "`"$script`"", '-Backend'
)

Start-Sleep -Seconds 3

Start-Process -FilePath 'powershell.exe' -ArgumentList @(
    '-NoExit', '-ExecutionPolicy', 'Bypass',
    '-File', "`"$script`"", '-Tunnel'
)

Start-Sleep -Seconds 8
Start-Process $website

Write-Host ''
Write-Host 'SentioGuard startup launched.' -ForegroundColor Green
Write-Host 'Keep the backend and tunnel terminal windows open.'
Write-Host 'Quick Tunnel URLs may change between runs.'
Write-Host 'If the tunnel URL changes, update BACKEND_URL in your Cloudflare Worker.'
Write-Host 'Never expose FLOAT_API_KEY.'
Read-Host 'Press Enter to close this launcher'
