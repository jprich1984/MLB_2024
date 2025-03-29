import pandas as pd
from pandas.api.types import is_numeric_dtype, is_integer_dtype
from sklearn.linear_model import LinearRegression
from clean_baseball_data import match
def main():
    """The goal of this file is to transform the cleaned data for 2024, getting it into the same format
    as the data in TeamWins_UpdatatedVersion.csv.  I will need to join the rosters data with the statistics data
    for 2024 then aggregate it so that their are statistics that are representative of the team as a whole."""

    pitching=pd.read_csv('pitchingAllHistory_clean.csv') #Data contains career stats of every pitcher in mlb history
    hitting=pd.read_csv('hittingAllHistory_clean.csv') #Data contains career stats of every hitter in mlb history.
    rosters=pd.read_csv("PlayerTeamsAll.csv") #File contains this years (2024) rosters with career stats for each team.

    L=["60-Day IL","Optioned","Reassigned",'Projected Restricted List (visa)','Released','Projected Injured List','Projected Restricted List',
       'Projected Restricted List (SUSP)','Projected Injured List (MiLB)'] #List of player types to disclude.

    rosters=rosters[~rosters['Status'].isin(L)] #Take out players who likely will not be playing
    rosters['Pitcher']=rosters['Pos'].apply(is_Pitcher) #Make a column which indicates if a player is a pitcher or not.
    rosters=rosters.rename(columns={'Name':'PLAYER'}) #Rename name column to player for joining purposes.
    print(rosters.info())
    roster_hitting=rosters[~rosters['Pitcher']] #Get dataFrame containing only hitters

    joined_hitting=pd.merge(roster_hitting,hitting,on='PLAYER',how='inner') #Merge the roster data with the hitters career stats data.

    roster_pitching=rosters[rosters['Pitcher']] #Get dataFrame containing only pitchers

    joined_pitching=pd.merge(roster_pitching,pitching, on='PLAYER',how='inner') #Join rosters data with pitchers career stats data.

    """When the team statistics are calculated, they will be sensitive to extreme values caused by rookies that for
    example have pitched only a few inning and let go of an exhorbinant amount of runs in those innings.  For example,
    I re ran the scrape after the dodgers played their opening games in seoul and the dodgers team ERA was above 8, because
    rookie Yomimoto let go of 5 runs in 1 inning making his career era 45.  Therefore, I am removing pitchers who have not pitched at least 
    10 innings."""
    joined_pitching = joined_pitching[joined_pitching['IP']>=10]

    """Now we need to create a weighted average for each statistics that best represents the team as a whole. For pitching
    I will weight based on two categories: starting rotation and bullpen.  To do this I will find out the average depth of the teams starting pitching
    convert this into a percent that represents the percentage of the game the teams pitchers will generally pitch.  This value will 
    become the weight that will be applied to the teams statistics, the rest of the weight will be given to the bullpen."""

    joined_pitching['Status']=joined_pitching['Status'].apply(lambda x: x if x=='Starting Rotation' else 'Bullpen')
    #Change the status column so that players are categorized as either starting rotation or bullpen.
    joined_pitching['WHIP']=joined_pitching['WHIP'].astype(float)
    joined_pitching['ERA'] = joined_pitching['ERA'].astype(float)
    joined_pitching['AVG'] = joined_pitching['AVG'].astype(float)
    """the methods in weightPitching use datatype to determine which aggregate function to apply to a column,
    float columns should be averaged while integer columns should be summed."""
    team_pitching=weightPitching(joined_pitching).get() #This returns the aggregated weighted average of all pitchers on each team.
    """Similar to pitching, I needed a weighted average for the teams hitting statistics.  How to weight each player category
    was not as easy to determine for hitting.  I decided to categorize a player as either lineup regular or bench and 
    assigned the lineup regular category to 75% of the weight remaining 25% to the bench.  This is probably generally pretty 
    accurate, however different teams are managed differently, and some teams give certain bench players a lot of 
    at-bats in certain situations.  For example, certain bench players will get more at-bats that a lineup regular if the
    pitcher is left-handed.  I encourage you to come up with different categories and weights to make this more accurate."""

    joined_hitting['Status']=joined_hitting['Status'].apply(lambda x: x if x=='Lineup Regular' else "Bench")
    weights = {'Lineup Regular': 0.75, 'Bench': 0.25}
    joined_hitting=joined_hitting[joined_hitting['AB']>=20] #remove batters that have less than 20 at-bats
    #joined hitting
    joined_hitting['AVG'] = joined_hitting['AVG'].astype(float)
    joined_hitting['OPS']=joined_hitting['OPS'].astype(float)
    joined_hitting['SLG'] = joined_hitting['SLG'].astype(float)
    joined_hitting['OBP'] = joined_hitting['OBP'].astype(float)
    joined_hitting['RBI'] = joined_hitting['RBI'].astype(int)
    joined_hitting['SB'] = joined_hitting['SB'].astype(int)
    joined_hitting['CS'] = joined_hitting['CS'].astype(int)
    joined_hitting['SO'] = joined_hitting['SO'].astype(int)

    team_hitting=weightedHitting(joined_hitting, weights).get() #Returns dataFrame with the aggregated team averages for each statistic.

    team_stats_24=pd.merge(team_pitching,team_hitting, how='inner',on='Team')
    team_stats_24['Year']=2024
    team_stats_24=team_stats_24.rename(columns={'Team':'CODE'})
    leagues=pd.read_csv('leagueInfo.csv') #contains the current teams with their leagues and divisions
    leagues=leagues[['CODE','division_id','league_id']]
    print(leagues.sort_values(by='CODE')['CODE'].unique())
    print(len(leagues))
    print(team_stats_24.sort_values(by='CODE')["CODE"].unique())
    print(len(team_stats_24))
    team_stats_24=pd.merge(leagues,team_stats_24, on=['CODE'])#add the league/division information to the dataFrame
    team_stats_24=team_stats_24.rename(columns={'division_id':'DIVISION','league_id':'LEAGUE'}) #rename so it matches the format of training data.
    team_stats_24.to_csv('2024teamStatsProjections.csv')





