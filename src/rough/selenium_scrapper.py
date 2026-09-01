"""
MoneyControl Mutual Fund Holdings Scraper — Selenium
======================================================
Steps:
  1. Navigate to the fund URL (with #holdings anchor)
  2. Scroll to Holdings section
  3. Click "View All" button → popup opens
  4. Scrape the popup table into JSON

Install:
  pip install selenium webdriver-manager

Usage:
  python mc_holdings_selenium.py
  python mc_holdings_selenium.py --url "https://www.moneycontrol.com/mutual-funds/nav/hsbc-mid-cap-fund-direct-plan/MCC275#holdings"
  python mc_holdings_selenium.py --all-funds   # reads from fund_urls.txt, one URL per line
"""

import argparse
import json
import time
import re
import sys
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException
)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False
    print("Tip: pip install webdriver-manager to auto-manage ChromeDriver")


# ── Constants ──────────────────────────────────────────────────────────────────

DEFAULT_URL = "https://www.moneycontrol.com/mutual-funds/nav/hsbc-mid-cap-fund-direct-plan/MCC275#holdings"
WAIT_TIMEOUT = 20   # seconds for explicit waits
LOAD_PAUSE   = 3    # seconds after page load
POPUP_PAUSE  = 3    # seconds after popup opens

# Selectors for "View All" button — tries each in order until one works.
# Uses CSS partial-class match so hashed suffixes (e.g. __EqL8o) don't matter.
VIEW_ALL_SELECTORS = [
    "[class*='Holdings'][class*='copyContent']",        # e.g. Holdings_web_copyContent__EqL8o
    "[class*='holdings'][class*='viewAll']",
    "[class*='Holdings'][class*='viewAll']",
    "//div[contains(@class,'Holdings') and contains(text(),'View All')]",  # XPath fallback
    "//div[contains(text(),'View All')]",                                   # broad XPath
    "//span[contains(text(),'View All')]",
    "//a[contains(text(),'View All')]",
]

# Selectors for the modal/popup container
MODAL_SELECTORS = [
    "[class*='Holdings'][class*='popup']",
    "[class*='holdings'][class*='modal']",
    "[class*='holdingsModal']",
    "[class*='popupContainer']",
    "[role='dialog']",
    "[class*='modal'][class*='show']",
    "[class*='Popup']",
    "[class*='Modal']",
]

# Selectors for individual holding rows inside the popup
ROW_SELECTORS = [
    "[class*='Holdings'][class*='row']",
    "[class*='holdings'][class*='row']",
    "[class*='holdingItem']",
    "[class*='tableRow']",
    "table tbody tr",
    "[class*='row']:not([class*='header'])",
]


# ── Driver setup ──────────────────────────────────────────────────────────────

def build_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--lang=en-IN")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    if USE_WDM:
        service = Service(ChromeDriverManager().install())
    else:
        service = Service()  # assumes chromedriver is on PATH

    driver = webdriver.Chrome(service=service, options=options)
    # Mask webdriver flag
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"}
    )
    return driver


# ── Step helpers ───────────────────────────────────────────────────────────────

def load_page(driver, url: str):
    """Navigate to the URL and wait for the page to settle."""
    print(f"\n[1] Loading: {url}")
    driver.get(url)
    time.sleep(LOAD_PAUSE)

    # Dismiss any cookie/notification banners
    for banner_sel in [
        "[id*='cookie'] button", "[class*='cookie'] button",
        "[class*='consent'] button", "[id*='gdpr'] button",
        "button[aria-label*='close']", "button[aria-label*='Close']",
    ]:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, banner_sel)
            btn.click()
            time.sleep(0.5)
        except Exception:
            pass


