# Bài 1: Lập trình an toàn

Gồm 3 lab, mỗi lab có README riêng ghi chi tiết cách chạy và phần phân tích
điểm yếu (bypass):

| Thư mục | Nội dung | Chi tiết |
|---|---|---|
| `Lab1/` | **SecureValidator** — ứng dụng Flask minh hoạ các bộ lọc đầu vào: email, URL, filename, SQL, HTML; kèm demo XSS theo ngữ cảnh | [Lab1/README.md](Lab1/README.md) |
| `Lab2/` | **GitSecure** — pre-commit hook chặn commit chứa thông tin nhạy cảm (secret, world-writable, bandit) | [Lab2/README.md](Lab2/README.md) |
| `Lab3/` | **SecureLogger** — ghi log dạng JSON, che PII (email), ký từng dòng log để phát hiện chỉnh sửa | [Lab3/README.md](Lab3/README.md) |

Môi trường chạy: Windows 11, Python 3.14. Có thể dùng chung venv `.venv` ở thư mục
gốc repo, hoặc tạo venv riêng trong từng lab.

Mỗi lab đều kèm một phần **phân tích defensive**: chứng minh rằng lọc kiểu
**blocklist** (chặn ký tự / từ khoá / tên biến "xấu") về bản chất không đủ an
toàn, bằng cách import trực tiếp hàm của lab rồi feed input soạn sẵn — **không
sửa cấu trúc code của lab**, chỉ thay đổi input — và chỉ ra hướng sửa đúng.

---

## 1. Lab1 — SecureValidator

```
Lab1/
├── secure-validator-lab/
│   ├── app.py                     # Flask: trang nhập liệu + route /context-demo (XSS theo ngữ cảnh)
│   ├── securevalidator/
│   │   ├── __init__.py
│   │   └── core.py                # validate_email/url/filename, sanitize_sql/html_input
│   ├── templates/                 # index.html, context_demo.html
│   ├── tests/test_validators.py   # unittest
│   ├── requirements.txt
│   ├── render.yaml                # cấu hình deploy (Render)
│   └── .gitignore
├── bypass_demo.py                 # chạy các hàm core với input né blocklist
└── README.md
```

### Chạy

```powershell
cd Bai1\Lab1\secure-validator-lab
pip install -r requirements.txt
python app.py                           # http://127.0.0.1:5000
python -m unittest discover -s tests
cd ..                                   # về Lab1
python bypass_demo.py                   # demo điểm yếu của bộ lọc
```

Điểm chính: lọc blocklist cho SQL vẫn để lọt tautology `1=1`, toán tử `||`,
comment `/**/`; `validate_url` không chặn IP nội bộ/metadata cloud (SSRF);
`html.escape` đúng cho nội dung phần tử nhưng không an toàn trong `href`
(`javascript:` scheme). Chi tiết và cách sửa: [Lab1/README.md](Lab1/README.md).

---

## 2. Lab2 — GitSecure

```
Lab2/
├── gitsecure-lab/
│   ├── .githooks/pre-commit           # scan_sensitive, check_permissions, run_bandit
│   ├── pre-commit-hook-test/bad.py    # file test có password hardcode
│   ├── requirements.txt
│   └── .gitignore
├── red_bypass.py                      # dựng repo Git tạm, chứng minh secret lọt qua end-to-end
└── README.md
```

### Chạy / kiểm tra

```powershell
cd Bai1\Lab2\gitsecure-lab
pip install -r requirements.txt
git init
git config core.hooksPath .githooks
# Cấp quyền thực thi cho hook qua Git Bash: chmod +x .githooks/pre-commit
git add pre-commit-hook-test\bad.py
git commit -m "test"                   # bị chặn: COMMIT BLOCKED by GitSecure

cd ..                                  # về Lab2, NGOÀI gitsecure-lab/
python red_bypass.py
```

Điểm chính: regex theo *tên biến cố định* bị lách bằng đổi tên biến, chèn hậu tố,
nối chuỗi, triple-quote, base64; `check_permissions()` trả `False` sẵn trên
Windows; `run_bandit()` so khớp `"SEVERITY: High"` sai case nên không bao giờ
bắt được lỗi. Chi tiết và cách sửa: [Lab2/README.md](Lab2/README.md).

---

## 3. Lab3 — SecureLogger

```
Lab3/
├── secure_logger_lab/
│   ├── app.py                         # Flask: POST /validate -> validate + ghi log
│   ├── securelogger/
│   │   ├── __init__.py
│   │   └── logger.py                  # mask_pii, hash_line, append_signature
│   ├── securevalidator/               # bản copy core.py của Lab1 (theo yêu cầu sách)
│   │   ├── __init__.py
│   │   └── core.py
│   └── requirements.txt
├── red_bypass.py                      # chứng minh 4 lỗ hổng: PII, email +alias, chữ ký, kế thừa Lab1
└── README.md
```

> `secure.log` / `secure.log.sig` là file log sinh ra khi chạy, không thuộc source.

### Chạy / kiểm tra

```powershell
cd Bai1\Lab3\secure_logger_lab
pip install -r requirements.txt
python app.py                          # http://127.0.0.1:5000
# Dùng Postman/curl gửi POST /validate với body JSON (xem README con)

cd ..                                  # về Lab3, NGOÀI secure_logger_lab/
python red_bypass.py
```

Điểm chính: `mask_pii()` dùng regex `key=value` nên không che được dict log dạng
`'key': 'value'`; email `+alias` chỉ bị che một phần, lộ danh tính thật;
`secure.log.sig` chỉ là SHA-256 không khoá (không phải HMAC) nên không chống giả
mạo có chủ đích; và kế thừa toàn bộ điểm yếu của SecureValidator (Lab1). Chi tiết
và cách sửa: [Lab3/README.md](Lab3/README.md).

---

> Toàn bộ nội dung mang tính giáo dục trên môi trường lab. Các phần "bypass" chỉ
> import và chạy lại chính hàm của lab với input soạn sẵn để phân tích điểm yếu,
> không thay đổi cấu trúc code, và luôn kèm hướng khắc phục.
