# MLB_2024: Predicting 2024 Season Outcomes

As the spring of 2024 approached, I began thinking about baseball. I had been eager to do a baseball project but had yet to get around to it.

I was particularly interested in how well one could predict the outcome of the entire season based solely on the teams' overall statistics for both pitching and hitting. Furthermore, I was interested in which statistics were most correlated with team wins. In this project, I use data from previous years to predict the outcome of the 2024 season. Particularly, I determine the amount of wins we can expect to see from each team. Who will be the division winners? Who will be in the wildcard games?

**Data Gathering and Processing:**

Suprisingly, the data for this project was not easy to come by. There were no CSV files on the web which had columns for both team wins and team statistics. As such, the project became very much about data gathering and processing as much as modeling and analysis. Many of the Python files in this project are for building the dataset through web scraping.

**Important Note:** The web scraping scripts (`scrape_mlb.py`, etc.) are included to demonstrate how the dataset was constructed. However, due to potential changes in website structure or API availability, **it's highly unlikely these scripts will run successfully without significant modifications.** **The resulting CSV files from these scripts are provided in the repository's `data/` folder.**

**Project Focus:**

The main focus of this project is on:

* **`Creating_2024_Team_Stats.ipynb`**: This notebook details the feature engineering and preprocessing steps. A key aspect of this process was calculating relative performance metrics, which show how a team's statistics compare to their division, league, and the entire MLB. These relative metrics proved to be highly important for accurate modeling.
* **`Predicting_2024.ipynb`**: This notebook contains the modeling and results. Here we see the XGBoost model being created, tuned and evaluated.

**Model Performance:**

The final XGBoost model achieved the following performance metrics:

* **R2 (Test Set):** 0.8440
* **RMSE (Test Set):** 4.7704

**Model Improvements:**

Significant improvements were observed during the modeling process:

* **Grid Search:** Hyperparameter tuning using grid search led to a considerable increase in model performance.
* **Permutation Feature Importance (PFI):** Feature selection based on PFI further refined the model, improving generalization capabilities, as evidenced by cross-validation scores.

**2024 Season Predictions and Observations:**

As for the 2024 season, we will have to see how it shakes out. The predicted standings generally align with what one might expect, however I do notice some surprises. For example, I would not expect the Brewers to have as bad of a season as predicted. Furthermore, I would expect the Dodgers to produce more than 89 wins. Some of these discrepancies could possibly be explained by difficulties in the data gathering and preprocessing steps. Nevertheless, this was an interesting analysis and it reinforces our understanding about what statistics generally produce wins in the MLB.

**How to Use This Repository:**

1.  Clone the repository: `git clone https://github.com/jprich1984/MLB_2024.git`
2.  Navigate to the project directory: `cd MLB_2024`
3.  Install the required packages: `pip install -r requirements.txt`
4.  Explore the notebooks `Creating_2024_Team_Stats.ipynb` and `Predicting_2024.ipynb` to understand the data processing, modeling, and results.
