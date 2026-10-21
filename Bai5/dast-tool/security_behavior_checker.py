class SecurityBehaviorChecker:
    """Quét chính mã nguồn đang chạy để tìm các lời gọi hệ thống nhạy cảm."""

    SUSPICIOUS_CALLS = ["os.system", "eval", "exec"]

    def suspicious_calls(self):
        suspicious = []
        try:
            with open(__file__, "r", encoding="utf-8") as f:
                content = f.read()
            for call in self.SUSPICIOUS_CALLS:
                if call in content:
                    suspicious.append(call)
        except Exception:
            pass
        return suspicious
