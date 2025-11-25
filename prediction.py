import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

TEAM_ABBREV_TO_NAME = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BRK": "Brooklyn Nets",
    "CHI": "Chicago Bulls",
    "CHO": "Charlotte Hornets",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards",
}


def load_team_stats(path):
    """to load team advanced stats with ORtg, DRtg, eFG%_DEF, etc.  """
    team_df = pd.read_excel(path)
    team_df = team_df.set_index("Team")
    return team_df

def add_features(player_df, team_df):
    """
    to add opponent and player rolling features for model training.
    """

    df = player_df.copy()

    df["Opp_TeamName"] = df["Opp"].map(TEAM_ABBREV_TO_NAME)

    opp_stats = team_df[["ORtg","DRtg","NRtg","Pace","eFG%_DEF"]]

    df = df.merge(opp_stats, left_on="Opp_TeamName", right_index=True, how="left")

    df["PTS_last3"] = df["PTS"].rolling(3).mean().shift(1)
    df["PTS_last5"] = df["PTS"].rolling(5).mean().shift(1)
    df["FGA_last3"] = df["FGA"].rolling(3).mean().shift(1)
    df["MP_last5"] = df["MP"].rolling(5).mean().shift(1)
    df["PTS_season"] = df["PTS"].expanding().mean().shift(1)
    df["Usage"] = (df["FGA"] + 0.44 * df["FTA"]) / df["MP"]

    # final clean model data
    df = df.dropna().copy()

    return df

def make_next_game_features(player_df, team_df, next_opp_abbrev, is_home: int):
    """
    Build a 1-row feature DataFrame for the upcoming game.
    is_home: 1 if home, 0 if away.
    """
    df = player_df.copy()
    # Make sure sorted by date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date").reset_index(drop=True)

    # Ensure numeric
    num_cols = ["MP","FGA","3P","FTA","PTS"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Recompute rolling features on full history
    df["PTS_last3"] = df["PTS"].rolling(3).mean().shift(1)
    df["PTS_last5"] = df["PTS"].rolling(5).mean().shift(1)
    df["FGA_last3"] = df["FGA"].rolling(3).mean().shift(1)
    df["MP_last5"]  = df["MP"].rolling(5).mean().shift(1)
    df["PTS_season"] = df["PTS"].expanding().mean().shift(1)
    df["Usage"] = (df["FGA"] + 0.44 * df["FTA"]) / df["MP"]

    # Take the *last played game* row as the base for form
    last = df.dropna().iloc[-1]

    # Opponent ratings for NEXT game
    opp_team_name = TEAM_ABBREV_TO_NAME[next_opp_abbrev]
    opp_row = team_df.loc[opp_team_name]

    # Build the feature dict in the SAME shape as FEATURES
    row = {
        "Home": is_home,
        "MP": last["MP"],
        "FGA": last["FGA"],
        "3P": last["3P"],
        "FTA": last["FTA"],
        "Usage": last["Usage"],
        "PTS_last3": last["PTS_last3"],
        "PTS_last5": last["PTS_last5"],
        "FGA_last3": last["FGA_last3"],
        "MP_last5": last["MP_last5"],
        "PTS_season": last["PTS_season"],
        "DRtg": opp_row["DRtg"],
        "ORtg": opp_row["ORtg"],
        "NRtg": opp_row["NRtg"],
        "Pace": opp_row["Pace"],
        "eFG%_DEF": opp_row["eFG%_DEF"],
    }

    return pd.DataFrame([row])


team_df = load_team_stats("team_stats.xlsx")

player_df=pd.read_excel("player_stats/James Harden.xlsx")
player_df = player_df[player_df["PTS"].notna()].copy()
df_model = add_features(player_df, team_df)
df_model.head()

FEATURES = [
    "Home","MP","FGA","3P","FTA","Usage",
    "PTS_last3","PTS_last5","FGA_last3","MP_last5","PTS_season",
    "DRtg","ORtg","NRtg","Pace","eFG%_DEF",
]

X = df_model[FEATURES]
y = df_model["PTS"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=7,
    random_state=42,
    min_samples_leaf=2,
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
print(f"Test MAE: {mae:.2f} points")


next_features = make_next_game_features(
    player_df=player_df,
    team_df=team_df,
    next_opp_abbrev="DEN",  
    is_home=0               # 1 = home, 0 = away
)

next_features = next_features[FEATURES]

pred_next = model.predict(next_features)[0]
print(f"Predicted NEXT GAME POINTS: {pred_next:.2f}")
