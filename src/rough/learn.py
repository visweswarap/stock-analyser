"""
MoneyControl Mutual Fund Holdings Scraper
==========================================
Handles the new layout where holdings are shown inside a popup
triggered by clicking the "View All" div:
  <div class="Holdings_web_copyContent__EqL8o">View All ...</div>

Strategy:
  1. Load the page with Playwright (real browser, JS enabled)
  2. Intercept all XHR/fetch network calls to capture the holdings API response
  3. If an API response is found → parse JSON directly (most reliable)
  4. Fallback: click the "View All" div, wait for the popup, then scrape the DOM

Requirements:
  pip install playwright pandas
  playwright install chromium

Usage:
  python mc_holdings_scraper.py
  python mc_holdings_scraper.py --url "https://www.moneycontrol.com/mutual-funds/nav/some-fund/XXXX"
  python mc_holdings_scraper.py --output holdings.csv
"""

import argparse
import json
import re
import time
from typing import List, Dict

import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

DEFAULT_URL = "https://www.moneycontrol.com/mutual-funds/nav/invesco-india-midcap-fund-direct-plan/MLI556"

# CSS selectors to try for the "View All" button (class names are hashed, so we use partial match)
VIEW_ALL_SELECTORS = [
    '[class*="Holdings_web_copyContent"]',
    '[class*="copyContent"]',
    'div:has-text("View All"):near([class*="Holdings"])',
    'text="View All"',
]

# Selectors to find the holdings table/rows inside the popup or on the page
POPUP_SELECTORS = [
    '[class*="Holdings_web_popup"]',
    '[class*="holdingsPopup"]',
    '[class*="holdings_popup"]',
    '[class*="popup"]',
    '[class*="modal"]',
    '[role="dialog"]',
]

HOLDING_ROW_SELECTORS = [
    '[class*="Holdings_web_row"]',
    '[class*="holdingRow"]',
    'table tbody tr',
    '[class*="row"]:has([class*="stock"],[class*="company"],[class*="name"])',
]


def scrape_holdings(url: str, headless: bool = True, timeout_ms: int = 30000) -> List[Dict]:
    """
    Main scraper. Returns a list of dicts, each representing one holding.
    Keys typically: name, percentage, value, sector, type, etc.
    """
    captured_api_responses = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="en-IN",
        )
        page = context.new_page()

        # ── Network interception: capture JSON responses that look like holdings ──
        def handle_response(response):
            url_lower = response.url.lower()
            # Keywords that suggest holdings-related API endpoints
            keywords = ["holding", "portfolio", "scheme", "fund-detail", "mf-detail",
                        "getportfolio", "fundholding", "topholding"]
            if any(k in url_lower for k in keywords):
                try:
                    if "json" in response.headers.get("content-type", ""):
                        data = response.json()
                        captured_api_responses.append({"url": response.url, "data": data})
                        print(f"  [API] Captured: {response.url}")
                except Exception:
                    pass

        page.on("response", handle_response)

        print(f"Loading: {url}")
        try:
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        except PWTimeout:
            print("  networkidle timed out, continuing anyway...")

        page.wait_for_timeout(3000)

        # ── Step 1: Check if any API call already gave us holdings ──
        holdings = _parse_api_responses(captured_api_responses)
        if holdings:
            print(f"  ✓ Extracted {len(holdings)} holdings from API response")
            browser.close()
            return holdings

        # ── Step 2: Click "View All" to trigger the popup ──
        print("  No API data found yet. Trying to click 'View All' button...")
        clicked = False
        for selector in VIEW_ALL_SELECTORS:
            try:
                el = page.wait_for_selector(selector, timeout=5000)
                if el:
                    el.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    el.click()
                    print(f"  Clicked: {selector}")
                    clicked = True
                    break
            except PWTimeout:
                continue

        if not clicked:
            # Try finding any element with "View All" text near "Holdings"
            try:
                page.get_by_text("View All").first.click()
                clicked = True
                print("  Clicked via text match")
            except Exception:
                print("  ⚠ Could not find 'View All' button")

        if clicked:
            page.wait_for_timeout(4000)  # Wait for popup/data to load

            # Check again for API responses triggered by the click
            holdings = _parse_api_responses(captured_api_responses)
            if holdings:
                print(f"  ✓ Extracted {len(holdings)} holdings from API response (post-click)")
                browser.close()
                return holdings

        # ── Step 3: Fallback — scrape the DOM ──
        print("  Falling back to DOM scraping...")
        holdings = _scrape_dom(page)
        browser.close()
        return holdings


def _parse_api_responses(responses: List[Dict]) -> List[Dict]:
    """Try to extract holdings from captured API JSON responses."""
    for item in responses:
        data = item["data"]
        holdings = _extract_holdings_from_json(data)
        if holdings:
            return holdings
    return []


