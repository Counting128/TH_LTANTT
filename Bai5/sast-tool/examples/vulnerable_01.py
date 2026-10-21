"""File ví dụ chứa nhiều lỗi bảo mật cố ý để kiểm thử công cụ SAST."""

import pickle  # import module không an toàn (deserialize tuỳ ý)

# Thông tin đăng nhập bị gán cứng trong mã nguồn
password = "admin@123"


def unsafe_func(expr):
    # eval() thực thi chuỗi tuỳ ý -> cực kỳ nguy hiểm
    return eval(expr)


def safe_func():
    print("Hello world!")


if __name__ == "__main__":
    unsafe_func("2 + 2")
    safe_func()
