import sqlite3
import flask
from flask.ext.htables import HTables


connection = sqlite3.connect(':memory:')


app = flask.Flask(__name__)
htables = HTables(app, tables=['person', 'sport'],
                  get_connection=lambda: connection)
app.register_blueprint(htables.admin, url_prefix='/admin')


if __name__ == '__main__':
    with app.test_request_context():
        htables.session.create_all()
    app.run(debug=True)
