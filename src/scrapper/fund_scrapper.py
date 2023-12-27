import os
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import json
import logging

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


def read_fund_details(is_testing: bool = True, fund_url: str = None, name: str = None, category: str = None):
    if is_testing:
        content = open('test_input/axis-long-term.txt', encoding="utf8")
    else:
        content = requests.get(fund_url).content

    # print(content)
    soup = BeautifulSoup(content, "html.parser")

    # Find the elements that contain the data you want
    amount = soup.find("span", class_="amt")
    # fund_name_element = soup.find("h1", class_="b_42")
    print(amount.text.strip())

    top_ten_holdings = find_top_ten_holdings(soup, name)

    db_utils.save_fund_stocks(top_ten_holdings)

    json_string = json.dumps(top_ten_holdings, indent=4)

    basedir = os.path.abspath(os.path.dirname(__file__))

    filename = Path(basedir)/'output'/category/f"{name.replace(' ', '-')}.json"
    filename1 = output_dir/category/f"{name.replace(' ', '-')}.json"

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # print(json_string)

    with open(filename, "w") as file:
        json.dump(top_ten_holdings, file)
        # file.write(json_string)
        file.close()

    with open(filename1, "w") as file1:
        json.dump(top_ten_holdings, file1)
        # file.write(json_string)
        file1.close()

    print(f"File: {filename}")
    print(f"Finished... {name}")
    print("---------------------------")
    return top_ten_holdings

# read_fund_details(is_testing=False, url=url)
