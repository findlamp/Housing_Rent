# coding:utf-8


from flask import Blueprint, current_app, make_response
from flask_wtf import csrf


# Provides blueprints for static files
html = Blueprint("web_html", __name__)


# 127.0.0.1:5000/()
# 127.0.0.1:5000/(index.html)
# 127.0.0.1:5000/register.html
# 127.0.0.1:5000/favicon.ico   # If the browser thinks the site identifier is, the browser will request the resource itself

@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    """提供html文件"""

    if not html_file_name:
        html_file_name = "index.html"

    # if file name is not favicon.ico
    if html_file_name != "favicon.ico":
        html_file_name = "html/" + html_file_name

    # Create a CSRF token value
    csrf_token = csrf.generate_csrf()

    # Flask provides a way to return static files
    resp = make_response(current_app.send_static_file(html_file_name))

    # set cookie
    resp.set_cookie("csrf_token", csrf_token)

    return resp
