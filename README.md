# Stock Analyser

This project scrapes, analyzes, and reports on Indian mutual fund holdings, focusing on mid-cap, small-cap, and large-cap funds. It is designed for research and data analysis of fund portfolios and their underlying stocks.

## Features
- Scrapes mutual fund data from Moneycontrol and similar sources
- Extracts fund lists and their top stock holdings
- Saves data to a local SQLite or Postgres database
- Provides scripts for mid-cap, small-cap, and large-cap fund analysis
- Outputs CSV and JSON reports for further analysis

## Setup Instructions

### Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

### Installation
1. Clone this repository
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up the database:
   - For SQLite: No setup needed (default: `mutualfunds.db`)
   - For Postgres: Edit connection details in `src/scrapper/db_utils.py`
   - Run the SQL in `sql/create_tables_sqlite.sql` or `sql/create_tables.sql` to create tables

### Running Scrapers
- Run a scraper script, e.g.:
  ```sh
  python src/scrapper/mid_cap_list_scraper.py
  python src/scrapper/small_cap_list_scraper.py
  python src/scrapper/large_cap_list_scraper.py
  ```
- Output and logs will be saved in the `output/` directory

### Database Tables
- `funds_list`: List of mutual funds and their metadata
- `stocks_by_fund`: Stocks held by each fund, with holding details

### Customization
- Edit `src/scrapper/config.py` to change scraping URLs
- Add or modify analysis scripts in `src/analyze/`

## Contribution Guidelines
- Please write tests for new features
- Follow PEP8 and standard Python best practices
- Open issues or pull requests for bugs and improvements

## Contact
- Repo owner: Vish Pepala, vish.pepala@spglobal.com
- For questions, open an issue or contact the maintainer