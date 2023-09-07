import pandas as pd
import glob


def run():
    json_files = glob.glob('../scrapper/output/small-cap/*.json')
    df = pd.concat([pd.read_json(f) for f in json_files], ignore_index=True)

    # Investment repeated for a stock and sort by stock name
    repeated_investments_df = df[df['Stock Invested in'].duplicated(keep=False)].sort_values(by=['Stock Invested in', 'pct_of_total_holdings'],
                                                                   ascending=[True, False])
    repeated_investments_df['1m_change1'] = repeated_investments_df['1m_change'].str.replace('%', '').astype(float)

    # Investment repeated and increased
    repeated_investments_inc_df = repeated_investments_df[repeated_investments_df["1m_change1"] > 0]

    # repeated_investments_inc_df.to_csv("report/small_cap_repeated_investments_inc_positive.csv", index=False)

    most_invested_stocks_df = repeated_investments_inc_df.groupby('Stock Invested in').size().reset_index(name='count')
    most_invested_stocks_filtered_df = most_invested_stocks_df[most_invested_stocks_df["count"] > 1]

    # most_invested_stocks_filtered_df.to_csv('report/small_cap_most_invested_stocks_filtered.csv', index=False)

    # Take "Stock Invested in", "stock_url" into separate df
    selected_columns_df = repeated_investments_inc_df[['Stock Invested in', 'stock_url']].drop_duplicates()

    # Perform a left join on the 'Stock Invested in' column; result ['Stock Invested in', 'count', 'stock_url']
    filtered_dff_with_stock_url = most_invested_stocks_filtered_df.merge(selected_columns_df, on='Stock Invested in', how='left')

    print("Finished")

run()
