# SecureLogger Lab

## Chạy / kiểm tra

```bash
cd secure_logger_lab
pip install -r requirements.txt
python app.py                # http://127.0.0.1:5000
```

Dùng Postman (hoặc curl) gửi `POST /validate` với body JSON:

```json
{
  "email": "phuoc@example.com",
  "url": "https://secure.com",
  "filename": "report.pdf",
  "sql": "' OR 1=1 --",
  "html": "<script>alert(1)</script>"
}
```

Kiểm tra kết quả:

- `secure.log` — log dạng JSON, trường `email` trong `data`/`results` đã bị che thành `<email_masked>`.
- `secure.log.sig` — chuỗi hash SHA-256 tương ứng từng dòng log, dùng xác thực log không bị chỉnh sửa.

## Bypass PII masking & tamper detection
`red_bypass.py` import trực tiếp `mask_pii()` / `hash_line()` từ `securelogger/logger.py`
(không copy/sửa code) và các hàm validate/sanitize từ `securevalidator/core.py`,
feed input được soạn để chứng minh 4 lỗ hổng thật:

```bash
cd Lab3                # chạy từ đây, NGOÀI secure_logger_lab/
python red_bypass.py
```

### 1. `password`/`token`/`apikey`/`key` KHÔNG BAO GIỜ bị che khi log qua `data`/`results`

`TOKEN_PATTERN` yêu cầu literal dấu `=` ngay sau keyword:

```
r'(?i)(token|apikey|key|password)\s*=\s*["\']?[\w\-]{8,}["\']?'
```

Nhưng `app.py` log nguyên `data`/`results` bằng `str(dict)`, và cú pháp dict
của Python luôn là `{'key': 'value'}` — **dấu hai chấm**, không phải dấu bằng.
Chỉ cần gửi thêm 1 field lạ (vd `"password": "hunter123456"`) trong body JSON
gửi tới `/validate` — field đó lọt vào `data` và bị log **y nguyên**, không hề
bị `mask_pii()` che, vì regex không bao giờ khớp cú pháp `'key': 'value'`.
Đã verify thực tế: `masked` vẫn chứa chuỗi `hunter123456` sau khi qua `mask_pii()`.

### 2. Email dạng `+alias` chỉ bị che một phần, lộ danh tính thật

`EMAIL_PATTERN` dùng `\w` cho phần local-part, mà `\w` không gồm ký tự `+`.
`vice.director+leak@example.com` → chỉ đoạn `leak@example.com` bị thay
`<email_masked>`, còn `vice.director` (danh tính thật đứng trước `+`) thì lộ
nguyên trong log.

### 3. `secure.log.sig` không chống giả mạo — chỉ là SHA-256 không khoá

`append_signature()` gọi thẳng `hashlib.sha256(line)`, **không phải**
`hmac.new(secret_key, line, sha256)`. Nghĩa là "chữ ký" chỉ là hash công khai:
ai đọc được source (ai cũng đọc được, nó nằm trong repo) đều tự tính lại được
hash cho bất kỳ nội dung nào họ muốn. Demo: sửa `results` trong 1 dòng log để
xoá bằng chứng SQL injection lọt qua, rồi tự tính lại `hash_line()` cho dòng
đã sửa — chữ ký giả sinh ra đúng định dạng 64 ký tự hex y hệt chữ ký thật,
không có cách nào phân biệt dòng nào bị sửa nếu chỉ dựa vào `secure.log.sig`.

### 4. Kế thừa toàn bộ điểm yếu của SecureValidator (Lab1)

Vì `securevalidator/core.py` trong Lab3 là bản copy y hệt Lab1 (theo đúng yêu
cầu sách), mọi bypass đã chứng minh ở `Bai1/Lab1/README.md` (SQL tautology,
SSRF qua `169.254.169.254`, path traversal URL-encoded, XSS qua
`javascript:` scheme...) vẫn áp dụng nguyên vẹn qua route `POST /validate`.

### Nguyên nhân gốc và cách sửa đúng

- **PII masking theo regex `key=value`** không khớp với định dạng thật của dữ
  liệu được log (`str(dict)` dùng dấu hai chấm). Cách sửa đúng: không log
  `str(dict)` thô — duyệt đệ quy từng key/value của dict, so khớp **tên key**
  (`key.lower() in {"password", "token", ...}`) để quyết định che, thay vì
  chạy regex trên toàn bộ chuỗi đã serialize.
- **Email regex thiếu `+`** trong local-part — nên dùng thư viện chuẩn
  (`email-validator`) hoặc mở rộng charset đúng theo RFC 5322 thay vì regex
  viết tay.
- **Tamper detection cần khoá bí mật (HMAC) không lưu chung ổ đĩa với log**,
  lý tưởng là khoá do KMS/HSM quản lý hoặc ký bằng khoá private lưu tách biệt
  — nếu không, "chữ ký" chỉ chứng minh được tính toàn vẹn ngẫu nhiên (phát
  hiện lỗi đĩa/truyền tải), hoàn toàn không chống được kẻ tấn công chủ đích.