class CalcTeamStatistics:
    def __init__(self,df):
        self.df=df.drop(columns=[item for item in df.columns if item.startswith('Unnamed')]).rename(columns={'PLAYER':'Player'})
        self.features=[item for item in self.df.columns if is_numeric_dtype(self.df[item])]
        self.grouped=self.group()
    def feature_dict(self):
        D={}
        for item in self.features:
           if is_integer_dtype(self.df[item]):
                D[item]='sum'
           else:
               D[item]='mean'
           if item=='IP':
               D[item]='sum'
        return D

    def group(self):
        grouped=self.df.groupby(['Team','Status']).agg(self.feature_dict())
        return grouped.reset_index()
class weightPitching(CalcTeamStatistics):
    def __init__(self,df):
        super().__init__(df)
        self.regrouped=self.starter_depth()
        self.weighted=self.weightedAverage()
        self.totals()
    def starter_depth(self):
        starters=self.grouped[self.grouped['Status']=='Starting Rotation'].copy()
        starters['starter contribution']=(starters['IP']/starters['G'])/9
        updated_grouped=pd.merge(self.grouped,starters[['starter contribution','Team']], on='Team', how='inner')
        updated_grouped['Weight']=updated_grouped.apply(lambda x: x['starter contribution'] if x['Status']=='Starting Rotation' else 1-x['starter contribution'], axis=1)
        return updated_grouped.drop(columns=['starter contribution'])
    def weightedAverage(self):
        D={}
        print(self.features)
        for item in self.features:
            if not is_integer_dtype(self.regrouped[item]) and item!='IP':
                self.regrouped[item]=self.regrouped[item]*self.regrouped['Weight']
                D[item]='sum'
            else:
                D[item]='sum'

        return self.regrouped.groupby('Team').agg(D)
    def totals(self):
        for item in self.features:
            if is_integer_dtype(self.weighted[item]) and item!='G':
                self.weighted[item]=(self.weighted[item]/self.weighted['IP'])*162*9

    def get(self):
        D={}
        for item in self.features:
            D[item]=item+'_pitch'
        return self.weighted.rename(columns=D)
class weightedHitting(CalcTeamStatistics):
    def __init__(self,df,weights):
        self.weights=weights
        super().__init__(df)
        self.weightedAvg()
        self.regrouped=self.regroup()

    def weightedAvg(self):
        for ind, row in self.grouped.iterrows():
            multiplyer=self.weights[self.grouped.loc[ind,'Status']]
            for item in self.features:
                if not is_integer_dtype(self.grouped[item]):
                     self.grouped.at[ind,item]=self.grouped.loc[ind,item]*multiplyer
    def regroup(self):
        D={}
        for item in self.features:
            D[item]='sum'

        regrouped=self.grouped.groupby('Team').agg(D).reset_index()
        return regrouped
    def get(self):
        for item in self.features:
            if is_integer_dtype(self.regrouped[item]):
                print(item)
                self.regrouped=LinearModel(self.regrouped,item).predict()
        return self.regrouped

class LinearModel:
    def __init__(self,df,col):
        self.df=df
        self.col=col
        self.data=pd.read_csv("TeamWins_UpdatedVersion.csv")

        self.features=self.Features()

        self.X=self.data[self.features]
        self.y=self.data[self.col]
        self.model = LinearRegression()
        self.model.fit(self.X, self.y)


    def Features(self):
        L=['AB','AVG','OBP']
        if self.col=='HR':
            L.append('SLG')
        L=[item for item in L if item!=self.col]
        return L
    def predict(self):
        pred_x=self.df[self.features]
        self.df[self.col]=self.model.predict(pred_x)
        return self.df
def is_Pitcher(pos):
    if 'P' in pos:
        return True
    else:
        return False

if __name__=='__main__':
    main()