import flask


admin_blueprint = flask.Blueprint('htables_admin', __name__)

@admin_blueprint.route('/')
def index():
    return flask.render_template('index.html')


class HTables(object):

    def __init__(self, app=None):
        if app is not None:
            self.initialize_app(app)
        self.admin = admin_blueprint

    def initialize_app(self, app):
        pass
