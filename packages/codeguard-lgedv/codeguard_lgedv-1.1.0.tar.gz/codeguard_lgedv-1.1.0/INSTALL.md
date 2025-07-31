
# MCP Server Installation Guide

## Windows

### 1. Download and Install Python
- Go to: https://www.python.org/downloads/windows/
- Download Python 3.9+ (recommended: 3.10 or newer).
- During installation, select **Add Python to PATH** before clicking Install.
- After installation, open Command Prompt and check:
  ```powershell
  python --version
  pip --version
  ```

### 2. Download the Auto-Install Script
- Download `install_mcp.ps1` from the project repository.

### 3. Run the Installation Script
- Open PowerShell and run:
  ```powershell
  .\install_mcp.ps1 -ProjectDir "C:\mcp_test" -PackageName "codeguard-lgedv"
  ```
- The script will:
  - Create a virtual environment (venv)
  - Install the MCP server package
  - Check for the executable
  - Automatically create `.vscode/mcp.json` configuration file

### 4. Configure MCP Server (if needed)
- Edit `.vscode/mcp.json` to set correct paths for `CPP_DIR` and `CUSTOM_RULE_PATH`.

### 5. Run MCP Server
- Start the server with:
  ```powershell
  C:\mcp_test\venv\Scripts\codeguard.exe --transport stdio
  ```

### 6. Uninstall MCP Server
- Delete the folder `C:\mcp_test` to remove all installed files.

---

## Linux

### 1. Install Python
- Install Python 3.9+ (recommended: 3.10 or newer):
  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip
  ```
- Check installation:
  ```bash
  python3 --version
  pip3 --version
  ```

### 2. Download the Auto-Install Script
- Download `install_mcp.sh` from the project repository.
- Make the script executable:
  ```bash
  chmod +x install_mcp.sh
  ```

### 3. Run the Installation Script
- Run the script:
  ```bash
  ./install_mcp.sh ~/mcp_test codeguard-lgedv
  ```
- The script will:
  - Create a virtual environment (venv)
  - Install the MCP server package
  - Check for the executable
  - Automatically create `.vscode/mcp.json` configuration file

### 4. Configure MCP Server (if needed)
- Edit `.vscode/mcp.json` to set correct paths for `CPP_DIR` and `CUSTOM_RULE_PATH`.

### 5. Run MCP Server
- Start the server with:
  ```bash
  ~/mcp_test/venv/bin/codeguard --transport stdio
  ```

### 6. Uninstall MCP Server
- Delete the folder `~/mcp_test` to remove all installed files.

---

**Note:**
- If you encounter errors, check Python installation and permissions.
- For custom rules, update the path in `mcp.json` accordingly.

For further help, contact the project maintainer or refer to the README.md.