def scroll_to_holdings(driver):
    """Scroll the holdings section into view."""
    print("[2] Scrolling to holdings section...")
    for sel in ["[class*='Holdings']", "#holdings", "[id*='holdings']"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(1)
            print(f"   Scrolled to: {sel}")
            return
        except NoSuchElementException:
            pass
    # Fallback: scroll down 60% of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
    time.sleep(1)


def click_view_all(driver) -> bool:
    """Find and click the 'View All' button. Returns True if successful."""
    print("[3] Clicking 'View All'...")
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    for sel in VIEW_ALL_SELECTORS:
        try:
            by = By.XPATH if sel.startswith("//") else By.CSS_SELECTOR
            el = wait.until(EC.presence_of_element_located((by, sel)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.5)
            try:
                el.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", el)
            print(f"   ✓ Clicked via: {sel}")
            time.sleep(POPUP_PAUSE)
            return True
        except TimeoutException:
            continue
        except Exception as e:
            print(f"   ✗ {sel}: {e}")
            continue

    print("   ✗ Could not find 'View All' button")
    return False


def find_modal(driver):
    """Return the modal element, or None."""
    print("[4] Locating popup/modal...")
    for sel in MODAL_SELECTORS:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, sel))
            )
            print(f"   Found modal: {sel}")
            return el
        except TimeoutException:
            continue
    print("   ⚠ Modal not found by known selectors, will search full page")
    return None


# ── Data extraction ────────────────────────────────────────────────────────────

def extract_holdings_from_modal(driver, modal_el) -> list:
    """Try multiple strategies to extract holdings from the popup."""

    root = modal_el or driver
    
    # Strategy A: parse a <table> inside the modal (TRY THIS FIRST)
    holdings = _extract_table(root, driver)
    if holdings:
        return holdings

    # Strategy B: look for structured rows in the modal
    holdings = _extract_rows(root, driver)
    if holdings:
        return holdings

    # Strategy C: get all text and regex-parse it
    holdings = _extract_by_regex(root)
    return holdings


def _extract_rows(root, driver) -> list:
    """Find holding rows via known CSS patterns."""
    
    # Special handling for holdings displayed as cards (not traditional rows)
    try:
        cards = root.find_elements(By.CSS_SELECTOR, "[class*='stockCard']") if hasattr(root, 'find_elements') else driver.find_elements(By.CSS_SELECTOR, "[class*='stockCard']")
        if len(cards) > 0:
            print(f"   Found {len(cards)} stock cards")
            holdings = []
            for card in cards:
                holding = {}
                
                # Extract title from h2 tag
                try:
                    title = card.find_element(By.TAG_NAME, "h2").text.strip()
                    holding["name"] = title
                except NoSuchElementException:
                    pass
                
                # Extract sector/category
                try:
                    sector = card.find_element(By.CSS_SELECTOR, "[class*='company']").text.strip()
                    holding["sector"] = sector
                except NoSuchElementException:
                    pass
                
                # Extract value and weightage from content divs
                try:
                    contents = card.find_elements(By.CSS_SELECTOR, "[class*='content']")
                    for content in contents:
                        name_el = content.find_element(By.CSS_SELECTOR, "[class*='name']").text.strip()
                        value_el = content.find_element(By.CSS_SELECTOR, "[class*='value']").text.strip()
                        holding[name_el.lower().replace(" ", "_")] = value_el
                except NoSuchElementException:
                    pass
                
                if "name" in holding:
                    holdings.append(holding)
            
            if holdings:
                return holdings
    except Exception:
        pass
    
    # Fallback: original row-based extraction
    # SKIP table rows — let _extract_table handle tables
    row_selectors_skip_tables = [
        "[class*='Holdings'][class*='row']",
        "[class*='holdings'][class*='row']",
        "[class*='holdingItem']",
        "[class*='tableRow']",
        # "table tbody tr",  # COMMENT THIS OUT
        "[class*='row']:not([class*='header'])",
    ]
    
    for sel in row_selectors_skip_tables:
        try:
            # ...existing code...
            if hasattr(root, 'find_elements'):
                rows = root.find_elements(By.CSS_SELECTOR, sel)
            else:
                rows = driver.find_elements(By.CSS_SELECTOR, sel)

            if len(rows) < 2:
                continue

            print(f"   Found {len(rows)} rows via: {sel}")
            holdings = []
            for row in rows:
                cells = row.find_elements(By.XPATH, ".//*[self::td or self::th or self::div or self::span][not(.//*[self::div or self::span])]")
                texts = [c.text.strip() for c in cells if c.text.strip()]
                if not texts:
                    texts = [row.text.strip()]
                if texts and len(texts[0]) > 1:
                    holdings.append({"raw": texts})
            if holdings:
                return _parse_raw_rows(holdings)
        except Exception:
            continue
    return []


