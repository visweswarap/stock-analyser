import requests
from bs4 import BeautifulSoup
import json
import re

def each_fund_details(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    data = {}

    # Portfolio Date
    portfolio_date = None
    span = soup.find('span', string=lambda t: t and '(Updated on' in t)
    if span:
        # Extract the text and find the date
        span_text = span.get_text()
        portfolio_date = span_text.replace('(', '').replace(')', '').replace('Updated on', '').strip()
    else:
        portfolio_date = None
    data["portfolio_date"] = portfolio_date

    # Asset Allocation and Equity Breakdown from both investment_block divs
    investment_blocks = soup.find_all('div', class_='investment_block')
    investment_json = {}
    if len(investment_blocks) >= 2:
        pass
    data["investment_breakdown"] = investment_json

    # Find the correct Top 10 Holdings table in local HTML (sample.html)
    top_10_holdings = []
    holdings_table = soup.find('table', id='portfolioEquityTable')
    if holdings_table:
        headers = [th.get_text(strip=True) for th in holdings_table.find_all('th')]
        for tr in holdings_table.find('tbody').find_all('tr')[:10]:
            cells = tr.find_all('td')
            if len(cells) >= 2:
                holding = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        # For the first column, extract the stock name from the <a> tag if present
                        if i == 0:
                            a = cell.find('a')
                            holding[headers[i]] = a.get_text(strip=True) if a else cell.get_text(strip=True)
                        else:
                            holding[headers[i]] = cell.get_text(strip=True)
                    else:
                        holding[f'col_{i+1}'] = cell.get_text(strip=True)
                top_10_holdings.append(holding)
    data["top_10_holdings"] = top_10_holdings

    return data

fund_categories = {
    "small-cap": "https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html"
}
def init():
    for category, url in fund_categories.items():
        funds = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        table_body = soup.find('tbody')
        if table_body:
            for row in table_body.find_all('tr'):
                fund_info = {}
                scheme_link = row.find('a', class_='robo_medium')
                if not scheme_link:
                    continue
                refined_scheme_name = scheme_link.text.strip().replace('\n', '').replace("                                           ", "")
                fund_info['Scheme-Name'] = refined_scheme_name
                fund_info['URL'] = scheme_link['href']
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                fund_info['Plan'] = cells[1].text.strip()
                fund_info['Category'] = category
                fund_info['Crisil Rank'] = cells[3].text.strip()
                fund_info['AuM (Cr)'] = cells[4].text.strip()
                if fund_info['Plan'] == "Direct Plan":
                    fund_info['Plan'] = "Direct"
                    details = each_fund_details(fund_info['URL'])
                    fund_info["details"] =  details
                    funds.append(fund_info)
        # Save to JSON
        with open(f"{category}-funds.json", "w", encoding="utf-8") as f:
            json.dump(funds, f, indent=2, ensure_ascii=False)
        print(f"Extracted {len(funds)} funds for {category}.")

if __name__ == "__main__":
    # init()
    response = each_fund_details("https://www.moneycontrol.com/mutual-funds/nav/motilal-oswal-midcap-fund-direct-plan-growth/MMO027")
    print(json.dumps(response, indent=2, ensure_ascii=False))