from flask import Blueprint, render_template, request, redirect, url_for
from classifier.simple_heuristics import judge_video
from common.utils import load_model, simple_linreg_test_processing

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
        linreg_model = load_model()
        result = linreg_model.predict(simple_linreg_test_processing(title))
        if result >= 36:
            return render_template("cat_result_good.html")
        return render_template("cat_result_bad.html")

    return render_template("cat_main.html")
