def __dev__():
    import json
    from pathlib import Path

    import pandas as pd

    from src.hanjadict.main import pronunciation
    from src.hanjadict.table import table_data

    df = pd.DataFrame(table_data.items(), columns=["hj", "ko"])

    df1 = df[df["ko"].str.contains(",")].reset_index(drop=True)
    df2 = df[df["ko"].str.contains(r"\(")].reset_index(drop=True)
    df3 = df[df["ko"].str.contains(r"\/")].reset_index(drop=True)

    idx = df["hj"].isin(df1["hj"]) | df["hj"].isin(df2["hj"]) | df["hj"].isin(df3["hj"])
    df_etc = df[~idx].reset_index(drop=True)
    df_hmm = df[idx].reset_index(drop=True)

    df_sample = pd.concat([df_etc.sample(10), df_hmm.sample(40)]).reset_index(drop=True)
    df_sample.sort_values("hj", inplace=True)
    d1 = df_sample.set_index("hj")["ko"].to_dict()
    Path("temp.json").write_text(
        json.dumps(d1, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # pron test
    df["pron"] = df["hj"].apply(pronunciation)
    df["pron"].isna().sum()
