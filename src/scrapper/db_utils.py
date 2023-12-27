import json
from datetime import datetime

import psycopg2


def db_connection():
    dbname = 'mutualfunds'
    user = 'postgres'
    password = 'postgres'
    host = 'localhost'
    port = '5432'
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn


def write_to_funds_list(data: list, file_path: str):
    """
    {
        "Scheme-Name": "ITI Small Cap Fund - Direct Plan - Growth",\n
        "URL": "https://www.moneycontrol.com/mutual-funds/nav/iti-small-cap-fund-direct-plan-growth/MIT043",\n
        "Plan": "Direct Plan",\n
        "Category": "Small Cap Fund",\n
        "Crisil Rank": "1",\n
        "AuM (Cr)": "1,647.13"
    },

    id SERIAL PRIMARY KEY,
    scheme_name VARCHAR(255),
    url VARCHAR(255),
    plan VARCHAR(255),
    category VARCHAR(255),
    crisil_rank INTEGER,
    aum_cr NUMERIC
    """
    dt = datetime.now().replace(microsecond=0)
    conn = db_connection()
    cur = conn.cursor()
    try:
        if data is None and file_path is not None:
            with open(file_path, 'r') as file:
                data = json.load(file)
        elif data is None and file_path is None:
            print("Ha ha... That's nice try. Feed me some data. Not None(s)")
            return

        funds_list = data
        for fund in funds_list:
            print(fund)
            scheme_name = fund['Scheme-Name']
            crisil_rank = fund['Crisil Rank']
            try:
                crisil_rank = int(crisil_rank)
            except ValueError:
                crisil_rank = 0
            fund_url = fund['URL']
            fund_plan = fund['Plan']
            fund_category = fund['Category']
            fund_aum = str(fund['AuM (Cr)']).replace(",", "")
            insert_query = f"""INSERT INTO funds_list (scheme_name, url, plan, category, crisil_rank, aum_cr, 
                                created_on, modified_on) 
                                VALUES ('{scheme_name}', '{fund_url}', '{fund_plan}', 
                                    '{fund_category}', {crisil_rank}, {fund_aum}, '{dt}', '{dt}');
                            """

            cur.execute(insert_query)

        conn.commit()
    except Exception as ex:
        raise ex
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
    print(funds_list)


def save_fund_stocks(data: list):
    """
{
    "fund_name": "Aditya Birla Sun Life Midcap Fund - Direct Plan - Growth",
    "stock_url": "https://www.moneycontrol.com/india/stockpricequote/chemicals/gujaratfluorochemicalslimited/GUJAR54281",
    "Stock_Invested_in": "Gujarat Fluorochemicals Ltd.",
    "Sector": "Specialty chemicals",
    "Value_Mn": "1268.4",
    "pct_of_total_holdings": "2.98%",
    "1m_change": "-0.18%",
    "1Y_Highest_Holding": "4.45% (Nov 2022)",
    "1Y_Lowest_Holding": "2.97% (Jul 2023)",
    "Quantity": "4.57 L",
    "1M_Change_in_Qty": "0.00"
  },
    id                    serial,
    fund_name             varchar,
    stock_url             varchar,
    "Stock_Invested_in"   varchar,
    "Sector"              varchar,
    "Value_Mn"            numeric,
    pct_of_total_holdings double precision,
    "1m_change"           double precision,
    "1Y_Highest_Holding"  varchar,
    "1Y_Lowest_Holding"   varchar,
    "Quantity"            bigint,
    "1M_Change_in_Qty"    double precision
    """
    dt = datetime.now().replace(microsecond=0)
    conn = db_connection()
    cur = conn.cursor()
    try:
        if data is None:
            print("Ha ha... That's nice try. Feed me some data. Not None(s)")
            return

        fund_data = data
        for stock in fund_data:
            print(stock)
            fund_name = stock["fund_name"]
            stock_url = stock["stock_url"]
            stock_invested_in = stock["Stock_Invested_in"]
            sector = stock["Sector"]
            value_mn = stock["Value_Mn"]
            pct_of_total_holdings = float(stock["pct_of_total_holdings"].replace('%', ''))
            one_m_change = float(stock["1m_change"].replace('%', ''))
            one_y_highest_holding = stock["1Y_Highest_Holding"]
            one_y_lowest_holding = stock["1Y_Lowest_Holding"]
            quantity = stock["Quantity"]
            if str(stock["1M_Change_in_Qty"]).__contains__(" K".lower()):
                one_m_change_in_qty = float(stock["1M_Change_in_Qty"].replace(" K", "")) * 1000
            elif str(stock["1M_Change_in_Qty"]).__contains__(" M".lower()):
                one_m_change_in_qty = float(stock["1M_Change_in_Qty"].replace(" M", "")) * 1000000
            elif str(stock["1M_Change_in_Qty"]).__contains__(" L".lower()):
                one_m_change_in_qty = float(stock["1M_Change_in_Qty"].replace(" L", "")) * 1000000

            insert_query = f"""INSERT INTO stocks_by_fund (fund_name, stock_url, Stock_Invested_in, Sector, Value_Mn, 
                                pct_of_total_holdings, 1m_change, 1Y_Highest_Holding, Quantity, 1M_Change_in_Qty,
                                created_on, modified_on) 
                                VALUES ('{fund_name}', '{stock_url}', '{stock_invested_in}', '{sector}', {int(value_mn)}, 
                                '{pct_of_total_holdings}', {one_m_change}, '{one_y_highest_holding}', '{one_y_lowest_holding}',
                                {quantity}, {one_m_change_in_qty}, '{dt}', '{dt}');
                            """

            cur.execute(insert_query)

        conn.commit()
    except Exception as ex:
        raise ex
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()


# write_to_funds_list(file_path="output/funds/mid-cap-funds.json")
# write_to_funds_list(file_path="output/funds/small-cap-funds.json")
