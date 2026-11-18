[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$secureKey = Read-Host 'Enter a NEW UniGPT key for the read-only model-list check (hidden)' -AsSecureString
try {
    $credential = New-Object System.Net.NetworkCredential('', $secureKey)
    $headers = @{ Authorization = 'Bearer ' + $credential.Password }
    $result = Invoke-RestMethod -Uri 'https://gpt.uni-muenster.de/v1/models' -Headers $headers -Method Get -TimeoutSec 30
    $model = @($result.data | Where-Object { $_.id -eq 'DeepSeek-V4-Flash' })
    if ($model.Count -eq 0) { throw 'The endpoint responded, but DeepSeek-V4-Flash was not listed. Verify the exact model ID in UniGPT.' }
    Write-Host 'UniGPT authentication succeeded and DeepSeek-V4-Flash is listed. No generation request was sent.'
} catch {
    # Do not dump HTTP request objects, headers, credentials or response bodies.
    throw 'UniGPT model-list check failed. Check the new key, endpoint, model ID and network access in the portal.'
} finally {
    $headers = $null
    $credential = $null
    $secureKey.Dispose()
}
