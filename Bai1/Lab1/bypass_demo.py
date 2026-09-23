"""
bypass_demo.py — Bài lab kiểm chứng điểm yếu của bộ lọc blocklist.

MỤC ĐÍCH GIÁO DỤC: chạy CHÍNH các validator trong securevalidator/core.py với
một tập chuỗi input được soạn sẵn, rồi in ra chuỗi nào "lọt" qua bộ lọc.
Không sửa cấu trúc code của lab — chỉ thay đổi các chuỗi input để quan sát.

Chạy:  python bypass_demo.py
"""

from securevalidator import (
    validate_email, validate_url, validate_filename,
    sanitize_sql_input, sanitize_html_input,
)

# Mỗi case: (input, có bị coi là "lọt qua bộ lọc" không, ghi chú vì sao)
# "lọt qua" = bộ lọc trả True cho thứ đáng ra phải chặn,
#             hoặc để lại một mảnh payload vẫn còn nguy hiểm.

SQL_CASES = [
    "' OR 1=1 --",              # payload kinh điển -> còn lại '1=1' (tautology)
    "1=1",                      # không dùng ký tự/từ khoá nào -> đi thẳng qua
    "'||1=1",                   # || là toán tử OR trong SQL, không nằm trong blocklist
    "admin'/**/=/**/'admin",    # comment /**/ không bị lọc, dùng để chia cắt token
]

URL_CASES = [
    "http://127.0.0.1/admin",                    # loopback
    "http://169.254.169.254/latest/meta-data/",  # metadata endpoint (cloud SSRF)
    "http://localhost:6379",                     # dịch vụ nội bộ
    "https://evil.com@127.0.0.1/",               # userinfo đánh lừa người đọc
]

FILE_CASES = [
    "../../etc/passwd",          # bị chặn (mẫu chuẩn)
    "%2e%2e%2fetc%2fpasswd",     # dạng URL-encoded -> lọt nếu bị decode ở bước sau
]

EMAIL_CASES = [
    "a@b.c",        # regex chấp nhận địa chỉ gần như vô nghĩa
    '"x"@a.b',      # địa chỉ hợp lệ theo RFC nhưng bị từ chối (quá chặt)
]

HTML_CASES = [
    '<script>alert(1)</script>',   # bị vô hiệu hoá đúng cách bởi html.escape
    'javascript:alert(1)',         # đi qua nguyên vẹn -> nguy hiểm trong href/attribute
    'x onmouseover=alert(1)',      # đi qua nguyên vẹn -> nguy hiểm trong ngữ cảnh thuộc tính
]


def line(label, value):
    print(f"  {label:<8} {value}")


def main():
    print("=" * 62)
    print(" DEMO: điểm yếu của lọc blocklist (chạy trên chính core.py)")
    print("=" * 62)

    print("\n[SQL] sanitize_sql_input — kỳ vọng: vô hiệu injection")
    for p in SQL_CASES:
        out = sanitize_sql_input(p)
        line("input", repr(p))
        line("=> ra", repr(out))
        print()

    print("[URL] validate_url — comment code nói 'prevent SSRF'")
    for p in URL_CASES:
        line("input", repr(p))
        line("=> hợp lệ?", validate_url(p))
        print()

    print("[FILE] validate_filename — chặn path traversal")
    for p in FILE_CASES:
        line("input", repr(p))
        line("=> hợp lệ?", validate_filename(p))
        print()

    print("[EMAIL] validate_email — regex quá lỏng và quá chặt cùng lúc")
    for p in EMAIL_CASES:
        line("input", repr(p))
        line("=> hợp lệ?", validate_email(p))
        print()

    print("[HTML] sanitize_html_input — html.escape phụ thuộc ngữ cảnh")
    for p in HTML_CASES:
        line("input", repr(p))
        line("=> ra", repr(sanitize_html_input(p)))
        print()

    context_xss_demo()


def context_xss_demo():
    """XSS theo ngữ cảnh: cùng html.escape (core không đổi) nhưng đặt vào href.

    Gọi route /context-demo qua test client để lấy đúng HTML mà server sinh ra.
    """
    print("[CONTEXT] escape ĐÚNG hàm nhưng SAI ngữ cảnh (href) -> vẫn XSS")
    payload = "javascript:alert(document.domain)"
    line("payload", repr(payload))
    line("escape", repr(sanitize_html_input(payload)))  # html.escape để nguyên
    try:
        from app import app
    except Exception as exc:  # pragma: no cover
        line("(bỏ qua)", f"không import được app: {exc}")
        return
    html = app.test_client().post(
        "/context-demo", data={"link": payload}).get_data(as_text=True)
    for tag in [ln.strip() for ln in html.splitlines() if "<a href=" in ln]:
        line("HTML ra", tag)
    print("  -> href='javascript:...' = lỗ hổng; href='#' = nhánh đã vá bằng validate_url")


if __name__ == "__main__":
    main()
