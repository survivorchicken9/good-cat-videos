from flask import Blueprint, render_template

process_blueprint = Blueprint("process", __name__)


@process_blueprint.route("/")
def index():
    return render_template("process.html")
