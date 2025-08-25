import pandas as pd
import imgkit

def main():
    df = pd.read_csv("results/validated.csv", delimiter=" ")
    scores = pd.read_csv("results/contentiousness_scores.csv", delimiter=" ")
    cont = pd.read_csv("results/contentiousness.csv", delimiter=" ")

    # Calculate errors
    df['error1'] = df['expected1'] - df['actual1']
    df['error2'] = df['expected2'] - df['actual2']
    
    df1 = df[['name1','error1']].copy()
    df1.columns = ['name','error']

    df2 = df[['name2','error2']].copy()
    df2.columns = ['name','error']

    df = pd.concat([df1, df2], ignore_index=True)
    # df['error'] = df['error'].abs()

    summary = df.groupby('name').agg(['mean','max','min'])

    # summary = summary.reset_index(level=[0,1])

    summary.columns = ['_'.join(map(str, col)) for col in summary.columns]

    merged = summary.join(scores.set_index('name'), how='left').join(cont.set_index('name'), how='left')

    merged['rand'] =  merged['rand'] / 6569769
    merged['stream'] =  merged['stream'] / 6583526
    merged['random/stream ratio'] = merged['rand'] - merged['stream']

    merged = merged.drop(['avg', 'rand', 'stream'], axis=1)
    merged['random/stream ratio'] = merged['random/stream ratio'].round(2)

    # print(merged)

    _max = merged[['error_max']].to_numpy().max()  
    _min = merged[['error_min']].to_numpy().min()  

    styled = (merged.style
        #   .format("{:.2f}%")
          .background_gradient(subset=['error_max'], cmap='Reds', vmin=0, vmax=_max)
          .background_gradient(subset=['error_min'], cmap='Blues_r', vmax=0, vmin=_min)
          .set_caption("Error values"))
    
    html = styled.to_html()
    with open("res.html", "w+") as f:
        f.write(html)

if __name__ == "__main__":
    main()