def _extract_table(root, driver) -> list:
    """Parse a standard HTML table with nested sector/weightage spans."""
    try:
        tables = (root if hasattr(root, 'find_elements') else driver).find_elements(By.TAG_NAME, "table")
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) < 2:
                continue

            # Extract headers
            header_row = rows[0]
            headers = [th.text.strip() for th in header_row.find_elements(By.XPATH, ".//th|.//td")]
            
            holdings = []
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                
                holding = {}
                
                # Parse each cell
                for cell_idx, cell in enumerate(cells):
                    if cell_idx == 0:
                        # For first column: extract stock name (direct text only, no span)
                        # Get direct text node using JavaScript
                        stock_name = driver.execute_script(
                            "return Array.from(arguments[0].childNodes).filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('').trim();",
                            cell
                        )
                        if not stock_name:
                            # Fallback: get text before the first span
                            stock_name = cell.text.split('\n')[0].strip()
                        
                        holding["name"] = stock_name
                        
                        # Get sector from span
                        try:
                            sector_span = cell.find_element(By.TAG_NAME, "span")
                            holding["sector"] = sector_span.text.strip()
                        except NoSuchElementException:
                            pass
                    
                    elif cell_idx == 1:
                        # For second column: value + weightage
                        cell_text = cell.text.strip()
                        lines = cell_text.split('\n')
                        if lines:
                            holding["value"] = lines[0].strip()
                            if len(lines) > 1:
                                holding["weightage"] = lines[1].strip()
                    
                    elif cell_idx == 2:
                        # For third column: 1M HLD Chg %
                        holding["1m_hld_chg"] = cell.text.strip()
                
                # Only add if we got a name
                if "name" in holding and holding["name"]:
                    holdings.append(holding)
            
            if holdings:
                print(f"   Parsed table: {len(holdings)} rows")
                return holdings
    except Exception as e:
        print(f"   Table parse error: {e}")
    
    return []

def _extract_by_regex(root) -> list:
    """Last resort: regex parse the modal text."""
    try:
        text = root.text if hasattr(root, 'text') else ""
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        holdings = []
        # Pattern: line contains a % value — assume it's a holding line
        pct_re = re.compile(r'(\d+\.?\d*)\s*%')
        num_re = re.compile(r'[\d,]+\.?\d*')

        for i, line in enumerate(lines):
            if pct_re.search(line):
                pct = pct_re.search(line).group(1)
                # Name is likely the previous non-numeric line
                name = lines[i-1] if i > 0 and not pct_re.search(lines[i-1]) else line
                numbers = num_re.findall(line)
                holdings.append({
                    "name": name,
                    "percentage": pct,
                    "numbers_in_row": numbers,
                    "raw_line": line,
                })

        print(f"   Regex extracted {len(holdings)} potential holdings")
        return holdings
    except Exception as e:
        print(f"   Regex extraction error: {e}")
        return []


def _parse_raw_rows(raw_holdings: list) -> list:
    """
    Convert raw cell arrays into structured dicts.
    Tries to detect which cell is: name, %, value, sector.
    """
    pct_re   = re.compile(r'^[\d.]+$')
    money_re = re.compile(r'^[\d,]+\.?\d*$')

    parsed = []
    for item in raw_holdings:
        cells = item.get("raw", [])
        if not cells:
            continue

        holding = {}

        # Heuristic: first long-ish text field = name
        for c in cells:
            if len(c) > 3 and not pct_re.match(c) and not money_re.match(c.replace(",","")):
                holding.setdefault("name", c)
                break

        # Find percentage (looks like "7.23" or "7.23%")
        for c in cells:
            clean = c.replace("%", "").strip()
            if pct_re.match(clean) and float(clean) <= 100:
                holding.setdefault("percentage", clean)
                break

        # Remaining numerics → value, shares, etc.
        numeric_fields = ["value_cr", "shares", "extra"]
        ni = 0
        for c in cells:
            clean = c.replace(",", "").replace("%", "").strip()
            if pct_re.match(clean) and c not in holding.values():
                if ni < len(numeric_fields):
                    holding[numeric_fields[ni]] = c
                    ni += 1

        holding["_raw_cells"] = cells
        parsed.append(holding)

    return parsed


