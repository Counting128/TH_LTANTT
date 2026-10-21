import json
import os
import unittest

from sast_tool.security_rule_engine import SecurityRuleEngine


class TestSecurityRuleEngine(unittest.TestCase):
    TEMP_RULES = "rules/temp_rules.json"

    def setUp(self):
        # Tạo file luật tạm thời để kiểm thử độc lập
        self.rules = [
            {"type": "Use of eval", "severity": "high"},
            {"type": "Pattern Match", "severity": "medium"},
        ]
        with open(self.TEMP_RULES, "w") as f:
            json.dump(self.rules, f)
        self.engine = SecurityRuleEngine(self.TEMP_RULES)

    def tearDown(self):
        os.remove(self.TEMP_RULES)

    def test_evaluate(self):
        ast_issues = [{
            "type": "Use of eval", "message": "msg",
            "lineno": 1, "col_offset": 0,
        }]
        pattern_issues = [{
            "type": "Pattern Match", "message": "msg",
            "lineno": 2, "col_offset": 1,
        }]

        results = self.engine.evaluate(ast_issues, pattern_issues)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["severity"], "high")
        self.assertEqual(results[1]["severity"], "medium")


if __name__ == "__main__":
    unittest.main()
