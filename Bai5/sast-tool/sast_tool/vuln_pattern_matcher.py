import re


class VulnPatternMatcher:
    """Dò các mẫu regex liên quan đến lỗ hổng bảo mật trên mã nguồn thô."""

    PATTERNS = [
        {
            "pattern": r'password\s*=\s*".*"',
            "message": "Hardcoded password detected.",
        },
        {
            "pattern": r"import\s+pickle",
            "message": "Usage of pickle module can be unsafe.",
        },
    ]

    def match(self, code: str):
        issues = []

        for rule in self.PATTERNS:
            for found in re.finditer(rule["pattern"], code):
                start = found.start()
                lineno = code[:start].count("\n") + 1
                col_offset = start - code.rfind("\n", 0, start) - 1

                issues.append({
                    "type": "Pattern Match",
                    "message": rule["message"],
                    "lineno": lineno,
                    "col_offset": col_offset,
                })

        return issues
