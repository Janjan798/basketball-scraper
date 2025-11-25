import pandas as pd
from openai import OpenAI

client = OpenAI()

def get_all_player_pergame_avg():
  """
  Gets the averages of all players in the nba for this season and saves it as an excel file
  """
  df_list = pd.read_html("https://www.basketball-reference.com/leagues/NBA_2026_per_game.html")
  df = df_list[0]
  df=df.iloc[:-1].copy()
  df=df.drop(columns=["Awards"])
  df.to_excel("nba_2026_all_players_average_per_game.xlsx", index=False)

def get_player_id(name_list:list):
  """
  Takes a list of player names and returns a list of their player ids in the Basketball Reference website
  """
  response = client.responses.create(
    model="gpt-5",
    input=f"what is the PlayerID for the following players in Basketball Reference: {name_list}. Only give me a list of ids in python form."
  )
  list_ids=eval(response.output_text)
  return list_ids

def get_all_games_player_data(name_list:list,season=2026):
    """
    Gets the data for each game played by a player(list:input) in this season and saves it as an excel file
    """
    for name in name_list:
        list_player_ids = get_player_id(name)
        for player_id in list_player_ids:
          df_list=pd.read_html(f"https://www.basketball-reference.com/players/{player_id[0]}/{player_id}/gamelog/{season}")
          df=df_list[7]#7 because the first 6 are some nonsense tables
          df.to_excel(f"player_stats/{name}.xlsx", index=False)

def get_team_stats_data():
    """
    Gets the average per game data for each team and saves it
    """
    df = pd.read_html("https://www.basketball-reference.com/leagues/NBA_2026.html#advanced-team",header=[0,1], index_col=0)
    df=df[10]
    df.columns = df.columns.droplevel(0)
    df=df.drop(columns=["Unnamed: 17_level_1", "Unnamed: 22_level_1", "Unnamed: 27_level_1", "Arena", "Attend.", "Attend./G"])
    df=df.iloc[:-1].copy()

    cols = df.columns.tolist()
    cols[16] = "eFG%_OFF"
    cols[17] = "TOV%_OFF"
    cols[18] = "ORB%_OFF"
    cols[19] = "FT/FGA_OFF"
    cols[20] = "eFG%_DEF"
    cols[21] = "TOV%_DEF"
    cols[22] = "DRB%_DEF"
    cols[23] = "FT/FGA_DEF"
    df.columns = cols

    df.to_excel("team_stats.xlsx",index=False)

#get_all_games_player_data(["James Harden","Ivica Zubac","Stephen Curry"])
#get_all_games_player_data(["James Harden"],2025)
#get_all_player_pergame_avg()
#get_team_stats_data()
