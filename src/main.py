# This is a sample Python script.
import argparse

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
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
    else:  # "default small cap"
        from scrapper import mid_cap_list_scraper as mc
        mc.get_list(False)

