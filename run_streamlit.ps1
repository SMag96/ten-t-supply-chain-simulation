$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
    }
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt -c requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
    .\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
    if ($LASTEXITCODE -ne 0) { throw "Streamlit exited with an error." }
} finally {
    Pop-Location
}
