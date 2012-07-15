import os.path
import sqlite3
import flask
from flask.ext.htables import HTables


def main(tmp):
    db_path = os.path.join(tmp, 'db.sqlite')
    app = flask.Flask(__name__)
    htables = HTables(app, tables=['person', 'sport'],
                      connect=lambda: sqlite3.connect(db_path))
    app.register_blueprint(htables.admin, url_prefix='/admin')

    with app.test_request_context():
        htables.session.create_all()
    app.run(debug=True)


if __name__ == '__main__':
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp()
    try:
        main(tmp)
    finally:
        shutil.rmtree(tmp)
