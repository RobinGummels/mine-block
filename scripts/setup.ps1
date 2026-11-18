[CmdletBinding()]
param([switch]$SkipFrontend, [switch]$SkipMath, [switch]$SkipBrowser, [switch]$Rust)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
function Invoke-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Executable failed with code $LASTEXITCODE" }
}
$nodeVersion = [version]((& node --version).TrimStart('v'))
if ($nodeVersion.Major -ne 22 -or $nodeVersion -lt [version]'22.16.0') { throw 'Use Node.js 22.16.0 or newer within major 22.' }
if ((& pnpm.cmd --version).Trim() -ne '10.5.0') { throw 'Install the SDK package manager: npm install -g pnpm@10.5.0' }
if (-not $SkipFrontend) {
    Push-Location (Join-Path $projectRoot 'frontend')
    $previousCi = $env:CI
    try {
        $env:CI = 'true'
        Invoke-Checked 'pnpm.cmd' @('install', '--frozen-lockfile')
    } finally {
        $env:CI = $previousCi
        Pop-Location
    }
}
if (-not $SkipMath) {
    Push-Location (Join-Path $projectRoot 'math')
    try {
        Invoke-Checked 'python' @('-c', 'import sys; assert sys.version_info >= (3, 12), "Python >=3.12 required"')
        Invoke-Checked 'python' @('-m', 'venv', '.venv')
        $pythonPath = Join-Path $PWD '.venv\Scripts\python.exe'
        Invoke-Checked $pythonPath @('-m', 'pip', 'install', '-r', 'requirements-local.txt')
        Invoke-Checked $pythonPath @('-m', 'pip', 'install', '--no-deps', '--no-build-isolation', '-e', '.')
    } finally { Pop-Location }
}
if (-not $SkipBrowser) {
    Push-Location (Join-Path $projectRoot 'qa')
    try {
        if (Test-Path -LiteralPath 'package-lock.json') { Invoke-Checked 'npm.cmd' @('ci') }
        else { Invoke-Checked 'npm.cmd' @('install') }
        Invoke-Checked 'npx.cmd' @('--no-install', 'playwright', 'install', 'chromium')
    } finally { Pop-Location }
}
if ($Rust) {
    Invoke-Checked 'cargo' @('check', '--locked', '--manifest-path', (Join-Path $projectRoot 'math\optimization_program\Cargo.toml'))
}
Write-Host 'Dependencies installed. Run scripts\test-setup.ps1 -Browser -Rust to verify.'
