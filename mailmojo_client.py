"""
Mailmojo API-klient for Bookingkoden AS.

Bruker OAuth2 client_credentials-flyten (server-til-server, ingen brukerinnlogging
nødvendig) mot Mailmojos ekte API (https://api.mailmojo.no), IKKE Zapier.

Dokumentasjon: https://mailmojo.dev/

Credentials hentes fra miljøvariabler (.env), se .env.example.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://api.mailmojo.no/oauth/token/"
API_BASE = "https://api.mailmojo.no/v1"

CLIENT_ID = os.environ.get("MAILMOJO_CLIENT_ID", "073cb990-f7a1-4fc0-83dd-663b5ac6d557")
CLIENT_SECRET = os.environ.get("MAILMOJO_CLIENT_SECRET")

# Kjente e-postliste-IDer for Bookingkoden AS (se README)
LIST_BOOKINGKODEN_AS = 46067
LIST_5_TIPS_ABONNENTER = 49158


class MailmojoError(Exception):
    pass


class MailmojoClient:
    """Enkel klient for å hente token og opprette nyhetsbrev-kladder i Mailmojo."""

    def __init__(self, client_id: str = CLIENT_ID, client_secret: str = CLIENT_SECRET):
        if not client_secret:
            raise MailmojoError(
                "MAILMOJO_CLIENT_SECRET mangler. Kopier .env.example til .env og "
                "fyll inn hemmeligheten fra Mailmojo (Konto > API-klienter)."
            )
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._token_expires_at = 0

    def get_access_token(self) -> str:
        """Henter (eller gjenbruker et fortsatt gyldig) access token."""
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        resp = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "newsletters lists subscribe",
            },
            timeout=15,
        )
        if resp.status_code != 200:
            raise MailmojoError(
                f"Klarte ikke hente access token ({resp.status_code}): {resp.text}"
            )

        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 3600)
        return self._access_token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def list_lists(self) -> list:
        """Henter alle e-postlister på kontoen."""
        resp = requests.get(f"{API_BASE}/lists/", headers=self._headers(), timeout=15)
        if resp.status_code != 200:
            raise MailmojoError(f"Klarte ikke hente lister ({resp.status_code}): {resp.text}")
        return resp.json()

    def list_newsletters(self, limit: int = 20) -> list:
        """Henter eksisterende nyhetsbrev/kampanjer (til inspeksjon/verifisering)."""
        resp = requests.get(
            f"{API_BASE}/newsletters/",
            headers=self._headers(),
            params={"limit": limit},
            timeout=15,
        )
        if resp.status_code != 200:
            raise MailmojoError(
                f"Klarte ikke hente nyhetsbrev ({resp.status_code}): {resp.text}"
            )
        return resp.json()

    def create_newsletter_draft(self, list_id: int, subject: str, html: str) -> dict:
        """
        Oppretter et nytt nyhetsbrev som KLADD (ikke sendt).

        Feltnavnene (list_id, subject, html) er hentet fra Zapier sin egen
        Mailmojo-integrasjon, som speiler det ekte API-et, men Zapier sin
        utførelse av selve kallet var buggy og skrev aldri innholdet. Dette
        scriptet kaller API-et direkte i stedet.

        Hvis dette feiler med 400/422, skriv ut resp.text for å se nøyaktig
        hvilke felt Mailmojo faktisk forventer, og juster body under.
        """
        body = {
            "list_id": list_id,
            "subject": subject,
            "html": html,
        }
        resp = requests.post(
            f"{API_BASE}/newsletters/",
            headers=self._headers(),
            json=body,
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise MailmojoError(
                f"Klarte ikke opprette nyhetsbrev ({resp.status_code}): {resp.text}"
            )
        return resp.json()

    def update_newsletter_draft(self, newsletter_id: int, **fields) -> dict:
        """Oppdaterer felt (subject, html, ...) på et eksisterende kladd-nyhetsbrev."""
        resp = requests.patch(
            f"{API_BASE}/newsletters/{newsletter_id}/",
            headers=self._headers(),
            json=fields,
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise MailmojoError(
                f"Klarte ikke oppdatere nyhetsbrev ({resp.status_code}): {resp.text}"
            )
        return resp.json()


def _test():
    client = MailmojoClient()
    print("Henter access token ...")
    token = client.get_access_token()
    print(f"OK – token hentet (starter med {token[:8]}...)")

    print("\nHenter e-postlister ...")
    try:
        lists = client.list_lists()
        for lst in lists.get("results", lists) if isinstance(lists, dict) else lists:
            print(f"  - {lst.get('name') or lst.get('id')}: id={lst.get('id')}")
    except MailmojoError as e:
        print(f"  Kunne ikke hente lister: {e}")

    print("\nHenter eksisterende nyhetsbrev (for referanse) ...")
    try:
        newsletters = client.list_newsletters(limit=5)
        print(newsletters)
    except MailmojoError as e:
        print(f"  Kunne ikke hente nyhetsbrev: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        _test()
    else:
        print("Bruk: python mailmojo_client.py test")
