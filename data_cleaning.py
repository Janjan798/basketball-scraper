import pandas as pd


def mp_to_float(mp):
    """
    MP column minutes played is like 35:30
    this function is to take that string as input and convert it into float 35.5
    """
    if isinstance(mp, str) and ":" in mp:
        m, s = mp.split(":")
        return int(m) + int(s) / 60
    return pd.to_numeric(mp, errors="coerce")

def clean_player_table(player_name):
    """
    to clean the table with player data and save it
    """
    df = pd.read_excel(f"player_stats/{player_name}.xlsx")
  
    df = df[df["Rk"] != "Rk"].copy() # to drop duplicate header row 

    df["HomeAway"] = df["Unnamed: 5"].apply(lambda x: "Away" if x == "@" else "Home")
    df = df.drop(columns=["Unnamed: 5"]) # to classify game as home or away and drop '@' column

    df = df.iloc[:-1].copy() # to drop last row (season total)

    numeric_cols = [
        "FG","FGA","FG%","3P","3PA","3P%","2P","2PA","2P%",
        "eFG%","FT","FTA","FT%","ORB","DRB","TRB",
        "AST","STL","BLK","TOV","PF","PTS","GmSc","+/-"
    ]

    for col in numeric_cols:
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce") # converting column data to numeric from object
        except:
            print(f"Player:{player_name} Error: Column {col} not available")
    df["MP"] = df["MP"].apply(mp_to_float)

    # date to datetime
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df.to_excel(f"player_stats/{player_name}.xlsx", index=False)

"""
clean_player_table("Ivica Zubac")
clean_player_table("Stephen Curry")
clean_player_table("James Harden")
"""


