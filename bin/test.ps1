$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    python -m pytest tests/unit -q @args
}
finally {
    Pop-Location
}
