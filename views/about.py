from flask import Blueprint, render_template

about_blueprint = Blueprint("about", __name__)


@about_blueprint.route("/")
def index():
	return render_template("about.html")
