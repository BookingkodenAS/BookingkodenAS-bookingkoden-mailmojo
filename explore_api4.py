"""
Runde 4: prov a hente et nytt token med "automations"-scope i tillegg,
og bruk det til a hente Velkomstserie-automasjonen (id 57996).
"""

import json
import os
import requests

CLIENT_ID = os.environ.get("MAILMOJO_CLIENT_ID", "073cb990-f7a1-4fc0-83dd-663b5ac6d557")
CLIENT_SECRET = os.environ["MAILMOJO_CLIENT_SECRET"]
TOKEN_URL = "https://api.mailmojo.no/oauth/token/"
API_BASE = "https://api.mailmojo.no/v1"

for scope in [
    "newsletters lists subscribe automations",
    "newsletters lists subscribe automations:read",
    "automations",
    "automations:read",
]:
    print(f"\n=== Prover scope: '{scope}' ===")
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": scope,
        },
        timeout=15,
    )
    print("token status:", resp.status_code)
    print(resp.text[:500])
    if resp.status_code != 200:
        continue
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    r2 = requests.get(f"{API_BASE}/automations/57996/", headers=headers, timeout=20)
    print("automation GET status:", r2.status_code)
    print(r2.text[:1500])
