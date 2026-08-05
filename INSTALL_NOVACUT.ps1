$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$payloadDir = Join-Path $root 'payload'
$zipPath = Join-Path $root 'NovaCut.zip'
$expectedSha256 = '2959c60a725d48e6db3e20cb78da516e986972a889638f272273f8cfc65a5226'

Write-Host ''
Write-Host 'NovaCut Installer' -ForegroundColor Cyan
Write-Host 'Reconstructing the original editor package...'

$parts = 1..8 | ForEach-Object {
    Join-Path $payloadDir ('novacut.b64.{0:D3}' -f $_)
}

foreach ($part in $parts) {
    if (-not (Test-Path -LiteralPath $part)) {
        throw "Missing payload file: $part"
    }
}

$base64 = ($parts | ForEach-Object {
    [System.IO.File]::ReadAllText($_).Trim()
}) -join ''

[System.IO.File]::WriteAllBytes(
    $zipPath,
    [System.Convert]::FromBase64String($base64)
)

$actualSha256 = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSha256 -ne $expectedSha256) {
    Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
    throw "Integrity check failed. Expected $expectedSha256 but received $actualSha256"
}

Write-Host 'Package verified.' -ForegroundColor Green
Write-Host 'Extracting NovaCut...'
Expand-Archive -LiteralPath $zipPath -DestinationPath $root -Force

$launcher = Join-Path $root 'NovaCut\NOVACUT.bat'
if (-not (Test-Path -LiteralPath $launcher)) {
    throw "Extraction completed, but the launcher was not found at $launcher"
}

Write-Host ''
Write-Host 'NovaCut is installed.' -ForegroundColor Green
Write-Host 'The editor will open now. The first setup run installs its free local dependencies.'
Write-Host ''
Start-Process -FilePath $launcher -WorkingDirectory (Split-Path -Parent $launcher)
