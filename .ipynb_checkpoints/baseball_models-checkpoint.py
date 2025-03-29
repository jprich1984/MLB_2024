import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split as tts
import numpy as np
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def main():
    """The goal here will be to make a model that predicts the amount of wins a team will earn, based on their
    statistics, and then apply the model to 2024 data."""
    data=pd.read_csv("TeamWins_UpdatedVersion.csv") #Data contains teams year stats with the amount of wins for each season
    features=['AVG','OBP','SLG','HR','BB','BB_pitch','SO_pitch','WHIP_pitch','AVG_pitch'] #These are the features for which
    #to build the model.
    data=leagueStats(data,features).applyAgg()  #Adds columns to the dataframe which are the differences between
    #the teams statistics and those of their diviison/league.  Also adds columns for the differences between the team stats and
    #the entire MLB.

    rf=randomForrests(data,features) #Random forrest regressor
    print("\nRoot Mean Squared Error of Model:", rf.getError())
    data24=pd.read_csv('2024teamStatsProjections.csv')#Data that contains each teams average career stats.
    data24=leagueStats(data24,features).applyAgg()#Transform the same way to include the difference between the team
    #and the league,division, and mlb.
    data24=rf.makePreds(data24)#Use model to make predictions. Adds a new column called 'Prediction'
    playoffPicture(data24).Print()#Print the results for each division as well as the wildcard teams.



class playoffPicture:
    def __init__(self,df):
        self.df=df
        self.divisions=[]
        divisions = self.df['DIVISION'].unique()
        self.leagues = self.df['LEAGUE'].unique()
        for item in self.leagues:
            for elem in divisions:
                self.divisions.append((item, elem))
        self.division_winners=[]
        self.divWinFrames=self.divisionWinners()
        self.wildcards=self.getWildcard()

    def  Print(self):
        for item in self.divWinFrames:
            print(f"Division {item[0]} {item[1]}\n{item[2].to_markdown()}")
        print("\t\t\t\t\tWildcards")
        for item in self.wildcards:
            print(f"League {item[0]}\n\t{item[1].to_markdown()}")



    def divisionWinners(self):
        dataFrames=[]
        for item in self.divisions:
            df=self.df[(self.df['LEAGUE']==item[0])&(self.df['DIVISION']==item[1])]
            df=df.sort_values(by='Prediction',ascending=False)
            self.division_winners.append(df['CODE'].head().values[0])
            df=df[['CODE','Prediction']]
            df=df.rename(columns={'CODE':'Team','Prediction':'Wins'})
            dataFrames.append((item[0],item[1],df))
        return dataFrames
    def getWildcard(self):
        wildcards=[]
        for league in self.leagues:
            df=self.df[self.df['LEAGUE']==league]
            df=self.df.sort_values(by='Prediction',ascending=False)
            df=df[~df['CODE'].isin(self.division_winners)]
            df = df[['CODE', 'Prediction']]
            df = df.rename(columns={'CODE': 'Team', 'Prediction': 'Wins'})
            wildcards.append((league,df.head(3)))
        return wildcards
