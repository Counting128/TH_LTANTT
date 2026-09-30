# Thực hành Lập trình An ninh thông tin (TH_LTANTT)

Bài thực hành môn Lập trình An ninh thông tin. Mỗi bài có README riêng ghi cách
chạy, ảnh kết quả và các điểm khác với giáo trình.

| Bài | Nội dung | Chi tiết |
|---|---|---|
| Bài 1 | Lập trình an toàn | [Bai1/](Bai1/) |
| Bài 2 | Mã hoá, triển khai PKI | [Bai2/README.md](Bai2/README.md) |

## Bài 1: Lập trình an toàn

| Lab | Nội dung | README |
|---|---|---|
| Lab 1 | SecureValidator: ứng dụng Flask kiểm tra đầu vào (email, URL, filename, SQL, HTML) | [Bai1/Lab1/README.md](Bai1/Lab1/README.md) |
| Lab 2 | GitSecure: pre-commit hook chặn commit chứa thông tin nhạy cảm | [Bai1/Lab2/README.md](Bai1/Lab2/README.md) |
| Lab 3 | SecureLogger: ghi log an toàn, che dữ liệu nhạy cảm, phát hiện sửa log | [Bai1/Lab3/README.md](Bai1/Lab3/README.md) |

## Bài 2: Mã hoá, triển khai PKI

| Phần | Nội dung |
|---|---|
| [Bai2/crypto-toolkit/](Bai2/crypto-toolkit/) | Thư viện `securecrypto`: AES-256-GCM, RSA, Argon2; kèm CLI, GUI và Flask API |
| [Bai2/mini-ca/](Bai2/mini-ca/) | CA đơn giản: Root CA, Intermediate CA, cấp chứng chỉ, xác thực chuỗi, thu hồi (CRL) |
| [Bai2/screenshots/](Bai2/screenshots/) | Ảnh kết quả chạy |

## Môi trường

- Windows 11, Python 3.14.
- Dùng chung một virtual environment `.venv` ở thư mục gốc repo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Cài thư viện và chạy từng bài theo README của bài đó.
