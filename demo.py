import flask
from flask.ext.htables import HTables


app = flask.Flask(__name__)
htables = HTables(app)
app.register_blueprint(htables.admin, url_prefix='/admin')


if __name__ == '__main__':
    app.run(debug=True)
