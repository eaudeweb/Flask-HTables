import flask
import htables


admin_blueprint = flask.Blueprint('htables_admin', __name__,
                                  template_folder='templates')

@admin_blueprint.route('/')
def index():
    app = flask.current_app
    htables_ext = app.extensions['htables']
    return flask.render_template('htables_admin_index.html',
                                 admin_adapters=htables_ext.admin_adapters)


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

    def __init__(self, app=None):
        if app is not None:
            self.initialize_app(app)
        self.admin = admin_blueprint
        self.admin_adapters = {}

    def initialize_app(self, app):
        assert app.config['HTABLES_ENGINE'] == 'sqlite'
        self.db = htables.SqliteDB(app.config['HTABLES_SQLITE_PATH'])
        app.teardown_request(self._close_session)
        app.extensions['htables'] = self

    def _close_session(self, err):
        top = flask._request_ctx_stack.top
        if not hasattr(top, 'htables_session'):
            return
        try:
            session = top.htables_session
            if err is None:
                session.commit()
            else:
                session.rollback()
            self.db.put_session(session)
        except:
            flask.current_app.logger.exception("Failed to close database")

    def _get_or_create_session(self):
        top = flask._request_ctx_stack.top
        if top is None:
            raise RuntimeError('working outside of request context')
        if not hasattr(top, 'htables_session'):
            top.htables_session = self.db.get_session()
            top.htables_session._debug = top.app.debug or top.app.testing
        return top.htables_session

    @property
    def session(self):
        return self._get_or_create_session()
