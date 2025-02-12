import json
import logging
import os
import time

import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html"


def get_list():
    content = requests.get(url).content

    soup = BeautifulSoup(content, 'html.parser')

    table_body = soup.find('tbody')

    data = []
    funds_urls = []

    for row in table_body.find_all('tr'):
        time.sleep(3)
        print(row)
    #
    # # Convert the data list to JSON
    # json_data = json.dumps(data, indent=4)
    # write_to_funds_list(data=data, file_path=None)


get_list()
