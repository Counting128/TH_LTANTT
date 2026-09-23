"""
red_bypass.py — Red team: chứng minh cách qua mặt GitSecure pre-commit hook
MÀ KHÔNG sửa gitsecure-lab/.githooks/pre-commit (core hook giữ nguyên 100%).

File này cố ý đặt NGOÀI gitsecure-lab/ (folder chứa nguyên xi source từ sách)
để phân biệt rõ: gitsecure-lab/ = Blue (không đụng), red_bypass.py = Red (mới).

Cách hoạt động: import trực tiếp các hàm scan_sensitive() / check_permissions()
/ run_bandit() từ CHÍNH file .githooks/pre-commit rồi feed các payload được
soạn để né bộ lọc blocklist, quan sát hàm nào trả None (nghĩa là "an toàn giả").

Chạy (từ thư mục Lab2/, ngoài gitsecure-lab/):  python red_bypass.py
"""

import importlib.util
from importlib.machinery import SourceFileLoader
import os
import subprocess
import sys
import tempfile

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # tránh UnicodeEncodeError trên console cp1252 (Windows)

HOOK_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "gitsecure-lab", ".githooks", "pre-commit"
)


def load_hook():
    loader = SourceFileLoader("gitsecure_hook", HOOK_PATH)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


hook = load_hook()

# Mỗi case: (nhãn, nội dung file, giải thích vì sao né được regex blocklist)
# "LỌT QUA" = scan_sensitive() trả None dù nội dung thực chứa secret sống được.
SENSITIVE_CASES = [
    ('baseline (đối chứng)', 'password = "hunter123"',
     'đúng định dạng keyword=value -> hook bắt được'),
    ('đổi tên biến', 'pwd = "hunter123"',
     'regex chỉ tìm cứng chữ "password", không có \\b nên "mypassword" vẫn bị bắt, '
     'nhưng "pwd" thì không chứa "password" nên lọt'),
    ('chèn hậu tố vào keyword', 'secret_key = "hunter123456"',
     'pattern là secret\\s*=\\s*... -> giữa "secret" và "=" có "_key" (không phải khoảng '
     'trắng) nên không khớp'),
    ('token dùng ký tự ngoài charset', 'token = "ab-cdefghijklmnop"',
     'charset của token chỉ cho phép [A-Za-z0-9] (thiếu - _ so với apikey/secret) '
     '-> chèn "-" trong 10 ký tự đầu là phá vỡ chuỗi khớp liên tục'),
    ('tách literal bằng nối chuỗi', 'password = "12" + "3456"',
     'regex yêu cầu 4+ ký tự ngay trong MỘT cặp nháy -> "12" chỉ có 2 ký tự nên không khớp, '
     'nhưng lúc chạy Python vẫn nối thành "123456" y như cũ'),
    ('triple-quote string', "password = '''hunter123'''",
     "regex đọc ['\\\"][^'\\\"]{4,}['\\\"] -> ký tự ngay sau nháy mở là 1 nháy khác "
     "(vì triple-quote) nên [^'\\\"] thất bại ngay bước đầu"),
    ('AWS key chèn ký tự phân tách', 'akey = "AKIA_ABCDEFGHIJKLMNOP"',
     '(AKIA|ASIA)[A-Z0-9]{16} yêu cầu 16 ký tự liền sau AKIA không có gì xen vào -> "_" phá vỡ'),
    ('AWS key nối chuỗi + base64', 'akey_b64 = "QUtJQUFCQ0RFRkdISUpLTE1OT1A="',
     'giá trị đã base64-encode, không còn chứa literal "AKIA..." hay "apikey=" trong source '
     '-> chỉ cần base64.b64decode() lúc runtime là ra lại access key thật'),
]


def demo_scan_sensitive():
    print("=" * 70)
    print(" [1] scan_sensitive() — né bộ lọc blocklist bằng biến đổi cú pháp")
    print("=" * 70)
    for label, content, why in SENSITIVE_CASES:
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(content + "\n")
            result = hook.scan_sensitive(path)
            status = "BỊ CHẶN " if result else "LỌT QUA (bypass)"
            print(f"[{status}] {label}")
            print(f"    code : {content}")
            print(f"    vì   : {why}")
            if result:
                print(f"    hook : {result}")
        finally:
            os.remove(path)
        print()


def demo_check_permissions():
    print("=" * 70)
    print(" [2] check_permissions() — kiểm tra world-writable")
    print("=" * 70)
    fd, path = tempfile.mkstemp(suffix=".py")
    os.write(fd, b"x = 1\n")
    os.close(fd)
    try:
        result = hook.check_permissions(path)
        print(f"platform hiện tại : {sys.platform}")
        print(f"kết quả check_permissions() : {result!r}")
        print("-> Trên Windows, hàm return False ngay dòng đầu (if platform.system() == "
              '"Windows": return False) -- KHÔNG CẦN kỹ thuật né tránh nào, bước kiểm tra '
              "quyền file coi như vô hiệu hoàn toàn trên máy Windows.")
    finally:
        os.remove(path)
    print()


