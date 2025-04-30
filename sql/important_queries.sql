SELECT "Stock_Invested_in" as Stock, count(*) as Count
    FROM
        (SELECT DISTINCT ON (fund_name, "Stock_Invested_in") *
         FROM stocks_by_fund WHERE "1M_Change_in_Qty" > 0 ORDER BY "Stock_Invested_in") as sbf
    GROUP BY "Stock_Invested_in" ORDER BY Count DESC;

SELECT DISTINCT ON (fund_name, "Stock_Invested_in") * FROM stocks_by_fund WHERE "1M_Change_in_Qty" > 0 ORDER BY "Stock_Invested_in";

-- -- --
SELECT "Stock_Invested_in" as Stock, count(*) as Count
    FROM
        (SELECT DISTINCT ON (fund_name, "Stock_Invested_in") *
    FROM stocks_by_fund WHERE "1M_Change_in_Qty" > 0
                          AND created_on > '2025-04-01' AND created_on < '2025-04-28'
                          AND id > 3000
                        ORDER BY "Stock_Invested_in") as sbf
    GROUP BY "Stock_Invested_in" ORDER BY Count DESC;

SELECT DISTINCT ON (fund_name, "Stock_Invested_in") * FROM stocks_by_fund WHERE "1M_Change_in_Qty" > 0 ORDER BY "Stock_Invested_in";

SELECT DISTINCT ON (fund_name, "Stock_Invested_in") * FROM stocks_by_fund;

SELECT Max(id) FROM stocks_by_fund;