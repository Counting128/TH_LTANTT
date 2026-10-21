import os
import unittest

from sast_tool.sarif_reporter import SarifReporter


class TestSarifReporter(unittest.TestCase):
    def test_generate_report(self):
        issues = [{
            "type": "Test",
            "message": "Test message",
            "lineno": 1,
            "col_offset": 0,
        }]

        output_file = "test_report.sarif"
        SarifReporter().generate_report(issues, output_file)

        self.assertTrue(os.path.exists(output_file))
        os.remove(output_file)


if __name__ == "__main__":
    unittest.main()
