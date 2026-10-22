"""AliExpress price tracker: the price drops, rises and new products since the previous run.

Runs the same search in price-monitoring mode. The Actor keeps the last price
of every product in a key-value store of your Apify account, so this script
can run from cron on any machine. The first run records the reference; later
runs return only the new products and the price changes (or, with
--only-drops, only the price drops), appended to a CSV history.

    export APIFY_TOKEN="<your-apify-token>"
    python monitor_prices.py "wireless earbuds" --sort orders --store earbuds-daily
"""

from scrape import COLUMNS, build_input, make_parser, run_actor, write_csv

MONITOR_COLUMNS = ["changeType", "previousPrice", "priceDelta", "priceDeltaPercent"]


def main():
    parser = make_parser("AliExpress price tracker: new products and price changes since the previous run.")
    parser.add_argument("--store", default="price-tracker",
                        help="name of the key-value store of your Apify account that keeps the previous prices "
                             "(one name per schedule)")
    parser.add_argument("--only-drops", action="store_true", help="return only the products whose price went down")
    parser.add_argument("--history", default="aliexpress_price_changes.csv",
                        help="CSV file the changes are appended to (default aliexpress_price_changes.csv)")
    args = parser.parse_args()

    run_input = build_input(args)
    run_input["monitorMode"] = "changes"
    run_input["monitorStoreName"] = args.store
    if args.only_drops:
        run_input["onlyPriceDrops"] = True
    rows = run_actor(run_input, args.max_charge)

    if not rows:
        print("No price drop since the previous run (the first run only records the prices)."
              if args.only_drops else "Nothing moved since the previous run.")
        return
    write_csv(rows, args.history, COLUMNS + MONITOR_COLUMNS, append=True)

    changed = [row for row in rows if row["changeType"] == "price_changed"]
    new = len(rows) - len(changed)
    print(f"Price changes: {len(changed)}, new products: {new} (appended to {args.history})")
    for row in sorted(changed, key=lambda row: row["priceDeltaPercent"] or 0):
        print(f'{row["previousPrice"]} -> {row["price"]} {row["currency"]} '
              f'({row["priceDeltaPercent"]} %)  {row["title"][:80]}  {row["url"]}')


if __name__ == "__main__":
    main()
