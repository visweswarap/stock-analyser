SELECT "Stock_Invested_in" as Stock, count(*) as Count
    FROM
        (SELECT DISTINCT ON (fund_name, "Stock_Invested_in") *
         FROM stocks_by_fund WHERE "1M_Change_in_Qty" > 0 ORDER BY "Stock_Invested_in") as sbf
    GROUP BY "Stock_Invested_in" ORDER BY Count DESC;

SELECT DISTINCT ON (fund_name, "Stock_Invested_in") * FROM stocks_by_fund WHERE "1M_Change_in_Qty" > 0 ORDER BY "Stock_Invested_in"