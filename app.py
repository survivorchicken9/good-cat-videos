from flask import Flask
from views.about import about_blueprint
from views.main import main_blueprint
from views.process import process_blueprint
from views.resources import resources_blueprint

app = Flask(__name__)


app.register_blueprint(main_blueprint)
app.register_blueprint(about_blueprint, url_prefix='/about')
app.register_blueprint(process_blueprint, url_prefix='/process')
app.register_blueprint(resources_blueprint, url_prefix='/resources')


if __name__ == "__main__":
    app.run(debug=True)