# ── Fund metadata ─────────────────────────────────────────────────────────────

def extract_fund_meta(driver, url: str) -> dict:
    """Extract fund name and as-of date from the page."""
    meta = {"url": url, "scraped_at": datetime.now().isoformat()}
    try:
        meta["fund_name"] = driver.find_element(
            By.CSS_SELECTOR, "h1, [class*='fundName'], [class*='fund_name'], [class*='FundName']"
        ).text.strip()
    except Exception:
        pass
    try:
        # Look for "as of" or "portfolio date" text
        for sel in ["[class*='asOf']", "[class*='portfolioDate']", "[class*='date']"]:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els:
                if "as of" in el.text.lower() or re.search(r'\d{4}', el.text):
                    meta["portfolio_date"] = el.text.strip()
                    break
    except Exception:
        pass
    return meta


# ── Main scrape function ──────────────────────────────────────────────────────

def scrape_fund(url: str, headless: bool = False, save_screenshot: bool = True) -> dict:
    """
    Full pipeline for one fund URL.
    Returns {"meta": {...}, "holdings": [...]}
    """
    driver = build_driver(headless=headless)
    result = {"meta": {}, "holdings": []}

    try:
        # 1. Load
        load_page(driver, url)

        # 2. Scroll to holdings
        scroll_to_holdings(driver)

        # 3. Click View All
        clicked = click_view_all(driver)
        if not clicked:
            print("   Will try to scrape whatever is visible without clicking")

        # 4. Find modal
        modal = find_modal(driver)

        # 5. Screenshot of popup
        if save_screenshot and modal:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"popup_{ts}.png"
            modal.screenshot(fname)
            print(f"[5] Screenshot saved: {fname}")
        elif save_screenshot:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"page_{ts}.png"
            driver.save_screenshot(fname)
            print(f"[5] Full-page screenshot saved: {fname}")

        # 6. Extract holdings
        print("[6] Extracting holdings data...")
        holdings = extract_holdings_from_modal(driver, modal)
        print(f"   → {len(holdings)} holdings extracted")
        print(json.dumps(holdings))

        # 7. Fund metadata
        meta = extract_fund_meta(driver, url)

        result = {"meta": meta, "holdings": holdings}

    except Exception as e:
        print(f"\n✗ Error: {e}")
        driver.save_screenshot("error_screenshot.png")
        raise
    finally:
        driver.quit()

    return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape MoneyControl fund holdings via Selenium")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--headless", action="store_true", help="Run Chrome headlessly")
    parser.add_argument("--no-screenshot", action="store_true", help="Skip screenshots")
    parser.add_argument("--output", default="holdings_output.json", help="Output JSON file")
    parser.add_argument("--all-funds", action="store_true",
                        help="Read URLs from fund_urls.txt (one per line) and scrape all")
    args = parser.parse_args()

    urls = []
    if args.all_funds:
        fp = Path("fund_urls.txt")
        if not fp.exists():
            print("fund_urls.txt not found. Create it with one MoneyControl URL per line.")
            sys.exit(1)
        urls = [l.strip() for l in fp.read_text().splitlines() if l.strip() and not l.startswith("#")]
    else:
        urls = [args.url]

    all_results = []
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"Fund {i}/{len(urls)}: {url}")
        print('='*60)
        try:
            result = scrape_fund(
                url=url,
                headless=args.headless,
                save_screenshot=not args.no_screenshot,
            )
            all_results.append(result)

            # Pretty print preview
            print("\nSample holdings:")
            for h in result["holdings"][:5]:
                print(f"  {h}")

            # Throttle between funds to avoid rate limiting
            if i < len(urls):
                wait = 5
                print(f"\nWaiting {wait}s before next fund...")
                time.sleep(wait)

        except Exception as e:
            print(f"  FAILED: {e}")
            all_results.append({"meta": {"url": url, "error": str(e)}, "holdings": []})

    # Save all results
    out_path = Path(args.output)
    out_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\n{'='*60}")
    print(f"✓ Saved {len(all_results)} fund(s) to {out_path}")

    # Summary
    for r in all_results:
        name = r["meta"].get("fund_name", r["meta"].get("url", "?"))
        count = len(r["holdings"])
        print(f"  {name}: {count} holdings")


if __name__ == "__main__":
    main()