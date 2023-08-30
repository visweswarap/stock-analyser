import pandas as pd
import glob


def get_data():
    json_files = glob.glob('../scrapper/output/small-cap/*.json')
    df = pd.concat([pd.read_json(f) for f in json_files])

    print(df.count())
    print("Finished")

get_data()
