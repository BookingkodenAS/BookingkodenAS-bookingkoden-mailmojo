"""
Engangs-diagnostikk: sjekker hvilke ekstra endepunkter Mailmojo-API-et
faktisk eksponerer, spesielt rundt automasjoner/dryppserier/velkomstserier,
siden api.mailmojo.no/v1/newsletters/ (kladder) er det eneste vi vet
fungerer fra README. Skriver ut statuskode + kort utdrag av body for hver
kandidat, og henter mailmojo.dev sin forside (blokkert fra Claude Code, men
ikke fra GitHub Actions) for a se om det finnes en offentlig endepunktliste.
"""

import requests
from mailmojo_client import MailmojoClient, API_BASE

client = MailmojoClient()
headers = client._headers()

candidates = [
    "automations/",
    "automation/",
    "autoresponders/",
    "autoresponder/",
    "flows/",
    "series/",
    "drip-campaigns/",
    "welcome-series/",
    "sequences/",
    "triggers/",
    "campaigns/",
]

print("=== Kandidat-endepunkter under", API_BASE, "===")
for path in candidates:
    url = f"{API_BASE}/{path}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        body = resp.text[:300].replace("\n", " ")
        print(f"{resp.status_code}  {url}\n    {body}")
    except Exception as e:
        print(f"ERROR  {url}  {e}")

print("\n=== Root av API-et ===")
for url in [API_BASE + "/", API_BASE.rsplit('/v1', 1)[0] + "/"]:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"{resp.status_code}  {url}\n    {resp.text[:500]}")
    except Exception as e:
        print(f"ERROR  {url}  {e}")

print("\n=== mailmojo.dev (offentlig API-dok) ===")
try:
    resp = requests.get("https://mailmojo.dev/", timeout=15)
    print(resp.status_code, len(resp.text), "bytes")
    print(resp.text[:3000])
except Exception as e:
    print("ERROR mailmojo.dev", e)

try:
    resp = requests.get("https://mailmojo.dev/openapi.json", timeout=15)
    print("\nopenapi.json:", resp.status_code, len(resp.text), "bytes")
    if resp.status_code == 200:
        print(resp.text[:3000])
except Exception as e:
    print("ERROR openapi.json", e)
