import psutil


class NetworkTrafficAnalyzer:
    """Thu thập thống kê lưu lượng mạng theo từng giao diện (NIC)."""

    def get_network_stats(self):
        return psutil.net_io_counters(pernic=True)
