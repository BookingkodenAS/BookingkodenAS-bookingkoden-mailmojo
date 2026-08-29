"""
Engangs-diagnostikk: henter Mailmojos Swagger/OpenAPI-spesifikasjon fra
https://api.mailmojo.no/ (funnet ved a sjekke API-roten) og filtrerer ut
alt relatert til automasjoner/dryppserier/velkomstserier, siden
api.mailmojo.no/v1/newsletters/ (kladder) er det eneste vi vet fungerer
fra README.
"""

import json
import requests
from mailmojo_client import MailmojoClient

client = MailmojoClient()
headers = client._headers()

resp = requests.get("https://api.mailmojo.no/", headers=headers, timeout=30)
print("status:", resp.status_code, "bytes:", len(resp.text))

with open("mailmojo_openapi.json", "w") as f:
    f.write(resp.text)

spec = resp.json()

print("\ntop-level keys:", list(spec.keys()))

paths = spec.get("paths", {})
print(f"\n=== Alle {len(paths)} paths ===")
for p in sorted(paths.keys()):
    methods = list(paths[p].keys())
    print(f"  {p}  [{', '.join(methods)}]")

keywords = ["automat", "series", "sequence", "welcome", "trigger", "drip", "flow", "step", "journey"]
print("\n=== Paths/definitions som matcher nokkelord:", keywords, "===")
for p, methods in paths.items():
    blob = json.dumps(methods).lower()
    if any(k in p.lower() or k in blob for k in keywords):
        print(f"\n--- {p} ---")
        print(json.dumps(methods, indent=2)[:2000])

definitions = spec.get("definitions", {})
print(f"\n=== Definisjoner som matcher nokkelord (av {len(definitions)} totalt) ===")
for name in sorted(definitions.keys()):
    if any(k in name.lower() for k in keywords):
        print(f"  {name}")
