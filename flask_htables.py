import flask
import htables


admin_blueprint = flask.Blueprint('htables_admin', __name__)

@admin_blueprint.route('/')
def index():
    app = flask.current_app
    session = app.extensions['htables'].session
    return flask.render_template('index.html', session=session)


@admin_blueprint.route('/<string:name>')
def table(name):
    app = flask.current_app
    session = app.extensions['htables'].session
    return flask.render_template('table.html', name=name, table=session[name])


class HTables(object):

    def __init__(self, app, tables, connect):
        self.schema = htables.Schema()
        for name in tables:
            self.schema.define_table(name, name)
        self.connect = connect
        if app is not None:
            self.initialize_app(app)
        self.admin = admin_blueprint

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
            top.htables_session = htables.SqliteSession(
                    self.schema, self.connect(), {})
        return top.htables_session

    @property
    def session(self):
        return self._get_or_create_session()
