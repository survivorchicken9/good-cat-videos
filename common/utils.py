import pickle
import pandas as pd


def simple_regression_test_processing(video_title: str):
    processed_list = video_title.lower().split()
    test_dataframe = pd.DataFrame()

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

    for good_word in good_words:
        for processed_word in processed_list:
            if good_word == processed_word:
                test_dataframe.loc[0, f"{good_word}_yn"] = 1
                continue
            test_dataframe.loc[0, f"{good_word}_yn"] = 0

    test_dataframe["len_title"] = len(processed_list)
    return test_dataframe


def load_model(model_name):
    file_name = f"classifier/{model_name}.p"
    with open(file_name, "rb") as pickled:
        data = pickle.load(pickled)
        model = data["model"]
    return model
