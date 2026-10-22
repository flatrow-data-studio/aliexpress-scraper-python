"""AliExpress scraper in Python: product prices, sales and shipping to CSV.

Runs the AliExpress Products Scraper (an Apify Actor) for one or more keywords
and saves one row per product to a CSV file, for the ship-to country and
currency you choose.

    export APIFY_TOKEN="<your-apify-token>"
    python scrape.py "wireless earbuds" --sort orders --max-results 60
    python scrape.py "led strip lights" --country GB --currency GBP --min-rating 4.5 --free-shipping
"""

import argparse
import csv
import json
import os
import sys
from decimal import Decimal

from apify_client import ApifyClient

ACTOR = "myth84/aliexpress-search-scraper"

# Columns written to the CSV. Every row of the dataset has more (see the README).
COLUMNS = [
    "platformProductId",
    "title",
    "currency",
    "price",
    "originalPrice",
    "discountPercent",
    "rating",
    "soldCount",
    "shippingFree",
    "shipsFrom",
    "isChoice",
    "isSponsored",
    "listedAt",
    "searchQuery",
    "searchRank",
    "url",
]


def make_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("keywords", nargs="+", help='searches as typed on AliExpress, e.g. "wireless earbuds"')
    parser.add_argument("--country", default="US", help="ship-to country, ISO code: US, GB, FR, DE... (default US)")
    parser.add_argument("--currency", default="USD", help="ISO code: USD, EUR, GBP... (default USD)")
    parser.add_argument("--sort", default="default", choices=["default", "orders", "price_asc", "price_desc"],
                        help="best matches, most ordered, or price")
    parser.add_argument("--price-max", type=int, help="maximum price, a whole number in the chosen currency")
    parser.add_argument("--min-rating", type=float, help="keep products rated at least this value, e.g. 4.5")
    parser.add_argument("--min-sold", type=int, help="keep products with at least this many units sold")
    parser.add_argument("--free-shipping", action="store_true", help="keep products shipped for free")
    parser.add_argument("--choice-only", action="store_true", help="keep products with the Choice badge")
    parser.add_argument("--max-results", type=int, default=50,
                        help="products per keyword (default 50); you pay per product saved")
    parser.add_argument("--max-charge", type=Decimal, help="stop the run once it has cost this many USD")
    return parser


def build_input(args):
    run_input = {
        "searchQueries": args.keywords,
        "country": args.country,
        "currency": args.currency,
        "sortBy": args.sort,
        "maxResults": args.max_results,
    }
    if args.price_max is not None:
        run_input["priceMax"] = args.price_max
    if args.min_rating is not None:
        run_input["minRating"] = args.min_rating
    if args.min_sold is not None:
        run_input["minSold"] = args.min_sold
    if args.free_shipping:
        run_input["freeShippingOnly"] = True
    if args.choice_only:
        run_input["choiceOnly"] = True
    return run_input


def run_actor(run_input, max_charge=None):
    """Runs the Actor, waits for it to finish and returns the rows of its dataset."""
    if not os.environ.get("APIFY_TOKEN"):
        sys.exit("Set APIFY_TOKEN first: Apify Console > Settings > API & Integrations.")
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR).call(run_input=run_input, max_total_charge_usd=max_charge)
    if run is None:
        sys.exit("The run could not be started.")
    status = getattr(run.status, "value", run.status)  # SUCCEEDED, FAILED, TIMED-OUT...
    if status != "SUCCEEDED":
        sys.exit(f"The run ended as {status}: open its log in Apify Console.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def cell(value):
    """Lists and objects as JSON text, so that every CSV row has the same columns."""
    return json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value


def write_csv(rows, path, columns=COLUMNS, append=False):
    new_file = not (append and os.path.exists(path))
    with open(path, "a" if append else "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(columns)
        for row in rows:
            writer.writerow([cell(row.get(column)) for column in columns])


def main():
    parser = make_parser("Scrape AliExpress product prices, sales and shipping to CSV.")
    parser.add_argument("--output", default="aliexpress_products.csv",
                        help="CSV file (default aliexpress_products.csv)")
    args = parser.parse_args()

    rows = run_actor(build_input(args), args.max_charge)
    write_csv(rows, args.output)
    print(f"{len(rows)} products saved to {args.output}")

    priced = (row for row in rows if row.get("price") is not None)
    best_sellers = sorted(priced, key=lambda row: row.get("soldCount") or 0, reverse=True)
    for row in best_sellers[:5]:
        print(f'{row.get("soldCount") or 0:>7} sold  {row["price"]} {row["currency"]}  {row["title"][:80]}')


if __name__ == "__main__":
    main()
