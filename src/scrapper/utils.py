import json
import logging
import time

from bs4 import ResultSet

from scrapper import fund_scrapper
from scrapper.db_utils import write_to_funds_list


def scrape_each_item(data: list, funds_urls: list, category: str, row: ResultSet):
    fund_info = {}

    # Extract scheme name and URL
    scheme_link = row.find('a', class_='robo_medium')
    refined_scheme_name = None
    if "\n" in scheme_link.text:
        refined_scheme_name = str(scheme_link.text).replace('\n', '').replace(
            "                                           ", "")
    else:
        refined_scheme_name = scheme_link.text

    logging.info("\n###################")
    logging.info(f"refined_scheme_name: {refined_scheme_name}")

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
                funds_urls.append(fund_info["URL"])
                fund_scrapper.read_fund_details(False, fund_info["URL"],
                                                name=refined_scheme_name,
                                                category=category)
                logging.info("Sleeping for 2 seconds... zzz ZZZ")
                time.sleep(2)
                logging.info("Ahh... That's a short sleep.  I am back.")
            else:
                logging.error(f"Fund URL is empty for: {refined_scheme_name}")
    except Exception as ex:
        logging.error(ex)

    # Convert the data list to JSON

    write_to_funds_list(data=data, file_path=None)