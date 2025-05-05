# This is a sample Python script.
import argparse
import logging


def setup_logging():
    # Configure the logging format
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    setup_logging()
    parser = argparse.ArgumentParser(description="stocks scrapper args")
    parser.add_argument('-category', action='store', default='small-cap', dest='category')
    # parser.add_argument('-category', action='store', default='small-cap', dest='category')
    # parser.add_argument('-category', action='store', default='small-cap', dest='category')
    # parser.add_argument('-category', action='store', default='small-cap', dest='category')
    args = parser.parse_args().__dict__
    if args["category"] == 'small-cap':
        from scrapper import small_cap_list_scraper as sc
        sc.get_list(False)
    elif args["category"] == 'mid-cap':
        from scrapper import mid_cap_list_scraper as mc
        mc.get_list(False)
    elif args["category"] == 'large-cap':
        from scrapper import large_cap_list_scraper as lc
        lc.get_list(False)
    else:  # default small cap
        from scrapper import mid_cap_list_scraper as mc
        mc.get_list(False)

