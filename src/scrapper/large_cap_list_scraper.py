import requests
from bs4 import BeautifulSoup
import logging

def get_list(save_to_file=False):
    """
    Scrapes large-cap fund data from Moneycontrol and prints or saves the results.
    """
    url = "https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/large-cap-fund.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch data: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "performanceTbl"})
    if not table:
        logging.error("Could not find the data table on the page.")
        return []

    funds = []
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    for row in table.find_all("tr")[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) == len(headers):
            fund = dict(zip(headers, cols))
            funds.append(fund)

    if save_to_file:
        import json
        import os
        output_dir = os.path.join(os.path.dirname(__file__), "output", "funds")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "large-cap-funds.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(funds, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved {len(funds)} funds to {output_path}")
    else:
        for fund in funds:
            print(fund)
    return funds
