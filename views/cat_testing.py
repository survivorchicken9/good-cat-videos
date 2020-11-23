from flask import Blueprint, render_template, request, redirect, url_for

cat_testing_blueprint = Blueprint("cat_testing", __name__)


@cat_testing_blueprint.route("/", methods=["GET", "POST"])
def check_video():
    if request.method == "POST":
        title = request.form["title"]
        title_lower = title.lower()

        # so this is where we do the magic eventually
        if "cat" in title_lower and "dog" not in title_lower:
            return render_template("cat_result_good.html")
        return render_template("cat_result_bad.html")

    return render_template("cat_main.html")
