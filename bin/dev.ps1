$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    python .\main.py @args
}
finally {
    Pop-Location
}
