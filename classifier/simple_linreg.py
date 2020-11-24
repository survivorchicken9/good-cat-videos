import pickle
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np
import pandas as pd


pd.set_option("display.float_format", lambda x: "%.2f" % x)  # just nice formatting
pd.set_option("mode.use_inf_as_na", True)

# keywords used: funny cats, cat compilation, cat videos, cats

# read data in and process
df = pd.read_csv("cat_test_results.csv")
df["Quality Metric"] = df["likeCount"] / df["dislikeCount"]
df["Quality"] = np.where(df["Quality Metric"] > 10, 1, 0)
df_linreg = df[["title", "Quality Metric"]].dropna()
df_linreg["title_processed"] = df_linreg["title"].str.lower().str.split()

good_words = [
    "2020",
    "animals",
    "baby",
    "cats",
    "best",
    "funny",
    "cat",
    "compilation",
    "cute",
    "dog",
    "animal",
    "try",
    "laugh",
    "animal",
    "not",
    "kitten",
    "games",
    "dogs",
    "kittens",
]

for word in good_words:
    df_linreg[f"{word}_yn"] = 0

for row in df_linreg.itertuples():
    title_processed_list = df_linreg.loc[row[0], "title_processed"]
    for good_word in good_words:
        for title_word in title_processed_list:
            if good_word == title_word:
                df_linreg.loc[row[0], f"{good_word}_yn"] = 1
                continue
            df_linreg.loc[row[0], f"{good_word}_yn"] = 0

df_linreg["len_title"] = df_linreg["title_processed"].str.len()

y = df_linreg["Quality Metric"]
X = df_linreg.drop(columns=["title", "title_processed", "Quality Metric"])

train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1, test_size=0.2)
linreg_model = LinearRegression(normalize=True)
linreg_model.fit(train_X, train_y)
val_predictions = linreg_model.predict(val_X)
# print(mean_absolute_error(val_y, val_predictions))

pickled_model = {'model': linreg_model}
pickle.dump(pickled_model, open('model_file' + ".p", "wb"))
