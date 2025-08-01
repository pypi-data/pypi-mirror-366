# MCP server

A simple MCP server by taikt

## Usage

## Todo
execute server tu dong tu vscode extension
https://code.visualstudio.com/api/extension-guides/mcp

# install clang
wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh 
sudo ./llvm.sh 20
sudo apt-get install libclang-20-dev clang-20
ls /usr/lib/llvm-20/lib/libclang.so

source venv/bin/activate
pip install clang (pip uninstall clang)

# work flow
Có! Để biết biến nào bị truy cập bởi nhiều thread, bạn cần:

1. **Phân tích call graph**: Xác định các hàm được gọi trong từng thread entry function.
2. **Ghi nhận truy cập biến**: Với mỗi hàm, phân tích các truy cập tới biến thành viên (member variable) hoặc biến toàn cục.
3. **Gắn thread context**: Đánh dấu mỗi truy cập biến là thuộc context nào (main hoặc thread).
4. **Gom nhóm theo biến**: Sau khi phân tích, gom nhóm các truy cập theo biến. Nếu một biến bị truy cập ở cả context main và thread (hoặc nhiều thread), đó là biến nghi ngờ bị race condition.

Pipeline hiện tại đã có logic này, nhưng cần đảm bảo:
- Metadata truy cập biến phải ghi rõ tên biến, class, file, và thread_context.
- Phân tích text hoặc AST phải đủ chính xác để không bỏ sót truy cập.

Tóm lại: Cần metadata chi tiết về mọi truy cập biến, gắn thread_context, rồi kiểm tra biến nào xuất hiện ở nhiều thread. Đây là cách chuẩn để phát hiện biến nghi ngờ bị race condition.

# how pro-tool doing
Các công cụ phân tích tĩnh chuyên nghiệp (như Coverity, Clang Static Analyzer, CodeSonar, Infer, ThreadSanitizer) thường giải quyết bước 2 bằng các kỹ thuật sau:

1. **Phân tích AST nâng cao**: Sử dụng AST chi tiết để nhận diện mọi truy cập biến, kể cả các phép toán như `value++`, `this->value++`, `value = ...`, kể cả qua con trỏ hoặc tham chiếu.

2. **Phân tích IR/SSA**: Chuyển mã nguồn sang Intermediate Representation (IR) hoặc Static Single Assignment (SSA) để dễ dàng theo dõi mọi truy cập và thay đổi biến trong toàn bộ chương trình.

3. **Dataflow Analysis**: Theo dõi luồng dữ liệu (dataflow) để xác định biến nào bị truy cập ở đâu, bởi hàm nào, trong context nào (thread/main).

4. **Symbolic Execution**: Mô phỏng luồng thực thi của chương trình để phát hiện mọi trường hợp truy cập biến, kể cả các nhánh điều kiện phức tạp.

5. **Thread/Concurrency Modeling**: Xây dựng mô hình các luồng (thread) và các điểm đồng bộ hóa (mutex, atomic, lock) để xác định biến nào bị truy cập đồng thời mà không có bảo vệ.

6. **Kết hợp phân tích text và AST**: Nếu AST không đủ, sẽ kết hợp với phân tích text, nhưng luôn ưu tiên AST/IR để đảm bảo độ chính xác.

Tóm lại: Công cụ chuyên nghiệp dùng AST/IR/dataflow/symbolic execution để ghi nhận mọi truy cập biến, không chỉ dựa vào regex text. Điều này giúp phát hiện đầy đủ và chính xác các biến bị truy cập bởi nhiều thread.

Giải pháp tổng quát để phân tích multi-thread functions và call graph trong nhiều dự án C++ với cấu trúc khác nhau:

### 1. **Tách biệt code user và code hệ thống**
- Chỉ thu thập các node thuộc file user (so sánh path với danh sách file dự án).
- Không duyệt node thuộc system headers để tránh log rác và tăng tốc.

### 2. **Thu thập hàm user định nghĩa**
- Duyệt đệ quy AST, thu thập tất cả các `FUNCTION_DECL` thuộc file user.
- Đối với hàm thành viên class, tạo key dạng `ClassName::FunctionName`.
- Đối với hàm global, dùng tên hàm.

### 3. **Xác định entrypoint và trace call graph**
- Xác định các hàm được dùng làm entrypoint cho thread (hàm truyền vào `std::thread`, `pthread_create`, v.v.).
- Trace call graph từ các entrypoint, ghi nhận tất cả hàm được gọi trực tiếp/gián tiếp trong ngữ cảnh thread.

### 4. **Xử lý các trường hợp đặc biệt**
- **Lambda:** AST không nhận diện lambda là hàm user định nghĩa, nên không trace được call graph. Giải pháp: Nếu dự án dùng lambda cho thread, cần có logic nhận diện và phân tích lambda (phức tạp, nhiều giới hạn).
- **Template, Inline, Macro:** Một số hàm template, inline, macro có thể bị Clang bỏ qua nếu không parse đúng context. Giải pháp: Cần biên dịch với compile flags đầy đủ, hoặc parse theo project thực tế (dùng compile_commands.json).
- **Dự án lớn, nhiều file:** Nên parse theo từng file hoặc theo project, không parse toàn bộ workspace một lần.

