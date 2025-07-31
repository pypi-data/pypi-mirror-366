## Deployment
Rất chi tiết về phương pháp Docker:

---

## 1. Docker Image là gì?

- Docker image là một gói đóng gói toàn bộ ứng dụng, các thư viện phụ thuộc, và cả hệ điều hành nền tảng (Linux base image, ví dụ: Ubuntu, Debian, Alpine...).
- Khi bạn build Docker image cho MCP server, image này sẽ chứa:
  - Một bản Linux tối giản (ví dụ: Ubuntu)
  - Python, các thư viện cần thiết, môi trường ảo, codeguard, v.v.
  - Toàn bộ cấu hình và script khởi động server

---

## 2. Người dùng cần gì để chạy Docker image?

- **Chỉ cần cài Docker** (trên Linux, Windows, hoặc Mac).
- Không cần cài Python, không cần cài thêm thư viện nào khác.
- Không cần quan tâm OS thật là gì, vì mọi thứ chạy trong container Linux.

---

## 3. Cách bạn build Docker image

Ví dụ file `Dockerfile`:
```Dockerfile
FROM ubuntu:22.04

# Cài đặt Python và các công cụ cần thiết
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Copy mã nguồn và môi trường ảo vào image
COPY mcp_server /opt/mcp_server

# (Tùy chọn) Cài đặt thêm các thư viện Python nếu cần
# RUN pip3 install -r /opt/mcp_server/requirements.txt

# Thiết lập thư mục làm việc
WORKDIR /opt/mcp_server

# Lệnh mặc định khi chạy container
ENTRYPOINT ["venv/bin/codeguard", "--transport", "stdio"]
```

Build image:
```bash
docker build -t mcp-server:latest .
```

---

## 4. Người dùng sử dụng Docker image như thế nào?

### a. Trên Linux hoặc Windows (đã cài Docker):

- **Kéo image về (nếu bạn upload lên Docker Hub):**
  ```bash
  docker pull yourdockerhub/mcp-server:latest
  ```
  Hoặc dùng file image bạn gửi:
  ```bash
  docker load -i mcp-server-image.tar
  ```

- **Chạy container:**
  ```bash
  docker run --rm -it \
    -v /path/to/your/project:/workspace \
    -e CPP_DIR=/workspace/code_test/race_condition/test_3 \
    -e CPP_INCLUDE_PATHS=/workspace/code_test/race_condition/test_3/include:/usr/include:/usr/include/c++/13 \
    -e CUSTOM_RULE_PATH=/workspace/copilot_md/Custom.md \
    mcp-server:latest
  ```
  - `-v ...` để mount thư mục mã nguồn của người dùng vào container.
  - `-e ...` để truyền biến môi trường cho MCP server.

- **Trên Windows:**  
  - Cài Docker Desktop, chạy các lệnh tương tự (đường dẫn có thể cần đổi sang dạng Windows hoặc WSL).

---

## 5. Ưu điểm của Docker

- Đảm bảo chạy đồng nhất trên mọi máy (Linux, Windows, Mac).
- Không lo xung đột thư viện, môi trường.
- Dễ dàng cập nhật, phân phối.

---

## 6. Nhược điểm

- Người dùng phải cài Docker (chiếm ~1-2GB).
- Có thể chậm hơn một chút so với chạy native.
- Trên Windows, cần Docker Desktop hoặc WSL2.

---

## 7. Tóm tắt

- Docker image MCP server chứa sẵn Linux, Python, codeguard, mọi thứ cần thiết.
- Người dùng chỉ cần cài Docker, không cần cài gì thêm.
- Chạy được trên Linux, Windows, Mac (qua Docker).
- Chỉ cần mount mã nguồn và truyền biến môi trường khi chạy container.

Nếu bạn cần mẫu Dockerfile hoàn chỉnh, hướng dẫn build/push image, hoặc script chạy mẫu, hãy yêu cầu!


Có, người dùng sử dụng Windows và cài VSCode hoàn toàn có thể truy cập MCP server chạy trong Docker.

### Cách hoạt động:

1. **Cài Docker Desktop trên Windows**  
   - Tải và cài đặt Docker Desktop: https://www.docker.com/products/docker-desktop/
   - Đảm bảo Docker Desktop đang chạy (có thể dùng WSL2 hoặc Hyper-V).

