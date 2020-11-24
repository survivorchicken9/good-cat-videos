import pickle
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for
from classifier.simple_heuristics import judge_video


# TODO: MOVE THIS INTO COMMON DIR HELPER FILE
def simple_test_processing(video_title: str):
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
        "kittens"
    ]
    
    for good_word in good_words:
        for processed_word in processed_list:
            if good_word == processed_word:
                test_dataframe.loc[0, f'{good_word}_yn'] = 1
                continue
            test_dataframe.loc[0, f'{good_word}_yn'] = 0
    
    test_dataframe['len_title'] = len(processed_list)
    return test_dataframe


# TODO: MOVE THIS INTO COMMON DIR HELPER FILE
def load_models():
    file_name = "classifier/model_file.p"
    with open(file_name, 'rb') as pickled:
        data = pickle.load(pickled)
        model = data['model']
    return model


cat_testing_blueprint = Blueprint("cat_testing", __name__)


@cat_testing_blueprint.route("/", methods=["GET", "POST"])
def check_video():
    if request.method == "POST":
        title = request.form["title"]

        # so this is where we do the magic eventually
        
        # simple heuristic method
        # if judge_video(title):
        #     return render_template("cat_result_good.html")
        # return render_template("cat_result_bad.html")
        
        # simple linreg method
        linreg_model = load_models()
        result = linreg_model.predict(simple_test_processing(title))
        if result >= 36:
            return render_template("cat_result_good.html")
        return render_template("cat_result_bad.html")

    return render_template("cat_main.html")
