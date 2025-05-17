import requests
from bs4 import BeautifulSoup


# TODO: Not used actively. use hni_reader instead.  That will hit the API directly.
@DeprecationWarning
def scrape():
    url = "https://www.moneycontrol.com/india-investors-portfolio/"

    html = requests.get(url).content

    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find the table with id 'investIND'
    table = soup.find('table', {'id': 'investIND'})

    # Extract data from the table
    data = []
    for row in table.find_all('tr')[1:]:  # Skip the header row
        columns = row.find_all('td')
        name = columns[0].find('span', {'itemprop': 'name'}).text.strip()
        networth = columns[1].text.strip().replace(',', '')  # Remove commas from numbers
        url = columns[0].find('a')['href']
        data.append({'Name': name, 'Networth': networth, 'URL': url})

    # Print the extracted data
    for entry in data:
        print(entry)


scrape()
