from flask import Blueprint, render_template, request, redirect, url_for
from classifier.simple_heuristics import judge_video

cat_testing_blueprint = Blueprint("cat_testing", __name__)


@cat_testing_blueprint.route("/", methods=["GET", "POST"])
def check_video():
    if request.method == "POST":
        title = request.form["title"]

        # so this is where we do the magic eventually
        if judge_video(title):
            return render_template("cat_result_good.html")
        return render_template("cat_result_bad.html")

    return render_template("cat_main.html")
