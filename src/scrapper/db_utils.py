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


# write_to_funds_list(file_path="output/funds/mid-cap-funds.json")
# write_to_funds_list(file_path="output/funds/small-cap-funds.json")
