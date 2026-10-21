"""Ví dụ thứ hai: trình diễn eval/exec và thao tác đọc file."""


def dangerous_eval(user_input):
    # Không kiểm soát đầu vào trước khi đưa vào eval
    return eval(user_input)


def read_file(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def execute_code(code):
    # exec cũng nguy hiểm tương tự eval
    exec(code)


if __name__ == "__main__":
    snippet = "print('Hello from eval')"
    dangerous_eval(snippet)
