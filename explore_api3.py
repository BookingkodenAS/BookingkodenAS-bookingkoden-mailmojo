"""
Runde 3: hent den faktiske "Velkomstserie - 5 tips"-automasjonen
(automation_id=57996, fra https://v3.mailmojo.no/automation/57996/) for a
se om den er feed-drevet (RSS) eller noe annet, og hvilke innstillinger
den faktisk har.
"""

import json
import requests
from mailmojo_client import MailmojoClient, API_BASE

client = MailmojoClient()
headers = client._headers()

automation_id = 57996
url = f"{API_BASE}/automations/{automation_id}/"
resp = requests.get(url, headers=headers, timeout=20)
print("status:", resp.status_code)
print(json.dumps(resp.json(), indent=2) if resp.headers.get("content-type", "").startswith("application/json") else resp.text)