def demo_run_bandit():
    print("=" * 70)
    print(" [3] run_bandit() — lỗi so khớp chuỗi hoa/thường")
    print("=" * 70)
    print('Hook kiểm tra:  if "SEVERITY: High" in result.stdout   (viết hoa toàn bộ)')
    tmp_dir = tempfile.mkdtemp(prefix="bandit_probe_")
    try:
        # File chắc chắn kích hoạt 1 finding SEVERITY=HIGH thật của bandit
        # (B602: subprocess với shell=True ghép chuỗi trực tiếp).
        with open(os.path.join(tmp_dir, "vuln.py"), "w") as f:
            f.write(
                "import subprocess\n"
                'password = "hunter123456"\n'
                'subprocess.call("echo " + password, shell=True)\n'
            )
        real = subprocess.run(["bandit", "-r", tmp_dir], capture_output=True, text=True)
        found_real_case = "Severity: High" in real.stdout      # định dạng thật của bandit
        found_hook_case = "SEVERITY: High" in real.stdout      # định dạng hook tìm
        print(f'bandit thực sự tìm thấy lỗi High severity ở file mẫu này -> {found_real_case}')
        print(f'chuỗi "SEVERITY: High" (hook tìm) có xuất hiện trong stdout?  -> {found_hook_case}')
        print("-> bandit tồn tại lỗi High thật (đã xác nhận), nhưng hook không bao giờ thấy vì "
              "nó tìm sai case. run_bandit() vì vậy KHÔNG BAO GIỜ phát hiện được lỗi 'High "
              "severity', bất kể bandit thực sự tìm thấy bao nhiêu lỗi nghiêm trọng. Không cần "
              "né gì cả — bước kiểm tra này chết sẵn trong code gốc.")
    except FileNotFoundError:
        print("(bỏ qua: chưa cài bandit — pip install bandit để tự kiểm chứng)")
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
    print()


def demo_full_commit_bypass():
    """Chứng minh bypass hoạt động thật trong luồng commit của Git.

    Tạo 1 repo Git TẠM (KHÔNG đụng tới gitsecure-lab thật), copy nguyên
    .githooks/pre-commit vào đó, rồi thử commit 1 file chứa secret đã né
    theo kỹ thuật 'tách literal bằng nối chuỗi' ở trên.
    """
    print("=" * 70)
    print(" [4] End-to-end: commit thật với secret đã né qua repo Git tạm")
    print("=" * 70)
    tmp_repo = tempfile.mkdtemp(prefix="gitsecure_bypass_demo_")
    try:
        subprocess.run(["git", "init", "-q"], cwd=tmp_repo, check=True)
        subprocess.run(["git", "config", "user.email", "red@demo.local"], cwd=tmp_repo, check=True)
        subprocess.run(["git", "config", "user.name", "Red Demo"], cwd=tmp_repo, check=True)
        os.makedirs(os.path.join(tmp_repo, ".githooks"), exist_ok=True)
        with open(HOOK_PATH, "r", encoding="utf-8") as src:
            hook_src = src.read()
        hook_dst = os.path.join(tmp_repo, ".githooks", "pre-commit")
        with open(hook_dst, "w", encoding="utf-8", newline="\n") as dst:
            dst.write(hook_src)
        os.chmod(hook_dst, 0o755)
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=tmp_repo, check=True)

        secret_file = os.path.join(tmp_repo, "config.py")
        with open(secret_file, "w") as f:
            f.write('db_password = "12" + "34567890"\n')  # né regex, ráp lại lúc runtime

        subprocess.run(["git", "add", "config.py"], cwd=tmp_repo, check=True)
        result = subprocess.run(
            [sys.executable, hook_dst],
            cwd=tmp_repo, capture_output=True, text=True,
        )
        print(f"repo tạm       : {tmp_repo}")
        print(f"exit code hook : {result.returncode}  (0 = cho qua, != 0 = bị chặn)")
        print("stdout hook    :", result.stdout.strip() or "(rỗng)")
        if result.returncode == 0:
            print("-> Hook CHO QUA. Nếu đây là repo thật, commit chứa mật khẩu hardcode "
                  "sẽ lọt lên remote mà GitSecure không hề cảnh báo.")
        else:
            print("-> Hook vẫn chặn (payload cần điều chỉnh thêm).")
    except FileNotFoundError:
        print("(bỏ qua: máy chưa có lệnh git trong PATH)")
    finally:
        import shutil
        shutil.rmtree(tmp_repo, ignore_errors=True)
    print()


def main():
    demo_scan_sensitive()
    demo_check_permissions()
    demo_run_bandit()
    demo_full_commit_bypass()


if __name__ == "__main__":
    main()
