# GitSecure Pre-commit Hook Lab

## Chạy / kiểm tra

```bash
cd gitsecure-lab
pip install -r requirements.txt

git init
git config core.hooksPath .githooks

# Windows: cấp quyền thực thi cho hook qua Git Bash
chmod +x .githooks/pre-commit

git add pre-commit-hook-test/bad.py
git commit -m "test"   # bị GitSecure chặn vì password hardcode trong bad.py
```

Kết quả mong đợi: terminal in ra `COMMIT BLOCKED by GitSecure` kèm danh sách
phát hiện (findings), đồng thời chi tiết được ghi vào `gitsecure.log`.

Trên Windows, `check_permissions()` bỏ qua kiểm tra world-writable
(`platform.system() == "Windows"` → `return False`) vì khái niệm quyền POSIX
(`stat.S_IWOTH`) không áp dụng theo cách giống Linux/macOS trên hệ thống file
NTFS.

## Bypass GitSecure (không sửa `.githooks/pre-commit`)

`red_bypass.py` import trực tiếp các hàm `scan_sensitive()`, `check_permissions()`,
`run_bandit()` từ chính file hook gốc (không copy/sửa code), feed các payload
được soạn để né blocklist, rồi dựng 1 repo Git **tạm** (không đụng repo thật)
để chứng minh 1 commit chứa secret thật sự lọt qua trót lọt end-to-end.

```bash
cd Lab2                # chạy từ đây, NGOÀI gitsecure-lab/
python red_bypass.py
```

### 1. `scan_sensitive()` — né blocklist bằng biến đổi cú pháp, không cần đổi ý nghĩa code

| Kỹ thuật | Ví dụ | Vì sao lọt |
|---|---|---|
| Đổi tên biến | `pwd = "hunter123"` | regex tìm cứng chữ `password`, không có trong `pwd` |
| Chèn hậu tố vào keyword | `secret_key = "hunter123456"` | `secret\s*=\s*...` cần `=` ngay sau `secret`, `_key` chen vào giữa làm gãy match |
| Ký tự ngoài charset của `token` | `token = "ab-cdefghijklmnop"` | charset `token` chỉ `[A-Za-z0-9]` (thiếu `-`/`_` so với `apikey`/`secret`) |
| Tách literal bằng nối chuỗi | `password = "12" + "3456"` | regex cần 4+ ký tự **trong một cặp nháy**; Python vẫn nối lại thành `"123456"` lúc chạy |
| Triple-quote string | `password = '''hunter123'''` | ký tự ngay sau nháy mở là 1 nháy khác → `[^'"]{4,}` gãy ngay bước đầu |
| AWS key chèn ký tự phân tách | `akey = "AKIA_ABCDEFGHIJKLMNOP"` | `(AKIA\|ASIA)[A-Z0-9]{16}` cần 16 ký tự liền kề, `_` phá vỡ |
| AWS key mã hoá base64 | `akey_b64 = "QUtJQUFCQ0RFRkdISUpLTE1OT1A="` | value không còn chứa literal `AKIA...` trong source, chỉ `b64decode()` lúc runtime |

### 2. `check_permissions()` — vô hiệu sẵn trên Windows

`if platform.system() == "Windows": return False` khiến bước kiểm tra
world-writable **không bao giờ chạy** trên máy Windows — không cần kỹ thuật né
tránh nào, đây là lỗ hổng có sẵn trong code gốc khi chạy ngoài Linux/macOS.

### 3. `run_bandit()` — lỗi so khớp hoa/thường khiến check chết hẳn

Hook kiểm tra `"SEVERITY: High" in result.stdout` (viết hoa toàn bộ), nhưng
bandit thật in ra `"Severity: High"` (chỉ hoa chữ `S` đầu). Đã kiểm chứng thực
tế bằng cách chạy bandit trên 1 file có lỗi High thật (subprocess + shell=True
+ password hardcode) — bandit tìm thấy lỗi, nhưng hook không bao giờ thấy vì
sai case. Không cần né gì cả, bước kiểm tra này chết sẵn.

### 4. End-to-end

`red_bypass.py` dựng 1 repo Git tạm, gắn đúng hook gốc, rồi `git add` +
chạy hook với 1 file chứa `db_password = "12" + "34567890"`. Kết quả thực tế:
hook thoát mã `0` và in `GitSecure: All checks passed.` — commit chứa mật khẩu
hardcode lọt qua hoàn toàn.

### Nguyên nhân gốc và cách sửa đúng

- Blocklist regex theo *tên biến cố định* luôn bị lách bằng cách đổi tên,
  tách chuỗi, hoặc đổi định dạng literal. Cách sửa đúng: quét theo **entropy**
  (Shannon entropy cao bất thường cho 1 chuỗi ngắn) hoặc dùng công cụ chuyên
  dụng như `gitleaks`/`trufflehog` thay vì regex tự viết.
- Charset không đồng nhất giữa các pattern (`token` thiếu `-`/`_`) là dấu hiệu
  regex viết tay dễ có lỗ hổng không chủ đích — nên review kỹ từng charset.
- So khớp chuỗi output của công cụ ngoài (`bandit`) phải test thực tế, không
  đoán định dạng; tốt hơn nên dùng `bandit -f json` rồi parse field
  `issue_severity` thay vì `in` trên text thô.
- `check_permissions()` cần logic thật cho Windows (ví dụ dùng ACL qua
  `icacls`/`win32security`) thay vì bỏ qua hoàn toàn.
