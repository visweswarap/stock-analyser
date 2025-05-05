-- SQLite-compatible schema for stock-analyser

-- funds_list table
CREATE TABLE IF NOT EXISTS funds_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_name TEXT,
    url TEXT,
    plan TEXT,
    category TEXT,
    crisil_rank INTEGER,
    aum_cr REAL,
    created_on DATE,
    modified_on DATE
);

-- stocks_by_fund table
CREATE TABLE IF NOT EXISTS stocks_by_fund (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_name TEXT,
    stock_url TEXT,
    Stock_Invested_in TEXT,
    Sector TEXT,
    Value_Mn REAL,
    pct_of_total_holdings REAL,
    one_m_change REAL,
    one_y_highest_holding TEXT,
    one_y_lowest_holding TEXT,
    Quantity INTEGER,
    one_m_change_in_qty REAL,
    created_on DATE,
    modified_on DATE,
    category TEXT
);

-- hni_portfolio table
CREATE TABLE IF NOT EXISTS hni_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_name TEXT,
    quantity_held REAL,
    holding_pct REAL,
    change_from_prev_qtr_value TEXT,
    holding_value REAL,
    name TEXT,
    net_worth REAL,
    portfolio_id INTEGER,
    slug TEXT,
    source TEXT,
    created_date DATE,
    modified_date DATE
);
