$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$port = 8000
$baseUrl = "http://127.0.0.1:$port"

$process = Start-Process `
  -FilePath python `
  -ArgumentList @("-m", "uvicorn", "server.main:app", "--host", "127.0.0.1", "--port", "$port") `
  -WorkingDirectory $repoRoot `
  -WindowStyle Hidden `
  -PassThru

try {
  Start-Sleep -Seconds 3
  python "$PSScriptRoot\verify_local_mvp.py" --base-url $baseUrl
}
finally {
  Stop-Process -Id $process.Id -ErrorAction SilentlyContinue
}
