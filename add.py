"""
Add a rental listing to the SQLite database.

Run from the project root:
  python add.py --price 100000 --rent 800 --size 50 --location Budapest
  python add.py   # prompts for each field
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database import connect, init_schema
from backend.models import ListingIn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def add_listing(
    price: float,
    rent: float,
    size: float,
    location: str,
    *,
    source: str = "manual",
) -> int:
    """Insert one listing; returns new row id."""
    listing = ListingIn(price=price, rent=rent, size=size, location=location.strip())
    conn = connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO listings (price, rent, size, location, source, created_at)
            VALUES (:price, :rent, :size, :location, :source, :created_at);
            """,
            {
                "price": listing.price,
                "rent": listing.rent,
                "size": listing.size,
                "location": listing.location,
                "source": source,
                "created_at": _now_iso(),
            },
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def _prompt_float(label: str) -> float:
    while True:
        raw = input(f"{label}: ").strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("  Enter a number.")


def _prompt_str(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("  Required.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a rental listing to RentEdge AI.")
    parser.add_argument("--price", type=float, help="Purchase price (EUR)")
    parser.add_argument("--rent", type=float, help="Monthly rent (EUR)")
    parser.add_argument("--size", type=float, help="Size (m²)")
    parser.add_argument("--location", type=str, help="City or area name")
    parser.add_argument("--source", type=str, default="manual", help="Source tag (default: manual)")
    args = parser.parse_args()

    init_schema()

    if args.price is not None and args.rent is not None and args.size is not None and args.location:
        price, rent, size, location = args.price, args.rent, args.size, args.location
    else:
        print("Enter listing details (or pass --price --rent --size --location).")
        price = args.price if args.price is not None else _prompt_float("Price (EUR)")
        rent = args.rent if args.rent is not None else _prompt_float("Monthly rent (EUR)")
        size = args.size if args.size is not None else _prompt_float("Size (m²)")
        location = args.location if args.location else _prompt_str("Location")

    row_id = add_listing(price, rent, size, location, source=args.source)
    print(f"Added listing #{row_id}: {location} — €{price:,.0f}, {size} m², €{rent:,.0f}/mo".replace(",", " "))


if __name__ == "__main__":
    main()
