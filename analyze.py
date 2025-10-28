import pandas as pd
import re
from collections import defaultdict

import constants

def sort_df(df: pd.DataFrame) -> pd.DataFrame:
    order = df.index.tolist()            # desired order (from the rows)
    df_aligned = df.reindex(columns=order)   # reorder columns to match index
    # if you also want to ensure rows follow same ordering (no-op if already sorted):
    return df_aligned.reindex(index=order)

def strip_name(n: str) -> str:
    if n.find("_") == -1:
        return n
    return n.split(sep='.')[1].split(sep='_')[0]

def main():
    df = pd.read_csv(f"{constants.RESULTS_DIR}/validated.csv", delimiter=" ")
    # scores = pd.read_csv(f"{constants.RESULTS_DIR}/contentiousness_scores.csv", delimiter=" ")
    # cont = pd.read_csv(f"{constants.RESULTS_DIR}/contentiousness.csv", delimiter=" ")

    # 10 9 = 1
    # 16 20 = -4

    # Calculate errors
    df['error1'] = df['expected1'] - df['actual1']
    df['error2'] = df['expected2'] - df['actual2']
    
    # df1 = df[['name1','error1']].copy()
    # df1.columns = ['name','error']

    # df2 = df[['name2','error2']].copy()
    # df2.columns = ['name','error']

    # df = pd.concat([df1, df2], ignore_index=True)

    data = defaultdict(lambda: defaultdict(dict))

    for _, row in df.iterrows():
        n1, n2 = row['name1'], row['name2']
        n1, n2 = strip_name(n1), strip_name(n2)
        if n1 == n2:
            data[n1][n2] = None
        data[n1][n2] = row['error1']
        data[n2][n1] = row['error2']

    df = pd.DataFrame.from_dict(data)
    df = sort_df(df)


    # summary = df.groupby('name').agg(['mean','max','min'])

    # summary = summary.reset_index(level=[0,1])

    # summary.columns = ['_'.join(map(str, col)) for col in summary.columns]

    # summary['error_mean'] *= 100
    # summary['error_max'] *= 100
    # summary['error_min'] *= 100

    # merged = summary.join(scores.set_index('name'), how='left')

    # print(merged)

    # _max = summary[['error_max']].to_numpy().max()  
    # _min = summary[['error_max']].to_numpy().min()  
    # _max2 = summary[['error_min']].to_numpy().max() 
    # _min2 =  summary[['error_min']].to_numpy().min()  

    # styled = (summary.style
    #       .format("{:.2f}%")
    #       .background_gradient(subset=['error_max'], cmap='Reds', vmin=_min, vmax=_max)
    #       .background_gradient(subset=['error_min'], cmap='Blues_r', vmax=_max2, vmin=_min2)
    #       .set_caption("Error values"))
    df.to_csv(f"{constants.RESULTS_DIR}/validation_matrix.csv")

    # _min = df.min().min()
    # _max = df.max().max()

    # styled = (df.style
    #         .format(lambda x: "" if pd.isna(x) else f"{x:.2f}%")
    #         .background_gradient(cmap='bwr', vmin=_min, vmax=_max)
    #         .map(lambda v: "background-color: lightgray" if pd.isna(v) else "")
    #         .set_table_attributes('style="table-layout: fixed; width:100%;"')
    #         # set equal column width and hide overflow with ellipsis
    #         .set_table_styles([
    #             {
    #                 "selector": "th, td",
    #                 "props": [
    #                     ("width", "100px"),            # choose desired width
    #                     ("max-width", "100px"),
    #                     ("overflow", "hidden"),
    #                     ("text-overflow", "ellipsis"),
    #                     ("white-space", "nowrap"),
    #                     ("padding", "4px 6px")         # optional: tighten spacing
    #                 ],
    #             }
    #         ])
    # )
    
    # html = styled.to_html()
    # with open("res.html", "w+") as f:
    #     f.write(html)

if __name__ == "__main__":
    main()