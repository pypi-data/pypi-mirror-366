$BASE_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "${env:PYTHONPATH};$BASE_DIR"
} else {
    $env:PYTHONPATH = "$BASE_DIR"
}

if (Test-Path -Path "$BASE_DIR/.venv/Scripts/python.exe") {
    & "$BASE_DIR/.venv/Scripts/python.exe" -m swenv @args
}
else {
    python.exe -m swenv @args
}
