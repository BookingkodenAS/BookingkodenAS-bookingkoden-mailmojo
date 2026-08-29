"""
Kommandolinje-verktøy: oppretter et nyhetsbrev-KLADD i Mailmojo fra emne + HTML-fil.

Eksempel:
    python create_weekly_newsletter.py \
        --list-id 46067 \
        --subject "Tillit bygges raskere enn du tror" \
        --html-file example_email.html

Sender IKKE noe. Oppretter kun en kladd som må godkjennes/sendes manuelt i Mailmojo.
"""

import argparse
import sys

from mailmojo_client import MailmojoClient, MailmojoError, LIST_BOOKINGKODEN_AS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-id",
        type=int,
        default=LIST_BOOKINGKODEN_AS,
        help=f"Mailmojo-liste-ID (default: {LIST_BOOKINGKODEN_AS} = Bookingkoden AS)",
    )
    parser.add_argument("--subject", required=True, help="Emnelinje for nyhetsbrevet")
    parser.add_argument(
        "--html-file", required=True, help="Sti til HTML-fil med selve innholdet"
    )
    args = parser.parse_args()

    with open(args.html_file, "r", encoding="utf-8") as f:
        html = f.read()

    client = MailmojoClient()

    try:
        result = client.create_newsletter_draft(
            list_id=args.list_id, subject=args.subject, html=html
        )
    except MailmojoError as e:
        print(f"FEIL: {e}", file=sys.stderr)
        sys.exit(1)

    newsletter_id = result.get("id")
    print("Nyhetsbrev-kladd opprettet.")
    print(f"  ID: {newsletter_id}")
    print(f"  Emne: {args.subject}")
    print(f"  Liste-ID: {args.list_id}")
    print("  Gå til https://v3.mailmojo.no/campaigns/ for å se over og sende.")


if __name__ == "__main__":
    main()
