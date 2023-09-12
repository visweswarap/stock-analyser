# This is a sample Python script.
import argparse

from scrapper import small_cap_list_scraper as sc


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    parser = argparse.ArgumentParser(description="stocks scrapper args")
    parser.add_argument('-category', action='store', default='small-cap', dest='category')
    # parser.add_argument('-category', action='store', default='small-cap', dest='category')
    # parser.add_argument('-category', action='store', default='small-cap', dest='category')
    # parser.add_argument('-category', action='store', default='small-cap', dest='category')
    args = parser.parse_args().__dict__
    if args["category"] == 'small-cap':
        sc.get_list(False)
    elif args["category"] == 'mid-cap':
        from scrapper import mid_cap_list_scraper as mc
        mc.get_list(False)
