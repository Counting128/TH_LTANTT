"""
red_bypass.py — Red team: chứng minh cách qua mặt SecureLogger (che PII) và
tamper detection (secure.log.sig) MÀ KHÔNG sửa secure_logger_lab/securelogger/logger.py
hay secure_logger_lab/securevalidator/core.py (core giữ nguyên 100%).

File này cố ý đặt NGOÀI secure_logger_lab/ (folder chứa nguyên xi source từ
sách) để phân biệt rõ: secure_logger_lab/ = Blue (không đụng), red_bypass.py = Red (mới).

Chạy (từ thư mục Lab3/, ngoài secure_logger_lab/):  python red_bypass.py
"""

import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # tránh UnicodeEncodeError trên console cp1252 (Windows)

# red_bypass.py nằm ngoài secure_logger_lab/ (để tách bạch Blue/Red) nên phải
# tự thêm folder đó vào sys.path trước khi import package Blue bên trong, đồng
# thời chuyển cwd vào đó để secure.log/secure.log.sig (được logger tạo lúc
# import) nằm đúng bên trong secure_logger_lab/ thay vì lạc ra ngoài Lab3/.
_LAB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secure_logger_lab")
sys.path.insert(0, _LAB_DIR)
os.chdir(_LAB_DIR)

from securelogger.logger import mask_pii, hash_line
from securevalidator.core import (
    validate_email, validate_url, validate_filename,
    sanitize_sql_input, sanitize_html_input,
)


def demo_mask_pii_password_leak():
    print("=" * 70)
    print(" [1] mask_pii() — password/token/apikey KHÔNG BAO GIỜ bị che khi")
    print("     đi qua trường 'data'/'results' (dict) mà app.py log ra")
    print("=" * 70)
    print("Nguyên nhân gốc: TOKEN_PATTERN yêu cầu literal dấu '=' ngay sau keyword")
    print('  r\'(?i)(token|apikey|key|password)\\s*=\\s*["\\\']?[\\w\\-]{8,}["\\\']?\'')
    print("nhưng khi Python in 1 dict ra chuỗi (str(dict)) thì cú pháp luôn là")
    print("  {'key': 'value'}   <- dấu HAI CHẤM, không phải dấu BẰNG")
    print("=> nếu request /validate gửi kèm 1 field lạ tên 'password', field đó")
    print("   sẽ được log nguyên vẹn trong 'data' mà KHÔNG hề bị mask.\n")

    # Mô phỏng đúng những gì app.py làm: secure_logger.info(..., extra={"data": data, ...})
    # rồi JSONFormatter gọi mask_pii(str(record.data)).
    attacker_payload = {
        "email": "phuoc@example.com",
        "url": "https://secure.com",
        "filename": "report.pdf",
        "sql": "' OR 1=1 --",
        "html": "<script>alert(1)</script>",
        "password": "hunter123456",   # field KHÔNG có trong schema nhưng vẫn bị log nguyên
    }
    raw = str(attacker_payload)
    masked = mask_pii(raw)

    print("raw   :", raw)
    print("masked:", masked)
    leaked = "hunter123456" in masked
    print(f"\n-> password còn NGUYÊN VĂN trong log sau khi mask_pii()?  {leaked}")
    print(f"-> email trong cùng dict có bị che đúng như kỳ vọng?        {'<email_masked>' in masked}")
    print()


def demo_mask_pii_plus_alias_email():
    print("=" * 70)
    print(" [2] mask_pii() — email dạng +alias chỉ bị che MỘT PHẦN")
    print("=" * 70)
    print(r"EMAIL_PATTERN: r'[\w\.-]+@[\w\.-]+\.\w+'  -- \w không gồm ký tự '+'")
    text = str({"email": "vice.director+leak@example.com"})
    masked = mask_pii(text)
    print("raw   :", text)
    print("masked:", masked)
    leaked_prefix = "vice.director+" in masked
    print(f"\n-> phần username thật trước dấu '+' vẫn lộ trong log?  {leaked_prefix}")
    print("-> chỉ có 'leak@example.com' bị thay <email_masked>, còn danh tính thật "
          "'vice.director' thì không.")
    print()


