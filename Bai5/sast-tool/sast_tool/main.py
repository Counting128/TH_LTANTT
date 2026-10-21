import sys

from sast_tool.ast_analyzer import ASTAnalyzer
from sast_tool.vuln_pattern_matcher import VulnPatternMatcher
from sast_tool.security_rule_engine import SecurityRuleEngine
from sast_tool.code_quality_checker import CodeQualityChecker
from sast_tool.sarif_reporter import SarifReporter


def main(file_path):
    with open(file_path, encoding="utf-8") as f:
        code = f.read()

    # 1) Phân tích AST, 2) dò pattern, 3) kiểm tra chất lượng bằng flake8
    ast_issues = ASTAnalyzer().analyze(code)
    pattern_issues = VulnPatternMatcher().match(code)
    quality_issues = CodeQualityChecker().check(file_path)

    # Áp bộ luật để gán severity, sau đó gộp thêm issue lint
    rule_engine = SecurityRuleEngine()
    final_issues = rule_engine.evaluate(ast_issues, pattern_issues)
    final_issues += quality_issues

    SarifReporter().generate_report(final_issues, analyzed_file=file_path)
    print("Analysis complete.")
    print(f"    Report saved to report.sarif with {len(final_issues)} issues.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m sast_tool.main <file_to_analyze.py>")
        sys.exit(1)
    main(sys.argv[1])
