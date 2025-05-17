import os
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import json
import logging
import re

from scrapper import db_utils

# url = "https://www.moneycontrol.com/mutual-funds/nav/axis-long-term-equity-fund-growth/MAA011"

today = datetime.today().strftime("%Y-%m-%d")
output_dir = Path(f'output/{today}/')
output_dir.mkdir(parents=True, exist_ok=True)


def find_top_ten_holdings(soup: BeautifulSoup, fund_name: str):
    # Find the main container for the portfolio composition
    table = soup.find("table", {"id": "portfolioEquityTable"})

    # Initialize an empty list to store the JSON data
    json_data = []

    # Find all the rows in the table's tbody
    rows = table.find("tbody").find_all("tr")

    # Iterate through each row and extract the relevant data
    for row in rows:
        columns = row.find_all("td")
        stock_link = columns[0].find("a")
        data = {
            "fund_name": fund_name,
            "stock_url": stock_link["href"],
            "Stock_Invested_in": stock_link.text.strip(),
            "Sector": columns[1].text.strip(),
            "Value_Mn": columns[2].text.strip(),
            "pct_of_total_holdings": columns[3].text.strip(),
            "1m_change": columns[4].text.strip(),
            "1Y_Highest_Holding": columns[5].text.strip(),
            "1Y_Lowest_Holding": columns[6].text.strip(),
            "Quantity": columns[7].text.strip(),
            "1M_Change_in_Qty": columns[8].text.strip()
        }
        json_data.append(data)
    # print(json_data)
    return json_data


def read_fund_details(is_testing: bool = True, fund_url: str = None,
                      name: str = None, category: str = None):
    if is_testing:
        content = open('test_input/axis-long-term.txt', encoding="utf8")
    else:
        content = requests.get(fund_url).content

    # print(content)
    soup = BeautifulSoup(content, "html.parser")

    # Find the elements that contain the data
    amount = soup.find("span", class_="amt")
    logging.info(f"Nav: {amount.text.strip()}")

    # Portfolio Date Ex: "30th Apr,2025
    portfolio_date = None
    span = soup.find('span', string=lambda t: t and '(Updated on' in t)
    if span:
        # Extract the text and find the date
        span_text = span.get_text()
        portfolio_date = span_text.replace('(', '').replace(')', '').replace('Updated on', '').strip()
    else:
        portfolio_date = None
   
    date_str = portfolio_date
    date_str_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    date_str_clean = date_str_clean.replace(',', ', ')
    
    portfolio_date = datetime.strptime(date_str_clean, "%d %b, %Y").date()
    
    # data["portfolio_date"] = portfolio_date

    top_ten_holdings = find_top_ten_holdings(soup, name)

    db_utils.save_fund_stocks(top_ten_holdings, db_type='sqlite', category=category, portfolio_date=portfolio_date)

    logging.info(f"Finished... {name}")
    print("---------------------------")
    return top_ten_holdings

# read_fund_details(is_testing=False, url=url)
