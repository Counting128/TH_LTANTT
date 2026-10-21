import subprocess
import tempfile


class VirtualSandbox:
    """Chạy lệnh trong thư mục tạm cách ly và trả về stdout/stderr."""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

    def run_isolated(self, command):
        result = subprocess.run(
            command,
            cwd=self.temp_dir,
            capture_output=True,
            shell=True,
        )
        return result.stdout.decode(), result.stderr.decode()
