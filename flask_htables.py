import flask
import htables


admin_blueprint = flask.Blueprint('htables_admin', __name__,
                                  template_folder='templates')

@admin_blueprint.route('/')
def index():
    app = flask.current_app
    session = app.extensions['htables'].session
    return flask.render_template('htables_admin_index.html', session=session)


@admin_blueprint.route('/<string:name>')
def table(name):
    app = flask.current_app
    htables_ext = app.extensions['htables']
    row_adapter = htables_ext.admin_adapters.get(name, DefaultAdapter)
    return flask.render_template('htables_admin_table.html',
                                 name=name,
                                 table=htables_ext.session[name],
                                 row_adapter=row_adapter)


class DefaultAdapter(object):

    columns = ['']
    limit = 100

    def __init__(self, row):
        value = repr(row)
        if len(value) > self.limit:
            value = value[:self.limit - 4] + ' ...'
        setattr(self, '', value)


class HTables(object):

    def __init__(self, app):
        if app is not None:
            self.initialize_app(app)
        self.admin = admin_blueprint
        self.admin_adapters = {}

    def initialize_app(self, app):
        app.teardown_request(self._close_database)
        app.extensions['htables'] = self

    def _close_database(self, err):
        top = flask._request_ctx_stack.top
        if not hasattr(top, 'htables_session'):
            return
        try:
            if err is None:
                top.htables_session.commit()
            else:
                top.htables_session.rollback()
            del top.htables_session
        except:
            flask.current_app.logger.exception("Failed to close database")

    def _get_or_create_session(self):
        top = flask._request_ctx_stack.top
        if top is None:
            raise RuntimeError('working outside of request context')
        if not hasattr(top, 'htables_session'):
            assert top.app.config['HTABLES_ENGINE'] == 'sqlite'
            db = htables.SqliteDB(top.app.config['HTABLES_SQLITE_PATH'])
            top.htables_session = db.get_session()
        return top.htables_session

    @property
    def session(self):
        return self._get_or_create_session()
