import pandas as pd
import re
def main():
    """The data that was scrapped came in pretty messy.  Many of the column names have duplicated text or otherwise
    incorrect names.  The player names field has similar problems.  The goal of this file is to clean this data.  Furthermore,
    the data that was collected does not contain columns for league and division.  I will use a file mlb_teams.csv to
    add the league and division information.  This file contains teams names whereas the scraped data contains
    codes for the team name.  I will convert the team names to codes using the match function in order to join the
    league and division data.  The team Statistics files for pitching and hitting had to be scraped separately, so
    this code will merge these two files together"""
    pitching=pd.read_csv('PitchingStatsAlltime2.csv').drop_duplicates() #read pitching csv generated by scrape_mlb.py
    hitting=pd.read_csv("HittingStatsAlltime.csv") #read hitting csv generated by scrape_mlb.py
    hitting=fixColumns(hitting) #fix mislabeled columns
    pitching=fixColumns(pitching) #fix mislabeled columns
    hitting["PLAYER"]=hitting['PLAYER'].apply(fixPlayerNames) #clean player name column
    pitching["PLAYER"] = pitching['PLAYER'].apply(fixPlayerNames) #clean player name column

    teams=pd.read_csv("teamStatistics1995-2023.csv") #Read in team statistics csv generated by scrape_mlb.py.  File does not contain
    #team wins

    teams=fixColumns(teams) #fix mislabeld columns
    teams['TEAM']=teams['TEAM'].apply(fixPlayerNames) #clean the team name column

    wins=pd.read_csv('WinsOnly.csv') #read in csv that contains team name (code) and amount of wins for a given year
    #also generated by scrape_mlb.py

    ids=wins.columns[3:]
    teams['CODE']=teams['TEAM'].apply(match,args=[ids]) #match the team names to the correct three letter code


    teams['WINS']=teams.apply(lookup, axis=1) #create Wins column by looking up team wins in the wins dataFrame.



    team_pitching=pd.read_csv("teamPitching1995-2023.csv") #csv generated by scrape_mlb.py
    team_pitching=fixColumns(team_pitching)

    team_pitching['TEAM']=team_pitching['TEAM'].apply(fixPlayerNames) #clean
    D={}
    for item in list(team_pitching.columns)[2:]: #add the word pitch to column names to distinguish between hitting stats when we
        #join the hitting dataframe.
        if item!='Year':
            D[item]=item+'_pitch'
    team_pitching['CODE'] = team_pitching['TEAM'].apply(match, args=[ids]) #add codes to pitching df
    team_pitching=team_pitching.rename(columns=D)

    team_pitching=team_pitching.drop(columns=['LEAGUE','TEAM'])#drop columns that will otherwise be duplicated
    teams=pd.merge(teams,team_pitching, on=['CODE','Year'],how='inner') #merge the team hitting and team pitching stats.



    division = pd.read_csv('mlb_teams.csv') #csv contains division and league information
    division=division[division['year']>1994] #filter out irrelavent years.

    division['CODE']=division['team_name'].apply(match, args=[ids]) #add the codes from the other files.

    division=division.rename(columns={'year':'Year'}) #make column names match
    division=division[['CODE','division_id','league_id','Year','team_name']]



    teams2=pd.merge(teams,division, on=['CODE','Year'], how='inner') #join teams with division adding division info to teams df.
    #This dataFrame will contain only rows where the year is 2020 or less because the division file only contains information
    #up to 2020.
    teams2=teams2.rename(columns={'division_id':'DIVISION'}) #rename column for consistency

    division_recent=division[division['Year']==2019] #dataFrame with only 2020 division information.  We'll assume that the divisions
    #remain the same after 2020.

    division_recent=division_recent[["CODE", "division_id","league_id",'team_name']]
    division_recent.to_csv('LeagueInfo.csv')
    division_recent=division_recent.rename(columns={'division_id':'DIVISION'})
    division_recent = division_recent.drop_duplicates(subset=['CODE', 'DIVISION', 'league_id'])

    teams_recent=teams[teams['Year']>2020]
    #print(division_recent.to_markdown())

    #print("here\n",  division_recent.to_markdown())
    #division_recent=division_recent[~((division_recent['CODE']=='MIL')&(division_recent['league_id']=='AL'))]




    teams_recent=pd.merge(teams_recent,division_recent, on=['CODE'],how='inner')

    final_teams=pd.concat([teams2,teams_recent], axis=0)

    final_teams=final_teams.drop(columns='league_id')

    pitching.to_csv('pitchingAllHistory_clean.csv')
    hitting.to_csv('hittingAllHistory_clean.csv')
    final_teams.to_csv('TeamWins_UpdatedVersion.csv') #includes years 1995 t0 2023 discluding 2020
    print('Hitting: Cleaned version of the career hitting stats.')
    print(hitting.info())
    print(hitting.sample(7).to_markdown())
    print('Pitching: Cleaned version of the career pitching stats.')
    print(pitching.info())
    print(pitching.sample(7).to_markdown())
    print("The final team_wins data: Data that will be used for the model.")
    print(final_teams.info())
    print(final_teams.sample(12).to_markdown())

def lookup(row):
    df=pd.read_csv("WinsOnly.csv")
    return df.loc[df['Year']==row['Year'],row['CODE']].values[0]
def fixColumns(df):
    D={}
    #df=df.rename(columns={"caret-upcaret-downGcaret-upcaret-downG":"GG"})
    df=df.drop(columns=[item for item in df.columns if "Unnamed" in item])
    for item in df.columns:
        if "caret-upcaret" in item:
            col= re.sub(r'[a-z\s]+', "", item)
            col=re.sub('-',"",col)
            df=df.rename(columns={item:col})
        else:
            col=item
        l=len(col)//2
        D[col]=col[:l]
    df=df.rename(columns=D)
    return df
def fixPlayerNames(x):
    pattern = r'[0-9]'
    new_string = re.sub(pattern, '', x)
    name=new_string.split(" ")

    name=list(map(lambda x: x[0]+x.split(x[0])[1],name))
    return " ".join(name)

def match(s1,codes):
    L=[]
    one=s1.split(' ')
    id=''
    for item in one:
        id+=item[0].upper()
        L.append(id)
    L.append(one[0][0:3].upper())
    if s1=='Arizona Diamondbacks':
        return 'ARI'
    elif s1 in ['Washington Nationals','Montreal Expos']:
        return 'WSN'
    elif s1=='St. Louis Cardinals':
        return 'STL'
    elif s1=='Chicago Cubs':
        return 'CHC'
    elif s1=='Toronto Blue Jays':
        return 'TOR'
    elif s1=='Florida Marlins':
        return 'MIA'
    elif 'Chicago White Sox' in s1:
        return 'CHW'
    elif "Angels" in s1:
        return "LAA"
    elif "Tampa Bay" in s1:
        return "TBR"
    for code in codes:
        for item in L:
            if item==code:
                return code

    return (s1,'No Match')

if __name__=='__main__':
    main()