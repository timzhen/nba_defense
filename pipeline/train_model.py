import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv('../data/all_seasons_combined.csv')


# 2015-16 and 2016-17 are missing on_ball_matchup_def_score and/or def_reb_score
# for either all or most rows -- those stats simply weren't tracked yet those seasons.
# rather than fill in fabricated averages for data that never existed, drop these
# two seasons entirely and only train on seasons with complete, real tracking data.
df = df[~df['SEASON'].isin(['2015-16', '2016-17', '2025-26'])]

df['on_ball_matchup_def_score'] = df['on_ball_matchup_def_score'].fillna(df['on_ball_matchup_def_score'].mean())


# your 5 category scores are the inputs
X = df[['rim_protection_score', 'shot_contesting_score', 'ball_disruption_score',
        'on_ball_matchup_def_score', 'def_reb_score']]
# X = my inputs -- the scores the model uses to make predictions

y = df['got_dpoy_votes']
# y = my label/target -- the thing we are trying to predict

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# test_size = 0.2 -- splits the 590 rows into 80% for training (472 rows), 20% held back for testing (118 rows)
# random_state = 42 -- makes the split reproducible, keeps the random seed the same


model = LogisticRegression(class_weight='balanced')  # helps with your imbalanced labels, tells the model to pay extra attention to rare positives examples instead of ignoring them
model.fit(X_train, y_train) # algrotihm looks at 472 training examples and learns mathematical relationship between 5 scores and whether a player got DPOY votes

predictions = model.predict(X_test)
# make the trained model predict on the 118 test rows that it hasn't seen before during training

print(accuracy_score(y_test, predictions)) # compares model's predictions against real, true answers for the 118 test rows and gives a single percentage of how often the model is correct
print(classification_report(y_test, predictions)) # shows precision, recall, and F1-score specifically

print('\nLearned weights per category:')
for category, weight in zip(X.columns, model.coef_[0]): # zip pairs up each category name w its corresponding learned weight
    print(f'  {category}: {weight:.3f}')
    # which defensive skills most strongly correlate with real world DPOY recognition


print(f'Loaded shape: {df.shape}')  # ADD THIS

df = df[~df['SEASON'].isin(['2015-16', '2016-17'])]
print(f'After season filter: {df.shape}')  # ADD THIS
print(df['SEASON'].value_counts())  # ADD THIS - see which seasons are actually present

import joblib # standard tool to save trained scikit learn models to disk
joblib.dump(model, '../nba-defense-backend/dpoy_model.pkl')