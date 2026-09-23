from flask import Flask, render_template, request
from securevalidator import (
    validate_email, validate_url, validate_filename,
    sanitize_sql_input, sanitize_html_input
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        results = {
            "email": validate_email(request.form["email"]),
            "url": validate_url(request.form["url"]),
            "filename": validate_filename(request.form["filename"]),
            "sql": sanitize_sql_input(request.form["sql"]),
            "html": sanitize_html_input(request.form["html"]),
        }
    return render_template("index.html", results=results)


@app.route("/context-demo", methods=["GET", "POST"])
def context_demo():
    """Demo: escaping ĐÚNG hàm nhưng SAI ngữ cảnh vẫn dẫn tới XSS.

    Không sửa securevalidator/core.py — vẫn gọi sanitize_html_input (html.escape).
    Chỉ khác: output được nhét vào thuộc tính href, nơi html.escape không đủ.
    """
    payload = ""
    escaped = ""
    safe_href = "#"          # bản vá đúng: chỉ nhận http/https
    if request.method == "POST":
        payload = request.form.get("link", "")
        escaped = sanitize_html_input(payload)          # = html.escape, giữ nguyên core
        safe_href = escaped if validate_url(payload) else "#"
    return render_template(
        "context_demo.html",
        payload=payload, escaped=escaped, safe_href=safe_href,
    )


if __name__ == "__main__":
    app.run(debug=True)