### 5. **Limitation của phương pháp hiện tại**
- **Clang AST chỉ nhận diện hàm khi parse đúng context:** Nếu không biên dịch như project thực tế, nhiều hàm sẽ bị bỏ qua.
- **Không trace được lambda, macro, template phức tạp.**
- **Không nhận diện các hàm được gọi qua function pointer, std::function, hoặc callback phức tạp.**
- **Không phân biệt được các hàm overload, hàm cùng tên ở nhiều class nếu không có đủ thông tin context.**

### 6. **Giải pháp nâng cao**
- Sử dụng compile_commands.json để parse đúng context từng file như khi biên dịch thực tế.
- Kết hợp với các công cụ phân tích tĩnh khác (CodeQL, Cppcheck, Clang Static Analyzer) để bổ sung thông tin.
- Nếu cần trace lambda, macro, template, phải viết thêm logic nhận diện AST node đặc biệt hoặc dùng các tool chuyên biệt.

---

**Tóm lại:**  
Phương pháp hiện tại phù hợp với các dự án C++ có cấu trúc rõ ràng, hàm thread entrypoint là hàm user định nghĩa, không dùng lambda/macro phức tạp. Nếu dự án dùng nhiều lambda, macro, template, hoặc có cấu trúc lớn, cần bổ sung logic nhận diện đặc biệt hoặc dùng compile_commands.json để parse đúng context.


Đúng, với dự án C++ phức tạp sử dụng lambda, macro, template, function pointer, hoặc callback, phương pháp phân tích dựa trên Clang AST và thu thập hàm entrypoint như hiện tại sẽ không đủ chính xác.

### Các phương pháp giải quyết trường hợp phức tạp:

#### 1. **Sử dụng compile_commands.json và Clang Tooling**
- Parse code theo đúng context biên dịch thực tế (đầy đủ flags, macro, include path).
- Dùng Clang Tooling (libTooling, clang-query, clang-tidy) để phân tích sâu hơn, có thể nhận diện lambda, template, macro, function pointer.

#### 2. **Kết hợp với CodeQL hoặc các công cụ phân tích tĩnh nâng cao**
- CodeQL có thể truy vết call graph, data flow, và nhận diện các hàm được gọi qua lambda, macro, template, function pointer.
- Có thể viết truy vấn để tìm các điểm truy cập biến trong nhiều luồng, kể cả qua callback/lambda.

#### 3. **Sử dụng Clang Static Analyzer hoặc Cppcheck**
- Các tool này có thể phân tích data flow, control flow, và nhận diện các vấn đề concurrency, kể cả khi dùng lambda, macro, template.

#### 4. **Kết hợp nhiều phương pháp**
- Dùng Clang AST để thu thập hàm cơ bản.
- Dùng CodeQL hoặc Cppcheck để phân tích sâu các trường hợp đặc biệt.
- Dùng compile_commands.json để parse đúng context từng file.

#### 5. **Phân tích runtime (dynamic analysis)**
- Dùng các tool như ThreadSanitizer, Helgrind, hoặc các framework kiểm tra concurrency khi chạy thực tế để phát hiện race condition mà static analysis không nhận diện được.

---

**Tóm lại:**  
- Để phân tích chính xác các dự án phức tạp, nên kết hợp Clang Tooling (với compile_commands.json), CodeQL, Cppcheck, và các tool runtime như ThreadSanitizer.
- Không có một phương pháp duy nhất nào giải quyết hoàn toàn mọi trường hợp phức tạp của C++.
- Nên dùng nhiều lớp phân tích (static + dynamic) và parse code theo đúng context biên dịch thực tế.

Nếu bạn muốn hướng dẫn cụ thể về CodeQL, compile_commands.json, hoặc các tool runtime, hãy yêu cầu chi tiết!

Clang Static Analyzer **không trực tiếp xuất ra danh sách các hàm chạy trong ngữ cảnh multi-thread**. Công cụ này chủ yếu phát hiện các lỗi như race condition, deadlock, memory leak, nhưng không liệt kê call graph hoặc các hàm được thực thi bởi nhiều thread.

**Giải thích chi tiết:**
- Clang Static Analyzer sẽ báo lỗi khi phát hiện truy cập biến không đồng bộ giữa các thread, nhưng không xuất ra danh sách hàm nào bị ảnh hưởng hoặc hàm nào là entrypoint của thread.
- Nếu bạn muốn lấy danh sách các hàm chạy trong ngữ cảnh multi-thread, bạn cần dùng Clang AST, CodeQL, hoặc các tool phân tích call graph chuyên biệt (hoặc tự viết script phân tích AST).

**Tóm lại:**  
- Clang Static Analyzer giúp phát hiện lỗi concurrency, nhưng không xuất ra danh sách hàm multi-thread.
- Nếu cần danh sách hàm, hãy dùng Clang AST, CodeQL, hoặc các tool call graph khác.

