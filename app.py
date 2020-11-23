from flask import Flask, render_template
from views.cat_testing import cat_testing_blueprint


app = Flask(__name__)


app.register_blueprint(cat_testing_blueprint)


if __name__ == '__main__':
    app.run(debug=True)
