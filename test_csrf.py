
import urllib.request
import urllib.error

from flask import url_for
from app import app

with app.test_request_context():
    test_url = url_for("settings.security_settings")

request = urllib.request.Request(
    "http://127.0.0.1:5000" + test_url,
    data=b"current_password=test&new_password=test12345678&confirm_password=test12345678",
    headers={
        "Content-Type": "application/x-www-form-urlencoded"
    },
    method="POST"
)

try:
    urllib.request.urlopen(request)
    print("Unexpected response: CSRF protection may not be working.")

except urllib.error.HTTPError as error:
    if error.code == 400:
        print("SUCCESS: Security Settings CSRF protection is working.")
    else:
        print("Check required. HTTP status:", error.code)

except Exception as error:
    print("Error:", error)
