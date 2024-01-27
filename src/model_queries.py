all_small_and_mid_cap = """SELECT "Stock_Invested_in", count(fund_name) as count from stocks_by_fund
    WHERE created_on = (SELECT MAX(created_on) FROM stocks_by_fund)
        AND "1m_change" >= 0
    group by stock_url, "Stock_Invested_in"
    Order by count DESC;"""

all_positive = """SELECT "Stock_Invested_in", count(fund_name) as count from stocks_by_fund
    WHERE created_on = (SELECT MAX(created_on) FROM stocks_by_fund)
        AND "1m_change" >= 0
    group by stock_url, "Stock_Invested_in"
    Order by count DESC;"""