def demo_tamper_signature_forge():
    print("=" * 70)
    print(" [3] secure.log.sig — 'chữ ký' chỉ là SHA-256 KHÔNG khoá bí mật")
    print("     => ai có quyền ghi file đều tự forge lại được, không cần biết bí mật gì")
    print("=" * 70)
    original_line = (
        '{"timestamp": "2025-06-10T06:56:26.197056Z", "level": "INFO", '
        '"message": "Validation check performed", "results": '
        '"{\'email\': True, \'url\': True, \'sql\': \'1=1\'}"}'
    )
    real_sig = hash_line(original_line)
    print("dòng log gốc      :", original_line)
    print("chữ ký thật (.sig):", real_sig)

    # Kẻ tấn công có quyền ghi secure.log (vd: chiếm được server, hoặc log lưu trên
    # volume dùng chung) sửa nội dung dòng log để xoá dấu vết...
    tampered_line = original_line.replace(
        '"results": "{\'email\': True, \'url\': True, \'sql\': \'1=1\'}"',
        '"results": "{\'email\': True, \'url\': True, \'sql\': \'\'}"'   # xoá bằng chứng SQLi lọt qua
    )
    # ...rồi chỉ cần gọi ĐÚNG hàm hash_line() công khai này để tự tính lại chữ ký mới,
    # không cần biết bất kỳ khoá bí mật nào vì hash_line() không dùng HMAC/khoá.
    forged_sig = hash_line(tampered_line)

    print("\ndòng log bị sửa   :", tampered_line)
    print("chữ ký giả mạo    :", forged_sig)
    print(f"\n-> chữ ký giả có khớp định dạng secure.log.sig y hệt chữ ký thật? "
          f"{len(forged_sig) == len(real_sig) == 64}")
    print("-> Vì append_signature() chỉ gọi hashlib.sha256(line) (không phải "
          "hmac.new(secret_key, line, sha256)), NGƯỜI XÁC MINH LẪN KẺ TẤN CÔNG dùng "
          "chung 1 hàm công khai, không có gì phân biệt được dòng nào do SecureLogger "
          "thật sinh ra và dòng nào do kẻ tấn công tự chế + tự ký lại. Tamper detection "
          "vì vậy không có giá trị chống giả mạo thực sự, chỉ phát hiện lỗi ngẫu nhiên.")
    print()


def demo_inherited_validator_bypass():
    print("=" * 70)
    print(" [4] Kế thừa toàn bộ điểm yếu của SecureValidator (Lab1) — vì")
    print("     securevalidator/core.py trong Lab3 là bản copy y hệt, không đổi")
    print("=" * 70)
    cases = [
        ("sanitize_sql_input", sanitize_sql_input("' OR 1=1 --"),
         "còn lại tautology 1=1 dùng được"),
        ("validate_url", validate_url("http://169.254.169.254/latest/meta-data/"),
         "endpoint metadata cloud vẫn hợp lệ -> SSRF thật"),
        ("validate_filename", validate_filename("%2e%2e%2fetc%2fpasswd"),
         "dạng URL-encoded của ../ vẫn được coi là hợp lệ"),
        ("sanitize_html_input", sanitize_html_input("javascript:alert(1)"),
         "html.escape không thêm gì -> nguy hiểm nếu đặt vào href"),
    ]
    for name, result, why in cases:
        print(f"  {name:<22} -> {result!r}   ({why})")
    print("\n(chi tiết đầy đủ + nguyên nhân gốc: xem Bai1/Lab1/README.md)")
    print()


def main():
    demo_mask_pii_password_leak()
    demo_mask_pii_plus_alias_email()
    demo_tamper_signature_forge()
    demo_inherited_validator_bypass()


if __name__ == "__main__":
    main()
