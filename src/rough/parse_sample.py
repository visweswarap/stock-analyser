import sys
import json
from bs4 import BeautifulSoup

# Usage: python parse_sample.py sample.html
html_path = sys.argv[1]
with open(html_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

holdings_table = soup.find('table', id='portfolioEquityTable')
top_10_holdings = []
if holdings_table:
    headers = [th.get_text(strip=True) for th in holdings_table.find_all('th')]
    for tr in holdings_table.find('tbody').find_all('tr')[:10]:
        cells = tr.find_all('td')
        if len(cells) >= 2:
            holding = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    if i == 0:
                        a = cell.find('a')
                        holding[headers[i]] = a.get_text(strip=True) if a else cell.get_text(strip=True)
                    else:
                        holding[headers[i]] = cell.get_text(strip=True)
                else:
                    holding[f'col_{i+1}'] = cell.get_text(strip=True)
            top_10_holdings.append(holding)

print(json.dumps(top_10_holdings, indent=2, ensure_ascii=False))
