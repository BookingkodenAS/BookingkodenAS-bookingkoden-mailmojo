"""
Runde 2: full skjema-detalj for Automation/Trigger, samt en titt på
eksisterende nyhetsbrev (for a se om automasjons-e-poster/steg dukker opp
der, og om "Velkomstserie - 5 tips" har en synlig automation_id).
"""

import json
import requests
from mailmojo_client import MailmojoClient, API_BASE

client = MailmojoClient()
headers = client._headers()

resp = requests.get("https://api.mailmojo.no/", headers=headers, timeout=30)
spec = resp.json()
definitions = spec.get("definitions", {})

for name in ["Automation", "AutomationDetail", "AutomationStatistics", "Trigger", "TriggerRule", "Newsletter", "NewsletterDetail", "NewsletterList"]:
    if name in definitions:
        print(f"\n=== definition: {name} ===")
        print(json.dumps(definitions[name], indent=2))
    else:
        print(f"\n(ingen definisjon kalt {name})")

print("\n\n=== GET /v1/newsletters/ (eksisterende nyhetsbrev/steg) ===")
resp = requests.get(f"{API_BASE}/newsletters/", headers=headers, params={"limit": 50}, timeout=20)
print("status:", resp.status_code)
print(json.dumps(resp.json(), indent=2)[:6000])
