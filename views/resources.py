from flask import Blueprint, render_template

resources_blueprint = Blueprint("resources", __name__)


@resources_blueprint.route("/")
def index():
    return render_template("resources.html")
