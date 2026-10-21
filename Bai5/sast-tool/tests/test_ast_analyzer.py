import unittest

from sast_tool.ast_analyzer import ASTAnalyzer


class TestASTAnalyzer(unittest.TestCase):
    def test_eval_detection(self):
        code = "eval('2+2')"
        issues = ASTAnalyzer().analyze(code)
        found = any(i["type"] == "Use of eval" for i in issues)
        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
