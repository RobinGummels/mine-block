[CmdletBinding()]
param([switch]$UseEnvironmentKey)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$previousKey = $env:UNIGPT_API_KEY
try {
    if ($UseEnvironmentKey) {
        if ([string]::IsNullOrWhiteSpace($env:UNIGPT_API_KEY)) { throw 'UNIGPT_API_KEY is not set.' }
    } else {
        $secureKey = Read-Host 'Enter a NEW UniGPT API key (hidden; not saved)' -AsSecureString
        $credential = New-Object System.Net.NetworkCredential('', $secureKey)
        $env:UNIGPT_API_KEY = $credential.Password
        if ([string]::IsNullOrWhiteSpace($env:UNIGPT_API_KEY)) { throw 'No API key entered.' }
    }
    Push-Location $projectRoot
    try {
        & opencode.cmd --standalone $projectRoot
        if ($LASTEXITCODE -ne 0) { throw "OpenCode exited with code $LASTEXITCODE" }
    } finally { Pop-Location }
} finally {
    $env:UNIGPT_API_KEY = $previousKey
    $credential = $null
    if ($secureKey) { $secureKey.Dispose() }
}
