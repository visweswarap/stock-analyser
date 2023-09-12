import re

import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/india/stockpricequote/steel-tubes-pipes/aplapollotubes/BT09"


def read_stck_data(stock_url: str = None):
    content = requests.get(url).content

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Find the div with class "nsecp" which contains the price value
    price_div = soup.find("div", class_="nsecp")

    print("####################\n")

    # Extract the price value from the 'rel' attribute
    price_value = price_div.get("rel")
    print(f"price_value: {price_value}")

    # Find the div elements with class "nseL52" and "nseH52" for 52-week low and high
    low_value = soup.find("div", class_="nseL52").text.strip()
    high_value = soup.find("div", class_="nseH52").text.strip()

    stock_overview_dict = {}

    # Find and extract the data
    overview_tables = soup.find_all('div', class_='oview_table')

    for table in overview_tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                key: str = cols[0].text.strip()
                if key == 'i\n\n\n\xa0VWAP':
                    print("its VWAP")
                    key = 'Volume-Weighted-Average-Price-VWAP'
                elif key.startswith('Mkt-Cap-(Rs.-Cr.)'):
                    key = "market-cap"
                key = key.replace(" ", "-")
                value: str = cols[1].text.strip()
                # re.sub(r'[^\w\s]', '', value)
                if "\n" in value:
                    value = value.split("\n")[0]
                stock_overview_dict[key] = value

    # Print the scraped data dictionary
    print(stock_overview_dict)


def read_volume_data(soup: None):
    content = requests.get(url).content

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Find the elements you want to scrape
    priv_head = soup.find('div', class_='priv_head')
    chart_volume = soup.find('div', class_='chart_volume')

    # Extract text content from the elements
    priv_head_text = priv_head.text.strip()
    chart_volume_text = chart_volume.text.strip()

    # Create a dictionary to store the scraped data
    scraped_data = {
        'priv_head': priv_head_text,
        'chart_volume': chart_volume_text
    }


def read_broker_recommendations(soup: None):
    if soup is None:
        content = requests.get(url).content

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
    # Find the div with id "broker_research"
    broker_research_div = soup.find("div", {"id": "broker_research"})

    # Initialize an empty list to store the scraped data
    scraped_data = []

    # Find all the divs with class "brrs_bx grey_bx" inside the broker_research_div
    research_blocks = broker_research_div.find_all("div", class_="brrs_bx grey_bx")

    # Iterate through each research block
    for research_block in research_blocks:
        # Extract the date
        date = research_block.find("div", class_="br_date").text.strip()

        # Extract the broker name
        broker_name = research_block.find("div", class_="brstk_name").h3.text.strip()

        # Extract the download link
        download_link = research_block.find("a")["href"]

        # Extract the recommendation and target price
        recommendation_table = research_block.find("table")
        reco_price = recommendation_table.find_all("strong")[0].text
        target_price = recommendation_table.find_all("strong")[1].text

        # Create a dictionary to store the scraped data for this block
        data = {
            "Date": date,
            "Broker Name": broker_name,
            "Download Link": download_link,
            "Recommendation Price": reco_price,
            "Target Price": target_price
        }

        # Append the data dictionary to the list
        scraped_data.append(data)

    print(scraped_data)

read_broker_recommendations(None)
