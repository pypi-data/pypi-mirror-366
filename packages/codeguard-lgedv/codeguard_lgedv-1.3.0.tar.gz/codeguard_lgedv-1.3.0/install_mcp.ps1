param(
    [string]$ProjectDir = "C:\mcp_test",
    [string]$PackageName = "codeguard-lgedv"
)

Write-Host "[INFO] MCP Server Auto Installer" -ForegroundColor Cyan
Write-Host "Project directory: $ProjectDir"
Write-Host "Python package: $PackageName"

# 1. Kiểm tra Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python is not installed. Please install Python 3.9+ from https://www.python.org/downloads/windows/" -ForegroundColor Red
    exit 1
}

# 2. Tạo thư mục dự án nếu chưa có
if (!(Test-Path $ProjectDir)) {
    New-Item -ItemType Directory -Path $ProjectDir | Out-Null
}
Set-Location $ProjectDir

# 3. Tạo môi trường ảo venv
if (!(Test-Path "$ProjectDir\venv\Scripts\Activate.ps1")) {
    Write-Host "[INFO] Creating virtual environment..."
    python -m venv venv
}

# 4. Kích hoạt venv
Write-Host "[INFO] Activating virtual environment..."
$venvActivate = "$ProjectDir\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Host "[ERROR] Failed to activate venv!" -ForegroundColor Red
    exit 1
}

# 5. Cài đặt package MCP server
Write-Host "[INFO] Installing MCP server package..."
$venvPython = "$ProjectDir\venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install $PackageName

# 6. Kiểm tra file thực thi
$exePath = "$ProjectDir\venv\Scripts\codeguard.exe"
if (Test-Path $exePath) {
    Write-Host "[SUCCESS] MCP server installed: $exePath" -ForegroundColor Green
} else {
    Write-Host "[ERROR] MCP server executable not found!" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Installation complete. You can run MCP server with:"
Write-Host "    $exePath --transport stdio" -ForegroundColor Yellow

# 7. Tự động tạo file mcp.json với cấu hình mẫu
$vscodeDir = "$ProjectDir\.vscode"
if (!(Test-Path $vscodeDir)) {
    New-Item -ItemType Directory -Path $vscodeDir | Out-Null
}
$mcpJsonPath = "$vscodeDir\mcp.json"
$mcpJsonContent = @'
{
  "servers": {
    "lgedv": {
      "command": "C:\\mcp_test\\venv\\Scripts\\codeguard.exe",
      "args": ["--transport", "stdio"],
      "env": {
        "CPP_DIR": "C:\\path\\to\\cpp_dir",
        "CUSTOM_RULE_PATH": "C:\\path\\to\\CustomRule.md"
      }
    }
  }
}
'@
Set-Content -Path $mcpJsonPath -Value $mcpJsonContent -Encoding UTF8
Write-Host ("[INFO] Created mcp.json at " + $mcpJsonPath) -ForegroundColor Green