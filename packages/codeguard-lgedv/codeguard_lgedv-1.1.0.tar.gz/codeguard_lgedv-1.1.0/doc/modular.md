# LGEDV MCP Server - Modular Architecture

## 📁 Cấu trúc thư mục mới

```
lgedv/
├── server.py                    # Main server file (modular architecture)
├── modules/                     # Core modules
│   ├── __init__.py
│   ├── config.py               # Cấu hình, constants và MCP resources
│   ├── data_models.py          # Data classes và models
│   ├── file_utils.py           # Tiện ích xử lý files
│   └── rule_fetcher.py         # Fetch rules từ local/remote
├── handlers/                    # Request handlers
│   ├── __init__.py
│   ├── tool_handlers.py        # Xử lý MCP tools
│   ├── prompt_handlers.py      # Xử lý MCP prompts
│   └── resource_handler.py     # Xử lý MCP resources + future features
├── analyzers/                   # Code analyzers
│   ├── __init__.py
│   └── race_analyzer.py        # Race condition analyzer
├── prompts/                     # Prompt templates
│   ├── __init__.py
│   └── prompt_templates.py     # Templates cho các prompts
└── resources/                   # Rule files
    ├── Misracpp2008Guidelines_en.md
    ├── LGEDVRuleGuide.md
    ├── CertcppGuidelines_en.md
    ├── CriticalRuleGuideLines.md
    ├── RapidScanGuidelines_en.md
    └── CustomRule.md
```

## 🔧 Các Module chính

### 1. **modules/config.py**
- Quản lý tất cả cấu hình
- Đường dẫn đến các rule files
- Setup logging
- Environment variables
- **Constants và paths** (MCP Resources logic trong handlers/)

### 2. **modules/data_models.py**
- Data classes cho race condition analysis
- SharedResource, ThreadUsage, RaceCondition
- AnalysisResult với methods tiện ích

### 3. **modules/file_utils.py**
- Utilities để xử lý C++ files
- list_cpp_files(), get_cpp_files_content()
- read_file_content(), file_exists()

### 4. **modules/rule_fetcher.py**
- Class RuleFetcher để fetch rules
- Hỗ trợ cả local files và remote URLs
- Factory functions cho từng loại rule

### 5. **handlers/tool_handlers.py**
- ToolHandler class route các MCP tool calls
- Xử lý fetch rules, list files, detect race conditions
- Clean separation of concerns

### 6. **handlers/prompt_handlers.py**
- PromptHandler class route các MCP prompt calls
- Xử lý check_lgedv, check_misra, check_certcpp, etc.
- Tự động tạo context cho race condition analysis

### 7. **handlers/resource_handler.py**
- ResourceHandler class cho MCP resources
- Hiện tại: đơn giản (metadata, validation)
- **Future ready**: caching, dynamic loading, permissions, versioning
- Consistent architecture pattern

### 8. **analyzers/race_analyzer.py**
- CppParser class để parse C++ code
- RaceConditionAnalyzer để phát hiện race conditions
- Detailed analysis với scope tracking

### 9. **prompts/prompt_templates.py**
- Tất cả prompt templates tập trung
- Dễ maintain và customize
- Consistent formatting

## 🚀 Cách sử dụng

### Chạy server:
```bash
python -m lgedv.server --transport stdio
```

### Hoặc sử dụng như module:
```python
from lgedv.handlers.tool_handlers import ToolHandler
from lgedv.analyzers.race_analyzer import RaceConditionAnalyzer

# Sử dụng tool handler
tool_handler = ToolHandler()
result = await tool_handler.handle_tool_call("detect_race_conditions", {"dir_path": "/path/to/code"})

# Sử dụng analyzer trực tiếp
analyzer = RaceConditionAnalyzer()
analysis = analyzer.analyze_codebase("/path/to/code")
```

## 📈 Lợi ích của cấu trúc mới

### 1. **Simplified Architecture**
- MCP Resources được xử lý trực tiếp trong config.py (không cần handler riêng)
- Giảm complexity cho static resources
- Focus handlers vào business logic phức tạp

### 2. **Separation of Concerns**
- Mỗi module có responsibility rõ ràng
- Dễ test từng component riêng biệt
- Giảm coupling giữa các parts

### 2. **Maintainability**
- Code dễ đọc và hiểu
- Dễ thêm/sửa/xóa features
- Clear dependencies

### 3. **Reusability**
- Các modules có thể sử dụng độc lập
- Dễ tạo CLI tools hoặc web interfaces
- Plugin architecture

### 4. **Testability**
- Mỗi module có thể unit test riêng
- Mock dependencies dễ dàng
- Integration tests rõ ràng

### 5. **Scalability**
- Dễ thêm analyzers mới
- Dễ thêm rule types mới
- Dễ extend functionality

## 🔄 Migration Completed

✅ **DONE:**
1. ~~**Phase 1**: Sử dụng song song server cũ và mới~~
2. ~~**Phase 2**: Test thoroughly với server mới~~
3. ~~**Phase 3**: Migrate hoàn toàn sang cấu trúc mới~~
4. ~~**Phase 4**: Remove legacy server.py~~

🎯 **Current Status**: **MIGRATION COMPLETE!**
- `server.py` now uses modular architecture
- All legacy code removed
- Clean, maintainable structure in place

## 📝 Todo / Improvements

- [ ] Add comprehensive unit tests
- [ ] Add configuration file support
- [ ] Add more analyzers (memory leaks, performance, etc.)
- [ ] Add web interface
- [ ] Add CLI tool
- [ ] Add plugin system
- [ ] Add caching for analysis results
- [ ] Add parallel processing for large codebases

## 🎯 Future Resource Features (resource_handler.py)

- [ ] **Resource Caching** - Cache metadata và content để tăng performance
- [ ] **Dynamic Loading** - Load resources từ remote URLs, databases
- [ ] **Resource Validation** - Validate integrity, checksums, formats
- [ ] **Access Control** - Permissions và authentication
- [ ] **Versioning** - Track resource versions và updates
- [ ] **Monitoring** - Analytics về resource usage
- [ ] **Compression** - Compress large rule files
- [ ] **Encryption** - Encrypt sensitive resources
