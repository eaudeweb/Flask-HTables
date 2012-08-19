import unittest
import tempfile
import shutil
import flask


POSTGRESQL_TEST_URI = "postgresql://localhost/test"


class DatabaseAccessTest(unittest.TestCase):

    def test_new_record_is_found(self):
        import flask_htables
        app = flask.Flask(__name__)
        app.config.update(HTABLES_ENGINE='sqlite',
                          HTABLES_SQLITE_PATH=':memory:')
        ht = flask_htables.HTables(app)
        with app.app_context():
            table = ht.session['person']
            table.create_table()
            person = table.new(hello="world")
            person.save()
            self.assertEqual(table.find_first(), {"hello": "world"})

    def htables_in_debug_mode(self, app):
        import flask_htables
        app.config.update(HTABLES_ENGINE='sqlite',
                          HTABLES_SQLITE_PATH=':memory:')
        ht = flask_htables.HTables(app)
        with app.app_context():
            table = ht.session['person']
            table.create_table()
            try:
                table.new(int_value=13)
            except AssertionError:
                return True
            else:
                return False

    def test_debug_is_disabled_by_default(self):
        app = flask.Flask(__name__)
        self.assertFalse(self.htables_in_debug_mode(app))

    def test_debug_is_propagated(self):
        app = flask.Flask(__name__)
        app.config['DEBUG'] = True
        self.assertTrue(self.htables_in_debug_mode(app))

    def test_debug_triggered_by_testing_mode(self):
        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        self.assertTrue(self.htables_in_debug_mode(app))


class HtablesBackendTest(unittest.TestCase):

    def create_app(self, **config):
        import flask_htables
        app = flask.Flask(__name__)
        app.config.update(config)
        ht = flask_htables.HTables(app)
        return app, ht

    def test_sqlite(self):
        import htables
        app, ht = self.create_app(HTABLES_ENGINE='sqlite',
                                  HTABLES_SQLITE_PATH=':memory:')
        self.assertIsInstance(ht.db, htables.SqliteDB)
        with app.app_context():
            self.assertIsNotNone(ht.session['person'])

    def test_postgresql(self):
        app, ht = self.create_app(HTABLES_ENGINE='postgresql',
                                  HTABLES_POSTGRESQL_URI=POSTGRESQL_TEST_URI)
        with app.app_context():
            self.assertIsNotNone(ht.session['person'])


class DatabaseAutocommitTest(unittest.TestCase):

    def setUp(self):
        import flask_htables
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.app = flask.Flask(__name__)
        self.app.config.update(HTABLES_ENGINE='sqlite',
                               HTABLES_SQLITE_PATH=self.tmp + '/db.sqlite')
        self.ht = flask_htables.HTables(self.app)
        with self.app.app_context():
            self.ht.session['person'].create_table()

    def test_commit_on_success(self):
        with self.app.app_context():
            self.ht.session['person'].new({'name': 'black'}).save()
            # autocommit should occur here

        with self.app.app_context():
            self.ht.session.rollback()
            self.assertEqual(list(self.ht.session['person'].find()),
                             [{'name': 'black'}])

    def test_rollback_on_error(self):
        with self.assertRaises(ValueError):
            with self.app.app_context():
                self.ht.session['person'].new({'name': 'black'}).save()
                raise ValueError # should trigger rollback

        with self.app.app_context():
            self.assertEqual(list(self.ht.session['person'].find()), [])
