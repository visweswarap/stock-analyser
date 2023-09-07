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

    print(f"low_value : {low_value}")
    print(f"high_value: {high_value}")


read_stck_data()
