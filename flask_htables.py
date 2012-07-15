import flask
import htables


admin_blueprint = flask.Blueprint('htables_admin', __name__)

@admin_blueprint.route('/')
def index():
    return flask.render_template('index.html')


class HTables(object):

    def __init__(self, app, tables, get_connection):
        self.schema = htables.Schema()
        for name in tables:
            self.schema.define_table(name, name)
        self.get_connection = get_connection
        self.initialize_app(app)
        self.admin = admin_blueprint

    def initialize_app(self, app):
        app.teardown_request(self._close_database)

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
                    self.schema, self.get_connection(), {})
        return top.htables_session

    @property
    def session(self):
        return self._get_or_create_session()
