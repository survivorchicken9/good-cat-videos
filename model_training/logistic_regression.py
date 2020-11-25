import pickle
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np
import pandas as pd

# option for formatting during notebook session
# pd.set_option("display.float_format", lambda x: "%.2f" % x)  # just nice formatting

# need this for taking out infinite values
pd.set_option("mode.use_inf_as_na", True)

# keywords used: funny cats, cat compilation, cat videos, cats

# read data in and do preprocessing to calculate quality metric for linreg model (like to dislike ratio)
df = pd.read_csv("../no_duplicates_cat_results.csv")
df["Quality Metric"] = df["likeCount"] / df["dislikeCount"]
df["Quality"] = np.where(df["Quality Metric"] > 10, 1, 0)
df_logreg = df[["title", "Quality"]].dropna()
df_logreg["title_processed"] = df_logreg["title"].str.lower().str.split()

# output from CountVectorizer only unigrams
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

# create yes/no columns for target words
for word in good_words:
    df_logreg[f"{word}_yn"] = 0

# add 1 if word in title and 0 if not (filling in features)
for row in df_logreg.itertuples():
    title_processed_list = df_logreg.loc[row[0], "title_processed"]
    for good_word in good_words:
        for title_word in title_processed_list:
            if good_word == title_word:
                df_logreg.loc[row[0], f"{good_word}_yn"] = 1
                continue
            df_logreg.loc[row[0], f"{good_word}_yn"] = 0

# add extra feature for the length of the title
df_logreg["len_title"] = df_logreg["title_processed"].str.len()

# define features and target
X = df_logreg.drop(columns=["title", "title_processed", "Quality"])
y = df_logreg["Quality"]

# train and test the model with basic LogisticRegression and CV
# train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1, test_size=0.2)
# linreg_model = LinearRegression(normalize=True)
# linreg_model.fit(train_X, train_y)
# val_predictions = linreg_model.predict(val_X)
# print(mean_absolute_error(val_y, val_predictions))

# train model with all data and pickle for use in production
logreg_model = LogisticRegressionCV(solver='liblinear', cv=6)
logreg_model.fit(X, y)
pickled_model = {"model": logreg_model}
pickle.dump(pickled_model, open("../classifier/logistic_regression" + ".p", "wb"))
