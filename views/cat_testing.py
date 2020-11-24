from flask import Blueprint, render_template, request
import classifier.simple_heuristics as simple_heuristics
from common.utils import load_model, linear_regression_test_processing

cat_testing_blueprint = Blueprint("cat_testing", __name__)


@cat_testing_blueprint.route("/", methods=["GET", "POST"])
def check_video():
    # TODO: create general preprocessing function for all user title inputs
    if request.method == "POST":
        title = request.form["title"]
        classifier_type = request.form.get("classifier_type")
        
        # catch empty titles
        if not title:
            return render_template("main.html")  # add the flash message instead of this for clarity on UI

        # and now we start the magic
        # TODO: show on results page what kind of classifier was used
        if classifier_type == 'simple_heuristics':
            model = simple_heuristics
            if model.predict(title):
                return render_template("result_good.html")
            return render_template("result_bad.html")

        else:
            # only linear regression method for now
            model = load_model(classifier_type)
            result = model.predict(linear_regression_test_processing(title))
            if result >= 36:
                return render_template("result_good.html")
            return render_template("result_bad.html")

    return render_template("main.html")
