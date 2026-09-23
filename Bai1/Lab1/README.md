# SecureValidator Lab

Bài thực hành môn Lập trình An toàn — kiểm tra đầu vào (input validation).
Ứng dụng Flask minh hoạ các bộ lọc: email, URL, filename, SQL, HTML.

## Chạy

```bash
pip install -r requirements.txt
python app.py            # mở http://127.0.0.1:5000
python -m unittest discover -s tests
python bypass_demo.py    # demo điểm yếu của bộ lọc
```

Route phụ `/context-demo` minh hoạ **XSS theo ngữ cảnh**: vẫn dùng đúng
`sanitize_html_input` (`html.escape`, core không đổi) nhưng đặt output vào thuộc
tính `href`. Payload `javascript:alert(1)` không chứa `< > & " '` nên escape để
nguyên → bấm link là chạy mã. Bản vá: kiểm tra scheme bằng `validate_url` trước
khi dùng cho `href`.

## Vì sao có `bypass_demo.py`

Đây là phần phân tích **defensive**: chứng minh rằng lọc kiểu **blocklist**
(chặn ký tự / từ khoá "xấu") về bản chất không đủ an toàn, và chỉ ra hướng sửa
đúng. `bypass_demo.py` chạy trực tiếp các hàm trong `securevalidator/core.py`
với một số chuỗi input soạn sẵn để quan sát chuỗi nào lọt qua — **không thay
đổi cấu trúc code của lab**, chỉ thay đổi input.

Kết quả thực tế quan sát được:

| Bộ lọc | Input | Kết quả | Vì sao lọt / vấn đề |
|---|---|---|---|
| `sanitize_sql_input` | `' OR 1=1 --` | `1=1` | Xoá `'`, `OR`, `--` nhưng vẫn để lại tautology `1=1` |
| `sanitize_sql_input` | `'\|\|1=1` | `\|\|1=1` | `\|\|` là toán tử OR trong SQL, không có trong blocklist |
| `sanitize_sql_input` | `admin'/**/=/**/'admin` | `admin/**/=/**/admin` | Comment `/**/` không bị lọc |
| `validate_url` | `http://127.0.0.1/...` | `True` | Chỉ kiểm tra scheme + netloc, **không** chặn nội bộ |
| `validate_url` | `http://169.254.169.254/...` | `True` | Endpoint metadata cloud vẫn qua → SSRF thật sự |
| `validate_filename` | `%2e%2e%2fetc%2fpasswd` | `True` | Dạng URL-encoded của `../`; nguy hiểm nếu decode ở bước sau |
| `validate_email` | `a@b.c` | `True` | Regex nhận cả địa chỉ gần như vô nghĩa |
| `sanitize_html_input` | `javascript:alert(1)` | không đổi | `html.escape` không thêm ký tự đặc biệt → nguy hiểm trong `href`/attribute |

## Nguyên nhân gốc và cách sửa đúng

- **SQL** — Không bao giờ "làm sạch" chuỗi rồi ghép vào câu SQL. Blocklist luôn
  có thể bị lách (tautology, toán tử thay thế, comment). Dùng **parameterized
  query / prepared statement** (`cursor.execute(sql, params)`), để driver tách
  dữ liệu khỏi mã lệnh.
- **URL / SSRF** — Comment code ghi "prevent SSRF" nhưng chỉ kiểm tra scheme.
  Cần **allowlist** host được phép, và chặn IP nội bộ/loopback/link-local
  (`127.0.0.0/8`, `169.254.0.0/16`, `10/8`, `192.168/16`, `::1`) sau khi phân
  giải DNS.
- **Filename** — Kiểm tra sau khi **decode** và **normalize** đường dẫn, hoặc
  tốt hơn là dùng allowlist ký tự (`^[A-Za-z0-9._-]+$`) thay vì blocklist.
- **Email** — Regex vừa quá lỏng vừa quá chặt. Ưu tiên thư viện chuẩn
  (vd `email-validator`) và xác thực bằng email gửi thật.
- **HTML / XSS** — `html.escape` đúng cho **nội dung phần tử**, nhưng escaping
  phải theo **ngữ cảnh** (thuộc tính, URL trong `href`, khối `<script>`). Dùng
  hệ thống template tự động escape theo ngữ cảnh và chặn scheme `javascript:`.