def _extract_holdings_from_json(data, depth=0) -> List[Dict]:
    """Recursively search JSON for a list of holding objects."""
    if depth > 6:
        return []

    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict):
            keys = set(k.lower() for k in first.keys())
            # Likely holdings if keys contain name/company + weight/percentage
            holding_keywords = {"name", "company", "stock", "scrip", "security"}
            weight_keywords = {"weight", "percentage", "percent", "corpus", "allocation", "holding"}
            if holding_keywords & keys and weight_keywords & keys:
                return [_normalize_holding(h) for h in data]
            # Try deeper
            for item in data[:3]:
                result = _extract_holdings_from_json(item, depth + 1)
                if result:
                    return result

    if isinstance(data, dict):
        # Look for common wrapper keys
        priority_keys = ["holdings", "portfolio", "schemes", "topHoldings",
                         "data", "result", "response", "fundHoldings"]
        for key in priority_keys:
            if key in data:
                result = _extract_holdings_from_json(data[key], depth + 1)
                if result:
                    return result
        # Try all keys
        for key, val in data.items():
            result = _extract_holdings_from_json(val, depth + 1)
            if result:
                return result

    return []


def _normalize_holding(raw: dict) -> dict:
    """Normalize a raw holding dict to standard keys."""
    # Map various possible key names to standard names
    key_map = {
        "name": ["name", "companyName", "company_name", "stockName", "stock_name",
                 "scripName", "scip_name", "security_name", "issuerName", "schemeName"],
        "percentage": ["percentage", "weight", "corpus", "allocation", "holding_percentage",
                       "percentOfNav", "percent_of_nav", "nav_percent", "corpusPercent"],
        "value": ["value", "marketValue", "market_value", "amount", "mv"],
        "sector": ["sector", "sectorName", "sector_name", "industry", "industryName"],
        "type": ["type", "assetType", "asset_type", "instrumentType", "category"],
        "shares": ["shares", "quantity", "units", "noOfShares"],
        "isin": ["isin", "ISIN", "isinCode"],
    }
    result = {}
    raw_lower = {k.lower(): v for k, v in raw.items()}
    for std_key, aliases in key_map.items():
        for alias in aliases:
            if alias.lower() in raw_lower:
                result[std_key] = raw_lower[alias.lower()]
                break
    # Include any remaining keys we didn't map
    for k, v in raw.items():
        if k not in result:
            result[k] = v
    return result


def _scrape_dom(page) -> List[Dict]:
    """Scrape holdings from the rendered DOM as a last resort."""
    holdings = []

    # Try to find a popup/modal first, else look at full page
    container = None
    for sel in POPUP_SELECTORS:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                container = el
                print(f"  Found container: {sel}")
                break
        except Exception:
            pass

    search_root = container or page

    # Try to find rows
    for sel in HOLDING_ROW_SELECTORS:
        try:
            rows = (container or page).query_selector_all(sel)
            if len(rows) > 2:
                print(f"  Found {len(rows)} rows via: {sel}")
                for row in rows:
                    cells = row.query_selector_all("td, [class*='cell'], [class*='col']")
                    texts = [c.inner_text().strip() for c in cells if c.inner_text().strip()]
                    if texts:
                        holdings.append({"raw_row": " | ".join(texts)})
                break
        except Exception:
            continue

    if not holdings:
        # Last resort: find all text that looks like percentages with company names
        print("  Trying regex extraction from full page text...")
        text = page.inner_text("body")
        # Look for patterns like "Company Name  X.XX%"
        pattern = re.compile(r'([A-Z][A-Za-z &.-]{5,60})\s+([\d.]+)\s*%')
        matches = pattern.findall(text)
        for name, pct in matches[:60]:
            holdings.append({"name": name.strip(), "percentage": pct})

    return holdings


def main():
    parser = argparse.ArgumentParser(description="Scrape MoneyControl mutual fund holdings")
    parser.add_argument("--url", default=DEFAULT_URL, help="MoneyControl fund URL")
    parser.add_argument("--output", default="holdings.csv", help="Output CSV file")
    parser.add_argument("--json-output", default="holdings.json", help="Output JSON file")
    parser.add_argument("--visible", action="store_true", help="Run browser in visible mode (not headless)")
    args = parser.parse_args()

    holdings = scrape_holdings(args.url, headless=not args.visible)

    if not holdings:
        print("\n⚠ No holdings found. Possible reasons:")
        print("  • MoneyControl may have changed class names again")
        print("  • Bot detection / CAPTCHA (try --visible to see the browser)")
        print("  • Login required to view all holdings")
        return

    df = pd.DataFrame(holdings)
    df.to_csv(args.output, index=False)
    with open(args.json_output, "w") as f:
        json.dump(holdings, f, indent=2)

    print(f"\n✓ Saved {len(holdings)} holdings to {args.output} and {args.json_output}")
    print("\nPreview:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()