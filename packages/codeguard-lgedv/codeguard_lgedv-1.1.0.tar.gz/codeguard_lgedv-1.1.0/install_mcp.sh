#!/bin/bash
# install_mcp.sh - Auto install MCP server on Linux

PROJECT_DIR="${1:-$HOME/mcp_test}"
PACKAGE_NAME="${2:-codeguard-lgedv}"

echo "[INFO] MCP Server Auto Installer (Linux)"
echo "Project directory: $PROJECT_DIR"
echo "Python package: $PACKAGE_NAME"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed. Please install Python 3.9+ (sudo apt install python3)" >&2
    exit 1
fi

# 2. Create project directory if not exists
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 3. Create virtual environment
if [ ! -f "$PROJECT_DIR/venv/bin/activate" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
fi

# 4. Activate venv
source "$PROJECT_DIR/venv/bin/activate"

# 5. Install MCP server package
echo "[INFO] Installing MCP server package..."
pip install --upgrade pip
pip install "$PACKAGE_NAME"

# 6. Check executable
EXE_PATH="$PROJECT_DIR/venv/bin/codeguard"
if [ -f "$EXE_PATH" ]; then
    echo "[SUCCESS] MCP server installed: $EXE_PATH"
else
    echo "[ERROR] MCP server executable not found!" >&2
    exit 1
fi

echo "[INFO] Installation complete. You can run MCP server with:"
echo "    $EXE_PATH --transport stdio"

# 7. Auto create mcp.json config
VSCODE_DIR="$PROJECT_DIR/.vscode"
mkdir -p "$VSCODE_DIR"
MCP_JSON_PATH="$VSCODE_DIR/mcp.json"
cat > "$MCP_JSON_PATH" <<EOF
{
  "servers": {
    "lgedv": {
      "command": "$EXE_PATH",
      "args": ["--transport", "stdio"],
      "env": {
        "CPP_DIR": "/path/to/cpp_dir",
        "CUSTOM_RULE_PATH": "/path/to/CustomRule.md"
      }
    }
  }
}
EOF

echo "[INFO] Created mcp.json at $MCP_JSON_PATH"
