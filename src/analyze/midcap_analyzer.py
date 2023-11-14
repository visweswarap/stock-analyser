from pathlib import Path

import pandas as pd
import glob
from datetime import datetime


def run():
    today = datetime.today().strftime("%Y-%m-%d")
    output_dir = Path(f"archive/{today}")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = glob.glob('../scrapper/output/mid-cap/*.json')
    df = pd.concat([pd.read_json(f) for f in json_files], ignore_index=True)

    df.rename(columns={'Stock Invested in': 'Stock_Invested_in'})
    # Investment repeated for a stock and sort by stock name
    repeated_investments_df = df[df['Stock_Invested_in'].duplicated(keep=False)].sort_values(
        by=['Stock_Invested_in', 'pct_of_total_holdings'],
        ascending=[True, False])
    repeated_investments_df['1m_change1'] = repeated_investments_df['1m_change'].str.replace('%', '').astype(float)

    # Investment repeated and increased
    repeated_investments_inc_df = repeated_investments_df[repeated_investments_df["1m_change1"] > 0]

    repeated_investments_inc_df.to_csv("report/mid_cap_repeated_investments_inc_positive.csv", index=False)
    repeated_investments_inc_df.to_csv(f"archive/{today}/mid_cap_repeated_investments_inc_positive.csv", index=False)

    most_invested_stocks_df = repeated_investments_inc_df.groupby('Stock_Invested_in').size().reset_index(name='count')
    most_invested_stocks_filtered_df = most_invested_stocks_df[most_invested_stocks_df["count"] > 1]

    most_invested_stocks_filtered_df = most_invested_stocks_filtered_df.sort_values("count", ascending=False)
    most_invested_stocks_filtered_df.to_csv('report/mid_cap_most_invested_stocks_filtered.csv', index=False)
    most_invested_stocks_filtered_df.to_csv(f"archive/{today}/mid_cap_most_invested_stocks_filtered.csv", index=False)

    print("Finished")


run()
