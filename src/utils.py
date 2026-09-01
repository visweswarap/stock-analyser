# TODO: Implement later
def cleanup():
    pass

import requests
from bs4 import BeautifulSoup
import re

def extract_holdings(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    holdings = []
    # Find the section containing 'HOLDINGS'
    holdings_section = soup.find(string=re.compile('HOLDINGS', re.IGNORECASE))
    if holdings_section:
        # Find the parent (should be a heading or div)
        parent = holdings_section.find_parent()
        # Find all headings (h2/h3) after the holdings section
        for tag in parent.find_all_next(['h2', 'h3'], limit=30):
            company = tag.get_text(strip=True)
            # Stop if we hit another major section
            if company.upper() in ["ABOUT", "OBJECTIVE", "RISKOMETER", "FUNDAMENTALS", "PORTFOLIO", "PERFORMANCE", "PEERS"]:
                break
            # The next sibling or next element contains the details
            details_tag = tag.find_next_sibling()
            if not details_tag:
                details_tag = tag.find_next(string=True)
            details = details_tag.get_text(strip=True) if details_tag else ''
            # Extract sector, value, weightage, 1M change
            m = re.match(r'([A-Za-z &]+)Value([\d.]+)Weightage([\d.]+%)1M HLD Chg %([\d.\-]+%)', details)
            if m:
                holdings.append({
                    "company": company,
                    "sector": m.group(1).strip(),
                    "value": m.group(2).strip(),
                    "weightage": m.group(3).strip(),
                    "one_month_change": m.group(4).strip()
                })
    return holdings

if __name__ == "__main__":
    url = "https://www.moneycontrol.com/mutual-funds/nav/mirae-asset-midcap-fund-direct-plan/MMA173"
    holdings = extract_holdings(url)
    print(f"Extracted {len(holdings)} holdings:")
    for h in holdings:
        print(h)