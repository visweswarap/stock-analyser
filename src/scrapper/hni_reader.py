import logging
import time

import requests
from bs4 import BeautifulSoup


def setup_logging():
    # Configure the logging format
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)


def read():
    """
    {
        "name":"Seetha Kumari",
        "noOfCompanies":10,
        "netWorth":"436",
        "portfolioId":53795,
        "slug":"seetha-kumari",
        "displayLock":"N"
    }
    :return:
    """
    setup_logging()
    individual_investors = []

    url = "https://www.moneycontrol.com/india-investors-portfolio/index-pagination?page={}&classic=true"
    hni_portfolio_url = "https://www.moneycontrol.com/india-investors-portfolio/{}/holdings"
    for i in range(1, 5):
        result = requests.get(url.format(i)).json()
        for investor in result['investIND']:
            individual_investors.append(investor)
            portfolio = read_hni_portfolio(hni_portfolio_url.format(investor['slug']))
            investor["portfolio"] = portfolio
            logging.info("Going to sleep for 5 seconds before reading another HNI.")
            time.sleep(5)
            logging.info("Back after 5 seconds sleep.  My alarm works :(")
        print(result)

    print(individual_investors)


def read_hni_portfolio(url: str):
    logging.info(f"Going to read: {url}")

    html_content = requests.get(url).content

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table with the specified ID
    table = soup.find('table', {'id': 'hold_table'})

    # Check if the table exists
    if table:
        entries = []
        # Initialize lists to store data

        count = 0
        # Iterate over table rows skipping the header row
        for row in table.find_all('tr')[1:]:
            try:
                # Extract data from each row
                stock_name = row.find('td', {'class': f'name_{count}'}).text.strip()
                quantity_held = row.find('td', {'class': f'quantityHeld_{count}'}).text.strip()
                holding_pct = row.find('td', {'class': f'holdingPer_{count}'}).text.strip()
                change_from_prev_qtr_value = row.find('td', {'class': f'changePrev_{count}'}).text.strip()
                holding_value = row.find('td', {'class': f'holdingVal_{count}'}).text.strip()

                entries.append({"stock_name": stock_name,
                                "quantity_held": quantity_held,
                                "holding_pct": holding_pct,
                                "change_from_prev_qtr_value": change_from_prev_qtr_value,
                                "holding_value": holding_value})
                # print(entries)
                count += 1
            except Exception as ex:
                logging.error(ex)
        return entries
    else:
        print("Table with ID 'hold_table' not found.")


read()