class randomForrests:
    def __init__(self,df,features):
        self.df=df
        """Add the difference metrics to the list of features.  These are metrics for the difference between the stats
        of the team and those of their division/league as well as the entire mlb."""
        self.features=features+['DivDiff_'+item for item in features]+['LeagueDiff_'+item for item in features]+['mlbDiff_'+item for item in features]
        self.regressor = RandomForestRegressor(n_estimators=250, random_state=0, min_samples_split=5)
        np.random.seed(458)
        self.train,self.test=tts(self.df, test_size=0.2)
        self.X_train=self.train[self.features]
        self.y_train=self.train['WINS']
        self.X_test=self.test[self.features]
        self.y_test=self.test['WINS']
        self.model=self.Model()


    def getParams(self):
        param_grid = {
            'n_estimators': [25, 50, 100, 150,200],
            'max_features': ['sqrt', 'log2', None],
            'max_depth': [3, 6, 9,12],
            'max_leaf_nodes': [3, 6, 9,12],
            'min_samples_split':[3,6,9,12]
        }

        grid_search = GridSearchCV(RandomForestRegressor(),
                                   param_grid=param_grid)
        grid_search.fit(self.X_train, self.y_train)
        print(grid_search.best_estimator_)
    def Model(self):
        """After tuning, I could not do better than the default parameters with 250 trees"""
        regressor = make_pipeline(StandardScaler(), RandomForestRegressor(n_estimators=200,max_depth=7))
        regressor.fit(self.X_train,self.y_train)
        return regressor
    def getError(self):
        """Returns the Root Mean Squared Error"""
        self.test['pred']=self.model.predict(self.X_test)
        return self.RMSE(self.test['WINS'],self.test['pred'])
    def RMSE(self,y,y_hat):
        return np.sqrt(sum((y-y_hat)**2)/len(y))
    def feature_selection(self):
        """Prints the most important features"""
        sel = SelectFromModel(RandomForestRegressor(n_estimators=200,max_depth=7, random_state=0, min_samples_split=6,max_leaf_nodes=14,min_samples_leaf=5))
        sel.fit(self.X_train, self.y_train)
        print(sel.get_support())
        selected_feat = self.X_train.columns[(sel.get_support())]
        print(selected_feat)
    def makePreds(self,df):
        """Returns a DataFrame with the predictions(amount of wins for each team).  The wins are adjusted to
        Account for the fact that there should be 2430 wins in a season."""
        X=df[self.features]
        df['Prediction']=self.model.predict(X)
        return self.CorrectWins(df)
    def CorrectWins(self,df):
        """Returns the amount of wins proportional to the total wins of all teams but in an amount that makes the total
        Amount of wins equal to the expected amount of wins for a season 2430."""
        predicted_total=df['Prediction'].sum()
        df['Prediction']=round((df['Prediction']/predicted_total)*(162*30/2))
        return df
class leagueStats:
    def __init__(self,df,features):
        self.df=df
        self.aggregates=self.features_dict(features)#dictionary that holds the columns as the key and the aggregate function
        #that should be applied as the value.
        self.features=features #The statistics for which we wish to calculate the difference between the league, division,mlb.


    def features_dict(self,F):
        """Returns a dictionary that is designed to be passed to the agg function, i.e {col_name:agg_func}."""
        D={}
        for i in F:
            D[i]='mean'
        return D

    def aggregatedStats(self,row,which='Division'):
        L=[]
        if which=='Division':
            df=self.df[(self.df['Year']==row['Year'])&(self.df['LEAGUE']==row['LEAGUE'])&(self.df['DIVISION']==row['DIVISION'])&
                       (self.df['CODE']!=row['CODE'])]
        elif which=='League':
            df = self.df[(self.df['Year'] == row['Year']) & (self.df['LEAGUE'] == row['LEAGUE'])&(self.df['CODE']!=row['CODE'])]
        else:
            df=self.df[(self.df['Year'] == row['Year']) &(self.df['CODE']!=row['CODE'])]
        for item in self.features:
            av=df[item].mean()
            L.append(row[item]-av)
        return pd.Series(L)
    def applyAgg(self):
        """Returns a dataFrame that includes columns for the teams stats relative to the teams league and division, as
        well as the entire mlb."""
        self.df[['DivDiff_'+item for item in self.features]]=self.df.apply(self.aggregatedStats ,axis=1)
        self.df[['LeagueDiff_'+item for item in self.features]]=self.df.apply(self.aggregatedStats,which='League',axis=1)
        self.df[['mlbDiff_'+item for item in self.features]]=self.df.apply(self.aggregatedStats, which='MLB',axis=1)
        return self.df
if __name__=='__main__':
    main()