-- create database mutualfunds;
grant ALL on database mutualfunds to postgres;

-- Create table
CREATE TABLE IF NOT EXISTS mutualfunds.public.funds_list (
    id SERIAL PRIMARY KEY,
    scheme_name VARCHAR(255),
    url VARCHAR(255),
    plan VARCHAR(255),
    category VARCHAR(255),
    crisil_rank INTEGER,
    aum_cr NUMERIC
);

alter table mutualfunds.public.funds_list add created_on DATE;

alter table mutualfunds.public.funds_list add modified_on DATE;


-- stocks_by_fund
CREATE TABLE IF NOT EXISTS mutualfunds.public.stocks_by_fund
(
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
);

ALTER TABLE mutualfunds.public.stocks_by_fund OWNER TO postgres;

alter table mutualfunds.public.stocks_by_fund add created_on DATE;

alter table mutualfunds.public.stocks_by_fund add modified_on DATE;

alter table mutualfunds.public.stocks_by_fund add category varchar;


-- HNI Portfolio
CREATE TABLE IF NOT EXISTS mutualfunds.public.hni_portfolio (
    id SERIAL PRIMARY KEY,
    stock_name VARCHAR(255),
    quantity_held DECIMAL(18, 2),
    holding_pct DECIMAL(5, 2),
    change_from_prev_qtr_value VARCHAR(255),
    holding_value DECIMAL(18, 2),
    name VARCHAR(255),
    net_worth DECIMAL(18, 2),
    portfolio_id VARCHAR(255),
    slug VARCHAR(255),
    source VARCHAR(255),
    created_date DATE,
    modified_date DATE
);

ALTER TABLE mutualfunds.public.stocks_by_fund OWNER TO postgres;