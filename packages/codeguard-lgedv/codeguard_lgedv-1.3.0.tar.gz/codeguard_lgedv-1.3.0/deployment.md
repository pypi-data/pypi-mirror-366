# Build and upload package
Truy cập https://pypi.org/account/register/
Đăng ký tài khoản và xác thực email.

(xoa existing venv)
rm -rf venv

sudo apt install python3.12-venv
source venv/bin/activate
pip install build twine
(trong thu muc chua pyproject.toml)
pip install build
python -m build

Kết quả: thư mục dist/ sẽ có file .whl và .tar.gz

upload len PyPI
twine upload dist/*

# Instation by user
## on Linux
python3 -m venv venv
source venv/bin/activate
pip install codeguard-lgedv

### mcp.json
"servers": {
  "codeguard": {
    "command": "/duong_dan_toi_venv/bin/codeguard",
    "args": ["--transport", "stdio"]
  }
}


## on window
### 1. Cài đặt Python và pip
- Truy cập trang chủ Python: https://www.python.org/downloads/windows/
- Tải bản Python 3.9+ (khuyến nghị 3.10 hoặc mới hơn).
- Chạy file cài đặt, chọn **Add Python to PATH** trước khi nhấn Install.
- Sau khi cài xong, mở Command Prompt (cmd) và kiểm tra:
  ```bash
  python --version
  pip --version
  ```
---

### 2. Tạo môi trường ảo (venv)

- Tạo thư mục dự án (ví dụ: `C:\mcp_test`)
- Mở cmd tại thư mục đó, chạy:
  ```bash
  python -m venv venv
  ```
- Kích hoạt venv:
  ```bash
  venv\Scripts\activate
  ```
- Kiểm tra lại:
  ```bash
  python --version
  pip --version
  ```

### 3. Cài đặt MCP server từ PyPI

- Cài đặt package (ví dụ: `codeguard-lgedv` hoặc tên package bạn đã upload):
  ```bash
  pip install codeguard-lgedv
  ```
- Kiểm tra file thực thi đã cài:
  ```bash
  dir venv\Scripts\codeguard.exe
  ```
  Nếu thấy file `codeguard.exe` là đã cài thành công.

---

### 4. Cấu hình file mcp.json (nếu dùng với extension hoặc cần custom rule)
- create folder .vscode on current codebase
- create file mcp.json in .vscode folder
- Ví dụ nội dung:
  ```json
  {
    "servers": {
        "lgedv": {
            "command": "C:\\Users\\tai2.tran\\mcp_server\\venv\\Scripts\\codeguard.exe",
            "args": ["--transport", "stdio"],
            "env": {
            "CPP_DIR": "E:\\src\\code_test\\mem_leak",
            "CUSTOM_RULE_PATH": "E:\\src\\codefun\\deepl\\mcp_server\\lgedv\\resources\\CustomRule.md" 
            }
        }
    }
  }
  ```




Để triển khai MCP server bằng PyInstaller, bạn cần thực hiện các bước sau:

---

### 1. Sửa code MCP server để đọc file tài nguyên (markdown) đúng cách

Giả sử bạn đang đọc file markdown như sau:
```python
with open("copilot_md/Custom.md", "r") as f:
    data = f.read()
```

Bạn cần thay bằng đoạn sau ở mọi nơi đọc file tài nguyên:

```python
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Đọc file markdown
with open(resource_path("copilot_md/Custom.md"), "r") as f:
    data = f.read()
```

- Nếu có nhiều file, dùng hàm này cho mọi file tài nguyên đóng gói.

---

### 2. Build file thực thi độc lập bằng PyInstaller

Kích hoạt venv (nếu dùng), cài PyInstaller:
```bash
pip install pyinstaller
```

Build file thực thi, đóng gói các file markdown:
```bash
pyinstaller --onefile lgedv/server.py --name codeguard \
  --add-data "copilot_md/Custom.md:copilot_md" \
  --add-data "copilot_md/Misracpp2008Guidelines_en.md:copilot_md" \
  --add-data "copilot_md/CertcppGuidelines_en.md:copilot_md"
```
- Thêm tất cả file markdown cần thiết bằng `--add-data`.

File thực thi sẽ nằm ở `dist/codeguard`.

---

### 3. Đóng gói và upload lên internet

- Nén file thực thi và các tài liệu hướng dẫn thành file `.zip` hoặc `.tar.gz`.
- Upload lên server, Google Drive, hoặc dịch vụ chia sẻ file (hoặc trang web của bạn).

---

### 4. Hướng dẫn người dùng tải về, cài đặt và sử dụng

**Bước 1:** Tải file thực thi về máy (giải nén nếu cần).

**Bước 2:** Chạy trực tiếp file thực thi:
```bash
./codeguard --transport stdio
```
- Không cần cài pip, không cần môi trường ảo, không cần source code.

**Bước 3:** Cấu hình đường dẫn trong `mcp.json`:
```json
"lgedv": {
  "command": "/duong_dan_toi_file/codeguard",
  "args": ["--transport", "stdio"],
  "env": {
    "CPP_DIR": "/duong_dan_toi_cpp_dir",
    "CUSTOM_RULE_PATH": "copilot_md/Custom.md"
  }
}
```
- Đường dẫn file markdown là đường dẫn tương đối hoặc tuyệt đối, tùy cách bạn đóng gói.

---
Để triển khai đồng thời cả hai cách (pip package và PyInstaller + VSCode extension) mà không phải thay đổi nhiều code MCP server, bạn nên:

### 1. Thiết kế code lấy đường dẫn file rule linh hoạt

Trong file `config.py`, sửa như sau:

```python
def get_rule_path(rule_name, default_relative_path):
    # Ưu tiên lấy từ biến môi trường (cho extension/pyinstaller)
    env_var = f"{rule_name.upper()}_RULE_PATH"
    env_path = os.environ.get(env_var)
    if env_path:
        return env_path
    # Nếu không có, dùng đường dẫn mặc định (cho pip package)
    return os.path.join(BASE_DIR, default_relative_path)

RULE_PATHS = {
    "misra": get_rule_path("misra", "resources/Misracpp2008Guidelines_en.md"),
    "lgedv": get_rule_path("lgedv", "resources/LGEDVRuleGuide.md"),
    "certcpp": get_rule_path("certcpp", "resources/CertcppGuidelines_en.md"),
    "critical": get_rule_path("critical", "resources/CriticalRuleGuideLines.md"),
    "rapidScan": get_rule_path("rapidScan", "resources/RapidScanGuidelines_en.md"),
    "custom": os.environ.get("CUSTOM_RULE_PATH", os.path.join(BASE_DIR, "resources/CustomRule.md"))
}
```

- Khi chạy qua pip: các file rule nằm trong package, code sẽ dùng đường dẫn mặc định.
- Khi chạy qua extension/PyInstaller: truyền đường dẫn file rule qua biến môi trường, code sẽ ưu tiên lấy từ đó.

### 2. Khi build bằng PyInstaller

- Đóng gói file rule vào binary như hướng dẫn trước.
- Extension truyền đường dẫn file rule qua biến môi trường khi start server.

### 3. Khi phân phối qua pip

- Đóng gói file rule vào package (dùng package_data hoặc include trong pyproject.toml).
- Code sẽ tự động lấy file rule từ package.

---

**Tóm lại:**  
- Sử dụng hàm lấy đường dẫn ưu tiên biến môi trường, fallback về đường dẫn mặc định.
- Không cần thay đổi logic đọc file, chỉ cần truyền đúng đường dẫn khi dùng extension/PyInstaller.

Cách này giúp bạn giữ code MCP server gần như nguyên vẹn, dễ bảo trì, dễ triển khai cả hai phương án!