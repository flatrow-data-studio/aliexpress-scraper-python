# AliExpress scraper in Python: product prices, sales and shipping

> This repository calls a paid Apify Actor built by Flatrow Data Studio (the author). Links to apify.com carry the author's affiliate code: the author may earn a commission if you sign up to Apify through them, at no extra cost to you.

A small AliExpress scraper in Python. `scrape.py` searches AliExpress for one or more keywords and saves **one row per product** to CSV: price and original price, discount, rating, exact number of units sold, ship-from country, free shipping, Choice badge, listing date and link, for the **ship-to country and currency you choose**. `monitor_prices.py` turns the same search into an **AliExpress price tracker** that returns only the price changes and new products since its previous run, or only the price drops.

Both scripts run the [AliExpress Products Scraper & Price Tracker](https://apify.com/myth84/aliexpress-search-scraper?fpr=pnpkfc) on Apify through the official `apify-client` package: the Actor runs in Apify's cloud and returns clean rows, so there is no browser, HTML parsing or proxy to maintain on your side. No login, no cookies, and **no personal data**: nothing about buyers or sellers is collected.

## Use cases

- **Dropshipping and product research**: best-selling products of a niche with exact units sold, ratings and ship-from country.
- **Sourcing for a market**: products shipped for free to the United Kingdom or Germany, priced in GBP or EUR.
- **Price drop alerts**: a daily cron job that prints the products whose price went down.
- **Competitor price monitoring**: prices and discounts of a product category across countries and currencies, ready for pandas or Excel.

## Installation

You need Python 3.11 or later and a free [Apify account](https://apify.com/?fpr=pnpkfc) (the free plan includes monthly credit).

```bash
git clone https://github.com/flatrow-data-studio/aliexpress-scraper-python.git
cd aliexpress-scraper-python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export APIFY_TOKEN="<your-apify-token>"   # Apify Console > Settings > API & Integrations
```

## Run it

```bash
# 60 best-selling wireless earbuds shipped to the United States
python scrape.py "wireless earbuds" --sort orders --max-results 60

# LED strips shipped for free to the United Kingdom, in GBP, rated 4.5 or more
python scrape.py "led strip lights" --country GB --currency GBP --free-shipping --min-rating 4.5
```

The script writes `aliexpress_products.csv` (change it with `--output`) and prints the five best sellers. Other options: several keywords in one run (`"phone case" "screen protector"`), `--sort` (`default`, `orders`, `price_asc`, `price_desc`), `--price-max`, `--min-sold 1000`, `--choice-only` for the Choice badge, and `--max-charge 0.50` to stop a run once it has cost 50 cents; `python scrape.py --help` lists them all. Products left out by a filter are never charged.

## Track prices every day

```bash
python monitor_prices.py "wireless earbuds" --sort orders --store earbuds-daily
```

The first run records the price of every product as the reference (they all come back as `new`). From the second run on, only the new products and the products whose price changed are returned, with `previousPrice`, `priceDelta` and `priceDeltaPercent`; they are printed and appended to `aliexpress_price_changes.csv`. Add `--only-drops` to get only the price drops: the first run then records the prices without returning anything. The reference lives in a key-value store of your Apify account named after `--store` (use one name per schedule), so the script can run from cron on any machine:

```bash
0 7 * * * cd /path/to/aliexpress-scraper-python && .venv/bin/python monitor_prices.py "wireless earbuds" --sort orders --store earbuds-daily >> tracker.log 2>&1
```

Keep the same keywords, country, currency, sort and filters from run to run: changing them starts a new reference.

## Sample output

One real row from a "wireless earbuds" search shipped to the United States, key columns only:

```json
{
  "platformProductId": "3256812817428248",
  "title": "2026 New Air 3【 Pro3 】 Bluetooth Wireless Earbuds With Heart Rate Monitoring, Active Noise Cancellation Headphones, Waterproof for Daily Use, For IPhone IOS Smartphone, Gaming /Sports /Fitness Earphones.",
  "currency": "USD",
  "price": 27.29,
  "originalPrice": 64.02,
  "discountPercent": 57,
  "rating": 4,
  "soldCount": 32,
  "shippingFree": true,
  "shipsFrom": "US",
  "isChoice": false,
  "listedAt": "2026-08-20"
}
```

## Columns

`scrape.py` writes these columns:

| Column | Meaning |
|---|---|
| `platformProductId` | AliExpress product id |
| `title` | Product title |
| `currency` | Currency of the prices |
| `price` | Current price |
| `originalPrice` | Price before the discount |
| `discountPercent` | Discount against `originalPrice` |
| `rating` | Average rating out of 5 |
| `soldCount` | Exact number of units sold |
| `shippingFree` | Free shipping to your ship-to country |
| `shipsFrom` | Ship-from country (US, CN, FR...) |
| `isChoice` | AliExpress Choice badge |
| `isSponsored` | Sponsored result |
| `listedAt` | Listing date |
| `searchQuery` | The keywords that found the product |
| `searchRank` | Position in the results |
| `url` | Product link |

The dataset of each run has more columns (image, delivery estimate, ship-to country...): add their names to `COLUMNS` in `scrape.py`. The full list is on the [Actor page](https://apify.com/myth84/aliexpress-search-scraper?fpr=pnpkfc).

## Pricing

The Actor is pay-per-event: from $1.80 per 1,000 products on Apify's Free plan, lower on paid plans. Apify's free monthly credit of $5 covers about 2,777 products. You pay per product saved and nothing else; `--max-results` caps every keyword of a run, products left out by a filter are never charged, and in price-tracking mode only the new and changed products (or only the drops) are saved and charged.

## FAQ

**Do I need to write a scraper or run a browser?** No. The Actor runs in Apify's cloud and is kept up to date when AliExpress changes its pages; your script receives JSON rows.

**Why does the sort look approximate across pages?** AliExpress sorts each page of 60 products on its own: the order is exact within a page and approximate across pages. Sort the CSV by `price` for a strict order.

**Is there personal data in the output?** No. Rows contain product facts only: no seller, store or buyer, and no review text or reviewer. Use the data for analysis, respect AliExpress's terms and the law of your country, and do not republish listings.

## Related

Other Python examples by Flatrow Data Studio, all with a CSV export and a price tracker:

- [amazon-scraper-python](https://github.com/flatrow-data-studio/amazon-scraper-python): Amazon product prices, ratings and price drops.
- [ebay-scraper-python](https://github.com/flatrow-data-studio/ebay-scraper-python): eBay listing prices, condition and units sold.
- [airbnb-scraper-python](https://github.com/flatrow-data-studio/airbnb-scraper-python): Airbnb listings, nightly and total prices, ratings and availability.
- [booking-scraper-python](https://github.com/flatrow-data-studio/booking-scraper-python): Booking.com hotel prices, taxes, review scores and stars.
- [google-hotels-scraper-python](https://github.com/flatrow-data-studio/google-hotels-scraper-python): Google Hotels prices, with every booking site's rate.

## License

MIT, see [LICENSE](LICENSE). AliExpress is a trademark of its owner; this project is not affiliated with AliExpress.
