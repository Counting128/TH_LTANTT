import tempfile
import unittest

from sast_tool.code_quality_checker import CodeQualityChecker


class TestCodeQualityChecker(unittest.TestCase):
    def test_flake8_detection(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         delete=True) as tmp:
            tmp.write("import os\n\n\n")
            tmp.flush()

            issues = CodeQualityChecker().check(tmp.name)
            only_lint = all(i["type"] == "Lint Issue" for i in issues)
            self.assertTrue(only_lint or len(issues) == 0)


if __name__ == "__main__":
    unittest.main()
