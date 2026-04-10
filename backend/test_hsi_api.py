import requests
import numpy as np
import io

# Create a small dummy npy file in memory
X = np.random.rand(10, 10, 200)
buf = io.BytesIO()
np.save(buf, X)
buf.seek(0)

# Send request
url = 'http://172.32.5.147:8000/api/v1/analyze-hsi'
files = {'file': ('dummy.npy', buf, 'application/octet-stream')}

print("Sending request to", url)
try:
    resp = requests.post(url, files=files, timeout=10)
    print("Status:", resp.status_code)
    print("Response headers:", resp.headers)
    if resp.status_code == 200:
        print("Success! JSON keys:", resp.json().keys())
    else:
        print("Error text:", resp.text)
except Exception as e:
    print("Exception:", e)
