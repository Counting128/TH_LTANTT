import subprocess


class CodeQualityChecker:
    """Chạy flake8 và chuyển các cảnh báo lint thành issue chuẩn hoá."""

    def check(self, filepath):
        issues = []
        result = subprocess.run(
            ["flake8", filepath],
            capture_output=True,
            text=True,
        )

        for line in result.stdout.splitlines():
            if not line:
                continue

            parts = line.split(":")
            if len(parts) < 4:
                continue

            # Đảm bảo phần dòng và cột đều là số hợp lệ
            try:
                lineno = int(parts[1])
                col_offset = int(parts[2])
            except ValueError:
                continue

            issues.append({
                "type": "Lint Issue",
                "message": line,
                "lineno": lineno,
                "col_offset": col_offset,
            })

        return issues
