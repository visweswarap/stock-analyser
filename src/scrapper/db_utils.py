import json
import logging
from datetime import datetime
import sqlite3
import psycopg2


def get_db_connection(db_type='sqlite'):
    if db_type == 'postgres':
        dbname = 'mutualfunds'
        user = 'postgres'
        password = 'postgres'
        host = 'localhost'
        port = '5432'
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        return conn
    else:
        # Default to SQLite
        conn = sqlite3.connect('mutualfunds.db')
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
    dt: datetime = datetime.now().replace(microsecond=0)
    conn = get_db_connection()
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
        logging.error(f"saving to DB failed: {ex}")
        raise ex
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
    print(funds_list)


def save_fund_stocks(data: list, db_type='sqlite', category=None):
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
    conn = get_db_connection()
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
            value_mn = float(stock["Value_Mn"])
            pct_of_total_holdings = float(stock["pct_of_total_holdings"].replace('%', ''))
            one_m_change = float(stock["1m_change"].replace('%', ''))
            one_y_highest_holding = stock["1Y_Highest_Holding"]
            one_y_lowest_holding = stock["1Y_Lowest_Holding"]
            quantity = stock["Quantity"].upper()
            quantity = normalise_amount(quantity)
            m_change_in_qty = stock["1M_Change_in_Qty"].upper()
            one_m_change_in_qty = normalise_amount(m_change_in_qty)

            if db_type == 'sqlite':
                insert_query = f"""
                INSERT INTO stocks_by_fund (
                    fund_name, stock_url, Stock_Invested_in, Sector, Value_Mn, pct_of_total_holdings,
                    one_m_change, one_y_highest_holding, one_y_lowest_holding, Quantity, one_m_change_in_qty,
                    created_on, modified_on, category)
                VALUES ('{fund_name}', '{stock_url}', '{stock_invested_in}', '{sector}', 
                                {int(value_mn)}, '{pct_of_total_holdings}', {one_m_change}, '{one_y_highest_holding}', 
                                '{one_y_lowest_holding}', {quantity}, {one_m_change_in_qty}, '{dt}', '{dt}', '{category}');
                """
            elif db_type == 'postgres':
                insert_query = f"""INSERT INTO stocks_by_fund (fund_name, stock_url, "Stock_Invested_in", 
                                "Sector", "Value_Mn", pct_of_total_holdings, "1m_change", "1Y_Highest_Holding", 
                                "1Y_Lowest_Holding", "Quantity", "1M_Change_in_Qty", created_on, modified_on, category) 
                              VALUES ('{fund_name}', '{stock_url}', '{stock_invested_in}', '{sector}', 
                                {int(value_mn)}, '{pct_of_total_holdings}', {one_m_change}, '{one_y_highest_holding}', 
                                '{one_y_lowest_holding}', {quantity}, {one_m_change_in_qty}, '{dt}', '{dt}', '{category}');
                            """
            cur.execute(insert_query)

        conn.commit()
    except Exception as ex:
        logging.error(f"saving to DB failed: {ex}")
        raise ex
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()


def save_hni_portfolio(portfolio: list):
    if portfolio is None or portfolio == []:
        logging.error("Want me to save none hni data ? Lets be practical!")
        return
    # dt = datetime.now().replace(microsecond=0)
    conn = get_db_connection()
    cur = conn.cursor()

    table_name = "hni_portfolio"
    try:
        for data in portfolio:
            # Convert Python types to PostgreSQL types
            logging.info(data)
            if data["quantity_held"] == '':
                data["quantity_held"] = '0'
            if data["holding_pct"] == '':
                data["holding_pct"] = '0'
            if data["holding_value"] == '':
                data["holding_value"] = '0'
            if data["net_worth"] == '':
                data["net_worth"] = '0'

            data["quantity_held"] = float(data["quantity_held"].replace(",", ""))
            data["holding_pct"] = float(data["holding_pct"].replace('%', '').strip())
            data["holding_value"] = float(data["holding_value"].replace(",", ""))
            data["net_worth"] = float(data["net_worth"].replace(",", ""))
            data["portfolio_id"] = int(data["portfolio_id"])

            # Generate SQL insert statement
            insert_statement = f"INSERT INTO {table_name} ({', '.join(data.keys())}, created_date, modified_date) VALUES ("
            for key, value in data.items():
                if isinstance(value, str):
                    insert_statement += f"'{value}', "
                else:
                    insert_statement += f"{value}, "

            # Add current date for created_date and modified_date
            insert_statement += "CURRENT_DATE, CURRENT_DATE);"
            print(insert_statement)
            cur.execute(insert_statement)
        conn.commit()
    except Exception as ex:
        logging.error("Failed to save HNI data to DB")
        logging.error(ex)
        raise ex
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()


def delete_current_month_data_before(category: str):
    if category is None or category == "":
        logging.error("You are deleting data without category? Be cautious!")
    # dt = datetime.now().replace(microsecond=0)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Generate SQL insert statement
        insert_statement = (f"DELETE FROM stocks_by_fund "
                            f"WHERE EXTRACT(MONTH FROM created_on) = EXTRACT(MONTH FROM CURRENT_DATE) "
                            f"AND EXTRACT(YEAR FROM created_on) = EXTRACT(YEAR FROM CURRENT_DATE)"
                            f"AND ;")
        print(insert_statement)
        cur.execute(insert_statement)
        conn.commit()
    except Exception as ex:
        logging.error("Failed to delete current month data from DB")
        logging.error(ex)
        raise ex
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()


def normalise_amount(value: str):
    if value.__contains__(" L"):
        value = float(value.replace(" L", "")) * 100000
    elif value.__contains__(" K"):
        value = float(value.replace(" K", "")) * 1000
    elif value.__contains__(" M"):
        value = float(value.replace(" M", "")) * 1000000
    elif value.__contains__(" CR"):
        value = float(value.replace(" CR", "")) * 10000000
    else:
        value = float(value)
    return value

# write_to_funds_list(file_path="output/funds/mid-cap-funds.json")
# write_to_funds_list(file_path="output/funds/small-cap-funds.json")
