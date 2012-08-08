import os.path
import flask
from flask.ext.htables import HTables, DefaultAdapter


def main(tmp):
    db_path = os.path.join(tmp, 'db.sqlite')
    app = flask.Flask(__name__)
    app.config.update(HTABLES_ENGINE='sqlite',
                      HTABLES_SQLITE_PATH=db_path)
    htables = HTables(app)
    with app.test_request_context():
        for name in ['person', 'sport']:
            htables.session[name].create_table()
            htables.admin_adapters[name] = DefaultAdapter
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