2. **Chạy MCP server trong Docker container**  
   - Người dùng kéo hoặc load Docker image MCP server như hướng dẫn trước.
   - Chạy container, mount thư mục mã nguồn Windows vào container (dùng đường dẫn kiểu Windows hoặc `/mnt/c/...` nếu dùng WSL2).

   Ví dụ:
   ```bash
   docker run --rm -it ^
     -v C:\Users\yourname\project:/workspace ^
     -e CPP_DIR=/workspace/code_test/race_condition/test_3 ^
     -e CPP_INCLUDE_PATHS=/workspace/code_test/race_condition/test_3/include:/usr/include:/usr/include/c++/13 ^
     -e CUSTOM_RULE_PATH=/workspace/copilot_md/Custom.md ^
     mcp-server:latest
   ```
   (Dấu `^` là để xuống dòng trong cmd, nếu dùng PowerShell hoặc Git Bash thì dùng `\`.)

3. **Cấu hình VSCode để kết nối tới MCP server**  
   - Nếu extension MCP hỗ trợ kết nối qua stdio hoặc TCP socket, bạn cấu hình mcp.json để trỏ tới endpoint phù hợp (ví dụ: `localhost:port` nếu server mở cổng).
   - Nếu chỉ dùng stdio, bạn có thể chạy VSCode trong WSL2, hoặc dùng Remote - Containers/WSL extension để VSCode truy cập trực tiếp vào container.

4. **Làm việc bình thường trên Windows**  
   - Mã nguồn vẫn nằm trên Windows, được mount vào container.
   - VSCode có thể truy cập file, gửi lệnh phân tích tới MCP server trong Docker.

---

### Lưu ý

- Nếu dùng stdio, bạn nên chạy VSCode trong WSL2 hoặc Remote Container để VSCode và MCP server cùng môi trường.
- Nếu muốn truy cập qua TCP, bạn cần sửa Dockerfile/entrypoint để MCP server lắng nghe trên cổng mạng (ví dụ: `--transport tcp --port 12345`) và mở port khi chạy container (`-p 12345:12345`).
- Docker trên Windows hiện đại (với WSL2) hỗ trợ rất tốt việc mount file và networking.

---

**Tóm lại:**  
Người dùng Windows + VSCode hoàn toàn dùng được MCP server qua Docker, chỉ cần cài Docker Desktop và mount đúng thư mục mã nguồn. Nếu cần truy cập qua TCP, hãy cấu hình MCP server lắng nghe trên cổng mạng.


Tùy vào đối tượng người dùng và mục tiêu triển khai, bạn nên chọn phương án như sau:

---

## 1. **Cài đặt trực tiếp (native Linux)**
**Nên dùng khi:**
- Người dùng đều sử dụng Linux, quen với dòng lệnh.
- Có thể cài Python, các thư viện phụ thuộc, và không ngại xử lý lỗi môi trường.
- Muốn hiệu năng tối đa, không muốn tốn thêm tài nguyên cho Docker.

**Ưu điểm:**
- Hiệu năng tốt nhất.
- Không cần cài thêm phần mềm nặng (Docker).
- Dễ tích hợp sâu với hệ thống, script, VSCode, v.v.

**Nhược điểm:**
- Dễ gặp lỗi phụ thuộc môi trường (Python, thư viện hệ thống).
- Khó đồng nhất khi triển khai trên nhiều máy khác nhau.

---

## 2. **Sử dụng Docker**
**Nên dùng khi:**
- Người dùng có thể là Linux, Windows, Mac, hoặc môi trường không đồng nhất.
- Muốn đảm bảo "chạy là được", không lo lỗi môi trường, không cần cài Python.
- Muốn đóng gói, phân phối, cập nhật dễ dàng.

**Ưu điểm:**
- Đảm bảo đồng nhất trên mọi máy, mọi OS.
- Không lo xung đột thư viện, môi trường.
- Dễ đóng gói, cập nhật, rollback.
- Người dùng Windows/Mac cũng dùng được.

**Nhược điểm:**
- Cần cài Docker (khá nặng, ~1-2GB).
- Có thể chậm hơn một chút so với native.
- Một số người dùng không quen Docker.

---

## **Khuyến nghị thực tế**

- **Nếu người dùng chủ yếu là developer Linux, thích nhẹ, tối ưu:**  
  → Hướng dẫn cài đặt native (kèm script tự động cài venv, pip install, kiểm tra phụ thuộc).

- **Nếu muốn sản phẩm dễ dùng, ít lỗi, đa nền tảng, hoặc phân phối cho nhiều đối tượng:**  
  → Đóng gói Docker, hướng dẫn chạy container (có thể kèm cả hướng dẫn native cho ai thích).

**Tóm lại:**  
- Đa số dự án hiện đại đều ưu tiên Docker để giảm rủi ro môi trường, nhất là khi phân phối cho nhiều người.
- Nếu bạn kiểm soát được môi trường (nội bộ Linux), native là tối ưu nhất.

Bạn có thể cung cấp cả hai hướng dẫn, nhưng nên ưu tiên Docker nếu muốn "ai cũng chạy được, không lỗi vặt".


Bạn hoàn toàn có thể triển khai MCP server từ xa (remote server) và cho phép người dùng truy cập qua HTTP (hoặc TCP socket). Đây là một hướng đi chuyên nghiệp, phù hợp khi:

- Bạn muốn quản lý, cập nhật, bảo trì server tập trung.
- Người dùng không cần cài đặt nặng nề, chỉ cần gửi request tới server từ xa.
- Dễ mở rộng, tích hợp CI/CD, hoặc phục vụ nhiều người dùng cùng lúc.

---

## Ưu điểm khi triển khai MCP server từ xa qua HTTP

- **Dễ bảo trì, cập nhật:** Chỉ cần update server một nơi, mọi người dùng đều hưởng lợi.
- **Không lo lỗi môi trường trên máy người dùng.**
- **Có thể tích hợp với nhiều công cụ, IDE, CI/CD pipeline.**
- **Dễ kiểm soát bản quyền, truy vết, log, bảo mật.**

---

## Nhược điểm/cân nhắc

- **Yêu cầu mạng ổn định** giữa client và server.
- **Cần bảo mật:** Xác thực, phân quyền, mã hoá nếu dữ liệu nhạy cảm.
- **Độ trễ:** Có thể cao hơn so với chạy local, nhất là với file lớn.
- **Cần phát triển/thêm API HTTP** nếu MCP server hiện tại chỉ hỗ trợ stdio hoặc TCP.

---

## Cách triển khai

1. **Triển khai MCP server trên một máy chủ (Linux hoặc Docker đều được).**
2. **Cấu hình MCP server lắng nghe trên cổng TCP hoặc HTTP** (nếu hỗ trợ).
   - Nếu chưa có HTTP API, bạn có thể phát triển một lớp wrapper (REST API hoặc gRPC) để nhận request từ client, chuyển cho MCP server xử lý, trả kết quả về.
3. **Người dùng cấu hình client/VSCode** để gửi request tới địa chỉ server từ xa (qua HTTP/TCP).
4. **(Tùy chọn) Xây dựng giao diện web hoặc plugin VSCode** để người dùng thao tác dễ dàng.

---

## Khi nào nên dùng?

- Khi số lượng người dùng lớn, phân tán, hoặc không muốn hỗ trợ cài đặt từng máy.
- Khi cần kiểm soát truy cập, log, bảo mật, hoặc tích hợp hệ thống lớn.

---

## Khi nào KHÔNG nên dùng?

- Khi dữ liệu phân tích là mã nguồn nhạy cảm, không muốn gửi ra ngoài.
- Khi người dùng cần hiệu năng tối đa, hoặc không có mạng ổn định.

---

**Tóm lại:**  
Triển khai MCP server từ xa qua HTTP là hướng đi hiện đại, chuyên nghiệp, rất phù hợp cho sản phẩm quy mô lớn hoặc SaaS. Tuy nhiên, cần cân nhắc bảo mật, hiệu năng, và phát triển thêm API nếu cần. Nếu bạn muốn hướng dẫn chi tiết triển khai hoặc thiết kế API, hãy yêu cầu!


Đây là vấn đề quan trọng khi triển khai MCP server từ xa: server cần truy cập mã nguồn nội bộ của user để phân tích, nhưng mã nguồn này thường không được phép gửi ra ngoài vì lý do bảo mật hoặc dung lượng lớn.

### Có 3 giải pháp chính:

---

## 1. **Đồng bộ mã nguồn lên server từ xa**

- **Cách làm:**  
  Người dùng upload (hoặc đồng bộ qua git, rsync, scp, API...) mã nguồn lên server MCP từ xa trước khi phân tích.
- **Ưu điểm:**  
  - Đơn giản, dễ triển khai.
  - Server có toàn bộ context để phân tích.
- **Nhược điểm:**  
  - Rủi ro bảo mật, lộ mã nguồn.
  - Không phù hợp với mã nguồn lớn, nhạy cảm, hoặc thay đổi liên tục.

---

## 2. **Chạy MCP server cục bộ (local) hoặc trong mạng nội bộ**

- **Cách làm:**  
  Đóng gói MCP server (native hoặc Docker) để user chạy trực tiếp trên máy của họ, hoặc trên một server nội bộ (on-premise).
- **Ưu điểm:**  
  - Không cần gửi mã nguồn ra ngoài.
  - Đảm bảo bảo mật tuyệt đối.
- **Nhược điểm:**  
  - Mất lợi thế quản lý tập trung, cập nhật phải làm trên từng máy.

---

## 3. **Thiết kế kiến trúc client-server: client chỉ gửi context cần thiết**

- **Cách làm:**  
  - Viết một client (plugin, script) chạy trên máy user, chỉ gửi những file cần thiết (hoặc trích xuất context, AST, metadata) lên server để phân tích.
  - Có thể nén, mã hoá, hoặc chỉ gửi một phần mã nguồn (ví dụ: file đang mở, hoặc các file liên quan).
- **Ưu điểm:**  
  - Giảm rủi ro lộ mã nguồn toàn bộ.
  - Có thể kiểm soát dữ liệu gửi đi.
- **Nhược điểm:**  
  - Cần phát triển thêm client.
  - Một số phân tích sâu vẫn cần nhiều context.

---

## 4. **Kết hợp: phân tích cục bộ, tổng hợp từ xa**

- **Cách làm:**  
  - Phần phân tích cần truy cập mã nguồn chạy local (hoặc trong mạng nội bộ).
  - Kết quả, log, hoặc các chỉ số tổng hợp mới gửi lên server từ xa để tổng hợp, hiển thị, hoặc lưu trữ.

---

### **Khuyến nghị thực tế**

- Nếu bảo mật là ưu tiên: **Nên chạy MCP server local hoặc on-premise**.
- Nếu bắt buộc phải dùng server từ xa: **Phải có cơ chế mã hoá, kiểm soát dữ liệu gửi đi, hoặc chỉ gửi context tối thiểu**.
- Nếu muốn linh hoạt: **Phát triển client thông minh để chỉ gửi phần cần thiết, hoặc cho phép user chọn file gửi đi**.

---

**Tóm lại:**  
Không nên gửi toàn bộ mã nguồn nội bộ ra ngoài nếu không kiểm soát được bảo mật. Hãy cân nhắc giải pháp hybrid (phân tích local, tổng hợp từ xa) hoặc phát triển client chỉ gửi context cần thiết. Nếu cần mẫu kiến trúc hoặc giải pháp kỹ thuật chi tiết, hãy yêu cầu!


Nếu MCP server và máy local của bạn đều nằm trong mạng nội bộ công ty, bạn hoàn toàn có thể triển khai MCP server từ xa và cho phép các máy client truy cập trực tiếp vào mã nguồn nội bộ để phân tích mà không phải lo lắng về bảo mật.

### Cách triển khai tối ưu trong mạng nội bộ:

1. **Đặt MCP server trên một máy chủ nội bộ (Linux hoặc Docker đều được).**
2. **Chia sẻ thư mục mã nguồn qua mạng nội bộ:**
   - Sử dụng NFS, Samba, hoặc mount ổ đĩa mạng để MCP server có thể truy cập trực tiếp vào thư mục mã nguồn của từng user (hoặc các dự án cần phân tích).
   - Hoặc, user có thể upload mã nguồn lên một thư mục chung trên server qua scp/rsync.

3. **Cấu hình MCP server:**
   - Đặt biến môi trường `CPP_DIR`, `CPP_INCLUDE_PATHS`, ... trỏ tới thư mục mã nguồn đã mount hoặc upload.
   - Có thể cấu hình động qua API hoặc giao diện web nếu muốn tiện lợi hơn.

4. **Client (user) thao tác:**
   - Sử dụng VSCode, plugin, hoặc script để gửi yêu cầu phân tích tới MCP server (qua HTTP/TCP hoặc stdio nếu dùng remote extension).
   - Nhận kết quả trả về và hiển thị trực tiếp trên máy local.

---

### Ưu điểm của mô hình này

- **Không lo bảo mật:** Dữ liệu không rời khỏi mạng nội bộ.
- **Dễ quản lý, bảo trì:** Chỉ cần update server một nơi.
- **Hiệu năng tốt:** Tốc độ truyền tải trong LAN rất nhanh, phù hợp cả với dự án lớn.
- **Dễ tích hợp:** Có thể tích hợp với các hệ thống CI/CD, quản lý mã nguồn nội bộ.

---

### Gợi ý thực tế

- Nếu có thể, nên dùng NFS hoặc Samba để mount thư mục mã nguồn từ máy user lên server, giúp MCP server luôn truy cập được mã nguồn mới nhất.
- Nếu không, user chỉ cần upload mã nguồn lên server mỗi lần cần phân tích.
- Có thể phát triển thêm giao diện web hoặc API để user chọn thư mục, submit job, và nhận kết quả dễ dàng.

---

**Tóm lại:**  
Bạn hoàn toàn nên triển khai MCP server từ xa trong mạng nội bộ công ty, cho phép truy cập trực tiếp mã nguồn để phân tích. Đây là mô hình tối ưu cho doanh nghiệp, vừa an toàn, vừa tiện lợi, vừa dễ mở rộng!