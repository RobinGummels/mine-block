[CmdletBinding()]
param([switch]$Browser, [switch]$Rust)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot 'math\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run scripts\setup.ps1 first.' }
function Invoke-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Executable failed with code $LASTEXITCODE" }
}
Push-Location (Join-Path $projectRoot 'math')
try {
    Invoke-Checked $pythonPath @('-m', 'pytest', 'tests', '-q')
    Invoke-Checked $pythonPath @((Join-Path $PSScriptRoot 'math_smoke.py'))
    if ($Rust) { Invoke-Checked 'cargo' @('check', '--locked', '--manifest-path', 'optimization_program/Cargo.toml') }
} finally { Pop-Location }
if ($Browser) {
    Push-Location (Join-Path $projectRoot 'qa')
    try { Invoke-Checked 'npm.cmd' @('test') } finally { Pop-Location }
}
