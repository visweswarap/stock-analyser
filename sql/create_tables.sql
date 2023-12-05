create database mutualfunds;
grant ALL on database mutualfunds to postgres;

-- Create table
CREATE TABLE funds_list (
    id SERIAL PRIMARY KEY,
    scheme_name VARCHAR(255),
    url VARCHAR(255),
    plan VARCHAR(255),
    category VARCHAR(255),
    crisil_rank INTEGER,
    aum_cr NUMERIC
);


