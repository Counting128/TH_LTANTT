# Thực hành Lập trình An ninh thông tin (TH_LTANTT)

Bài thực hành môn Lập trình An ninh thông tin. Mỗi bài có README riêng ghi cách
chạy, ảnh kết quả và các điểm khác với giáo trình.

| Bài | Nội dung | Chi tiết |
|---|---|---|
| Bài 1 | Lập trình an toàn | [Bai1/README.md](Bai1/README.md) |
| Bài 2 | Mã hoá, triển khai PKI | [Bai2/README.md](Bai2/README.md) |
| Bài 3 | Bảo mật mạng máy tính | [Bai3/README.md](Bai3/README.md) |
| Bài 4 | Bảo mật Web App và API | [Bai4/README.md](Bai4/README.md) |
| Bài 5 | Phân tích và Kiểm thử Bảo mật (SAST & DAST) | [Bai5/README.md](Bai5/README.md) |

## Bài 1: Lập trình an toàn

| Lab | Nội dung | README |
|---|---|---|
| Lab1 | SecureValidator: ứng dụng Flask kiểm tra đầu vào (email, URL, filename, SQL, HTML) | [Bai1/Lab1/README.md](Bai1/Lab1/README.md) |
| Lab2 | GitSecure: pre-commit hook chặn commit chứa thông tin nhạy cảm | [Bai1/Lab2/README.md](Bai1/Lab2/README.md) |
| Lab3 | SecureLogger: ghi log an toàn, che dữ liệu nhạy cảm, phát hiện sửa log | [Bai1/Lab3/README.md](Bai1/Lab3/README.md) |

## Bài 2: Mã hoá, triển khai PKI

| Phần | Nội dung |
|---|---|
| [Bai2/crypto-toolkit/](Bai2/crypto-toolkit/) | Thư viện `securecrypto`: AES-256-GCM, RSA, Argon2; kèm CLI, GUI và Flask API |
| [Bai2/mini-ca/](Bai2/mini-ca/) | CA đơn giản: Root CA, Intermediate CA, cấp chứng chỉ, xác thực chuỗi, thu hồi (CRL) |
| [Bai2/screenshots/](Bai2/screenshots/) | Ảnh kết quả chạy |

## Bài 3: Bảo mật mạng máy tính

| Phần | Nội dung |
|---|---|
| [Bai3/secure-chat/](Bai3/secure-chat/) | Chat qua SSL/TLS (mTLS), mã hoá đầu-cuối AES-256, quản lý kết nối và phòng chat |
| [Bai3/netrecon/](Bai3/netrecon/) | Trinh sát mạng: quét cổng, nhận dạng dịch vụ, banner, ARP, tra CVE; có CLI, web Flask, gửi email |
| [Bai3/screenshots/](Bai3/screenshots/) | Ảnh kết quả chạy |

## Bài 4: Bảo mật Web App và API

| Phần | Nội dung |
|---|---|
| [Bai4/web-vuln-scanner/](Bai4/web-vuln-scanner/) | Quét lỗ hổng web: XSS, SQL Injection, CSRF, SSRF; có báo cáo, web Flask và unittest |
| [Bai4/jwt-security-tools/](Bai4/jwt-security-tools/) | Bảo mật JWT: validator, cracker, OAuth client, token manager, API gateway; có pytest |
| [Bai4/screenshots/](Bai4/screenshots/) | Ảnh kết quả chạy |

## Bài 5: Phân tích và Kiểm thử Bảo mật (SAST & DAST)

| Phần | Nội dung |
|---|---|
| [Bai5/sast-tool/](Bai5/sast-tool/) | Phân tích tĩnh (SAST): duyệt AST, dò pattern, bộ luật, kiểm tra chất lượng (flake8), xuất báo cáo SARIF; có unittest |
| [Bai5/dast-tool/](Bai5/dast-tool/) | Phân tích động (DAST): giám sát runtime, bộ nhớ, mạng, hành vi và sandbox; có CLI, web API (Flask) và unittest |
| [Bai5/screenshots/](Bai5/screenshots/) | Ảnh kết quả chạy |

## Môi trường

- Windows 11, Python 3.14.
- Dùng chung một virtual environment `.venv` ở thư mục gốc repo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Cài thư viện và chạy từng bài theo README của bài đó.
