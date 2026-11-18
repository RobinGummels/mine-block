[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$env:TURBO_TELEMETRY_DISABLED = '1'
Push-Location (Join-Path $projectRoot 'frontend')
try {
    Write-Host 'Storybook: http://127.0.0.1:6001/?path=/story/mode-base-book--random'
    & pnpm.cmd run storybook --filter=lines
    if ($LASTEXITCODE -ne 0) { throw "Storybook exited with code $LASTEXITCODE" }
} finally { Pop-Location }
