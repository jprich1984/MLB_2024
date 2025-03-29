import pandas as pd
import numpy as np
import requests
from io import StringIO


def main():
    """Contains functions that scrape table data from various baseball websites.  The goal is to create two files, one
    That will be used for training/testing data and another that will be used as new data to make predictions.  The first three
    function calls are for creating the training data.  Later, I will merge these three files together to make a file
    that contains teams, years, team wins, and various statistics.  This file will be used to create a model that will predict team
    wins.  The last two function calls are for creating the new data for
    which I will apply the model to.  These files will be merged with a file that contains the names of players currently
    on the roster of mlb teams.  From this I will create a file that contains teams and statistics but with no wins."""
    create_team_pitching() #creates a file that contains team pitching stats for each year 1995-2023.
    create_team_hitting() #creates a file that contains team statistics for each  1995-2023
    create_team_wins() #Creates a file that contains team wins for each year
    create_player_pitching() #creates a file that  contains the career statistics for each pitcher who ever played.
    create_player_hitting() #creates a file that contains the career statistics for each hitter that ever played.


def create_player_pitching():
    url_pitch = "https://www.mlb.com/stats/pitching/games/all-time-totals"
    pitching=scrapeMLB_players(url_pitch,421)
    pitching.to_csv('PitchingStatsAlltime2.csv')

def create_player_hitting():
    url_hit="https://www.mlb.com/stats/games/all-time-totals"
    hitting=scrapeMLB_players(url_hit,781)
    hitting.to_csv("HittingStatsAlltime.csv")

def create_team_hitting():
    url_team="https://www.mlb.com/stats/team/"
    years=[i for i in range(1995,2020)]+[2021,2022,2023]
    teams=scrapeMLB_teams(url_team,years)
    teams.to_csv("teamStatistics1995-2023.csv")
def create_team_wins():
    url_wins="https://www.baseball-reference.com/leagues/majors/index.shtml"
    wins=scrapeBaseballReference(url_wins)
    years=[str(i) for i in range(1995,2020)]+["2021","2022","2023"]
    wins=wins[wins['Year'].isin(years)]
    wins=wins.dropna(axis=1,how='all')
    wins.to_csv("WinsOnly.csv")

def create_team_pitching():
    years = [str(i) for i in range(1995, 2020)] + ["2021", "2022", "2023"]
    team_pitching_url="https://www.mlb.com/stats/team/pitching/"
    team_pitching=scrapeMLB_teams(team_pitching_url,years)
    team_pitching.to_csv("teamPitching1995-2023.csv")
def scrapeMLB_teams(url,years):
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
    tabs=[]  #list will hold the list of dataframes
    for year in years:
        url2=url+f"{year}"
        r=requests.get(url2,headers=header)
        add_on=pd.read_html(StringIO(r.text))[0]
        add_on['YearYear']=year
        tabs.append(add_on)
        print(add_on)
    df=tabs[0]
    for item in tabs[1:]:
        df=pd.concat([df,item],axis=0)
    return df
def scrapeMLB_players(url,numPages):
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
    r = requests.get(url, headers=header)
    first=pd.read_html(StringIO(r.text)) #returns a list that contains 1 element which is a dataframe.
    tabs=[first]  #list will hold the list of dataframes
    for i in range(2,numPages+1):
        url2=url+f"?page={i}"
        r=requests.get(url2,headers=header)
        add_on=pd.read_html(StringIO(r.text))
        tabs.append(add_on)
        print(add_on)
    table=tabs[0][0]

    for item in tabs[1:]:
        table=pd.concat([table,item[0]], axis=0)
        print(item)
    return table

def scrapeBaseballReference(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
    r = requests.get(url, headers=header)
    first=pd.read_html(StringIO(r.text)) #returns a list that contains 1 element which is a dataframe.
    return first[0]

if __name__=='__main__':
    main()