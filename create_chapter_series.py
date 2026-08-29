"""
Oppretter ett nyhetsbrev-KLADD per kapittel i newsletter-content/manifest.json.
Hvert utkast blir liggende som kladd i Mailmojo (ikke sendt) - Geir kopierer
selv innholdet inn som steg i automasjonen "Velkomstserie - 5 tips" i
Mailmojos egen editor, siden API-et ikke stotter a bygge automasjons-steg
direkte (se README).
"""

import json
import sys

from mailmojo_client import MailmojoClient, MailmojoError, LIST_BOOKINGKODEN_AS

with open("newsletter-content/manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

client = MailmojoClient()

results = []
for item in manifest:
    chapter = item["chapter"]
    title = item["title"]
    fname = item["file"]
    subject = f"{chapter}. {title}"
    with open(f"newsletter-content/{fname}", "r", encoding="utf-8") as f:
        html = f.read()

    try:
        result = client.create_newsletter_draft(
            list_id=LIST_BOOKINGKODEN_AS, subject=subject, html=html
        )
    except MailmojoError as e:
        print(f"FEIL pa kapittel {chapter} ({title}): {e}", file=sys.stderr)
        results.append({"chapter": chapter, "title": title, "error": str(e)})
        continue

    newsletter_id = result.get("id")
    print(f"OK  kapittel {chapter}: '{subject}' -> newsletter_id={newsletter_id}")
    results.append({"chapter": chapter, "title": title, "newsletter_id": newsletter_id})

print("\n=== Oppsummering ===")
for r in results:
    if "error" in r:
        print(f"  {r['chapter']}. {r['title']}: FEILET - {r['error']}")
    else:
        print(f"  {r['chapter']}. {r['title']}: id={r['newsletter_id']}")

failed = [r for r in results if "error" in r]
if failed:
    print(f"\n{len(failed)} av {len(results)} kapitler feilet.")
    sys.exit(1)

print(f"\nAlle {len(results)} kapittel-kladder opprettet. Se https://v3.mailmojo.no/campaigns/")
