import json
import logging
import os
import time

import requests
from bs4 import BeautifulSoup

from src.scrapper import fund_scrapper

url = "https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html"


def get_list(is_testing: bool = True):
    content = None
    if is_testing:
        content = open("test_input/small-cap-equity-funds.html", encoding="utf8")
    else:
        content = requests.get(url).content

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Find the table body containing the data
    table_body = soup.find('tbody')

    # Initialize a list to store the scraped data
    data = []
    small_cap_funds_urls = []

    # Iterate through each row in the table body
    for row in table_body.find_all('tr'):
        time.sleep(3)
        fund_info = {}

        # Extract scheme name and URL
        scheme_link = row.find('a', class_='robo_medium')
        # print(scheme_link.text)
        refined_scheme_name = None
        if "\n" in scheme_link.text:
            refined_scheme_name = str(scheme_link.text).replace('\n', '').replace("                                           ", "")
        else:
            refined_scheme_name = scheme_link.text

        logging.info("\n###################")
        logging.info(refined_scheme_name)

        fund_info['Scheme-Name'] = refined_scheme_name
        fund_info['URL'] = scheme_link['href']

        # Extract other data
        cells = row.find_all('td')
        plan = cells[1].text.strip()
        fund_info['Plan'] = plan
        fund_info['Category'] = cells[2].text.strip()
        fund_info['Crisil Rank'] = cells[3].text.strip()
        fund_info['AuM (Cr)'] = cells[4].text.strip()

        try:
            if plan == "Direct Plan":
                if fund_info["URL"]:
                    logging.info(f"#### scrapping {fund_info['URL']} ####")
                    # Append the fund_info to the data list
                    data.append(fund_info)
                    small_cap_funds_urls.append(fund_info["URL"])
                    fund_scrapper.read_fund_details(False, fund_info["URL"], name=refined_scheme_name, category="small-cap")
                else:
                    logging.error(f"Fund URL is empty for: {refined_scheme_name}")
        except Exception as ex:
            logging.error(ex)

    # Convert the data list to JSON
    json_data = json.dumps(data, indent=4)

    # Print the JSON data
    # print(json_data)
    filename = f"output/funds/small-cap-funds.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        json.dump(data, file)


get_list(is_testing=False)