Nếu bạn muốn hướng dẫn dùng CodeQL hoặc Clang AST để lấy danh sách hàm multi-thread, tôi có thể hỗ trợ chi tiết!

Đúng, Clang AST như cách bạn đang implement **không xử lý triệt để cho code phức tạp dùng lambda, macro, template, function pointer, hoặc callback**.

**Lý do:**
- Lambda trong C++ được Clang AST nhận diện là một kiểu node đặc biệt (LambdaExpr), không phải FUNCTION_DECL, nên không dễ truy vết như hàm thường.
- Nếu thread entrypoint là lambda, bạn sẽ không có tên hàm cụ thể để trace call graph, và không thể xác định rõ các hàm bị ảnh hưởng trong multi-thread context.
- Macro, template, function pointer, callback cũng khó trace vì Clang AST chỉ phân tích cú pháp, không phân tích luồng thực thi động hoặc các trường hợp phức tạp.

**Kết luận:**  
- Clang AST chỉ phù hợp cho code C++ có cấu trúc rõ ràng, hàm entrypoint là hàm user định nghĩa.
- Với code phức tạp dùng lambda, macro, template, function pointer, bạn cần kết hợp thêm các tool khác (CodeQL, static analyzer nâng cao, hoặc dynamic analysis).

Nếu bạn muốn phân tích sâu lambda, cần viết logic nhận diện LambdaExpr và phân tích body của lambda, nhưng vẫn có nhiều giới hạn và không thể trace call graph như hàm thường.

# callstack
Có hai cách để phân tích call stack:

1. **Phân tích tĩnh (static analysis)**  
   - Dùng AST để xây dựng call graph: xác định hàm nào gọi hàm nào, từ đó biết luồng thực thi tiềm năng.
   - Không cần chạy chương trình, nhưng không thể biết chính xác call stack thực tế nếu có các nhánh động, virtual, function pointer, v.v.

2. **Phân tích động (dynamic analysis)**  
   - Build và chạy chương trình, dùng các công cụ như gdb, lldb, Valgrind, ThreadSanitizer, hoặc thêm mã log để ghi lại call stack khi chương trình thực thi.
   - Có thể dùng macro hoặc hook để in call stack tại các điểm truy cập biến nghi ngờ.
   - Kết quả phản ánh đúng call stack thực tế, nhưng chỉ cho các trường hợp đã chạy qua.

Nếu muốn lấy call stack thực tế:
- Build chương trình với debug symbols (`-g`).
- Chạy với gdb/lldb, đặt breakpoint tại hàm hoặc biến nghi ngờ, dùng lệnh `bt` (backtrace) để lấy call stack.
- Hoặc dùng ThreadSanitizer (`-fsanitize=thread`) để tự động phát hiện race và in call stack khi phát hiện lỗi.

Tóm lại:  
- Phân tích tĩnh chỉ cho call graph tiềm năng.  
- Phân tích động (build và chạy) mới lấy được call stack thực tế tại thời điểm truy cập biến.  
Bạn muốn hướng dẫn chi tiết cách lấy call stack bằng gdb/lldb hoặc ThreadSanitizer không?


## Example

cd /home/worker/src/codefun/deepl/mcp_server
### tao moi truong ao 1 lan dau
rm -rf venv
sudo apt install python3.12-venv
python3 -m venv venv 

### kich hoat moi truong ao neu mo new terminal
source venv/bin/activate 

### luon cai lai khi thay doi server code
pip install -e .

## run server
start server trong mcp.json
mo copilot chat cua so moi (copilot tu dong ket noi server)
go: fetch_lgedv_rule

## xem log
cat /tmp/mcp_simple_prompt.log

## upload package
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

## user install
python3 -m venv venv
source venv/bin/activate
pip install codeguard-taikt

## user setup mcp.json
"servers": {
  "codeguard": {
    "command": "/duong_dan_toi_venv/bin/codeguard",
    "args": ["--transport", "stdio"]
  }
}

## When use MCP resource
dung khi co file markdown, vi cau truc don gian, tham khao cach lay lgedv rule(markdown) bang mcp resource trong code hien tai 
Neu lay resouce la cpp file, no khong co cau truc nen AI agent kho hieu, khong the parse
metadata type.

## note
Có, rất cần thiết phải có file __init__.py trong thư mục package (ví dụ: mcp_server/) nếu bạn muốn Python nhận diện đó là một package hợp lệ để import (ví dụ: import mcp_server.server). File này có thể rỗng, chỉ cần tồn tại.

File __main__.py không bắt buộc, trừ khi bạn muốn chạy package đó như một module (python -m mcp_server). Đối với trường hợp sử dụng entry point script như mcp-taikt = "mcp_server.server:main", bạn không cần __main__.py, chỉ cần __init__.py là đủ.

Tóm lại:
- __init__.py: Bắt buộc để Python nhận diện package.
- __main__.py: Chỉ cần nếu muốn chạy python -m <package>. Không bắt buộc cho entry point script.

