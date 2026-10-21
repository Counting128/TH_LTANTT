import gc


class MemoryAnalyzer:
    """Phát hiện rò rỉ bộ nhớ cơ bản và kiểm tra tràn số nguyên."""

    def check_memory_leaks(self):
        gc.collect()
        # Các object còn __del__ trong gc.garbage thường là dấu hiệu rò rỉ
        leaks = [obj for obj in gc.garbage if hasattr(obj, "__del__")]
        return leaks

    def check_overflow(self, value):
        try:
            if isinstance(value, int) and abs(value) > 2 ** 63:
                return True
        except Exception:
            return False
        return False
