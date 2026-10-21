import ast


class ASTAnalyzer:
    """Duyệt cây cú pháp trừu tượng để phát hiện lời gọi eval()."""

    def analyze(self, code: str):
        issues = []
        tree = ast.parse(code)

        for node in ast.walk(tree):
            is_call = isinstance(node, ast.Call)
            if is_call and getattr(node.func, "id", "") == "eval":
                issues.append({
                    "type": "Use of eval",
                    "message": "Use of eval() is dangerous and should be avoided.",
                    "lineno": node.lineno,
                    "col_offset": node.col_offset,
                })

        return issues
