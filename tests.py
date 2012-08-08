import unittest
import tempfile
import shutil
import flask


class DatabaseAccessTest(unittest.TestCase):

    def test_new_record_is_found(self):
        import flask_htables
        app = flask.Flask(__name__)
        app.config.update(HTABLES_ENGINE='sqlite',
                          HTABLES_SQLITE_PATH=':memory:')
        ht = flask_htables.HTables(app)
        with app.test_request_context():
            table = ht.session['person']
            table.create_table()
            person = table.new(hello="world")
            person.save()
            self.assertEqual(table.find_first(), {"hello": "world"})

    def test_debug_is_propagated(self):
        import flask_htables
        app = flask.Flask(__name__)
        app.config.update(HTABLES_ENGINE='sqlite',
                          HTABLES_SQLITE_PATH=':memory:',
                          DEBUG=True)
        ht = flask_htables.HTables(app)
        with app.test_request_context():
            table = ht.session['person']
            table.create_table()
            with self.assertRaises(AssertionError):
                table.new(int_value=13)


class DatabaseAutocommitTest(unittest.TestCase):

    def setUp(self):
        import flask_htables
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.app = flask.Flask(__name__)
        self.app.config.update(HTABLES_ENGINE='sqlite',
                               HTABLES_SQLITE_PATH=self.tmp + '/db.sqlite')
        self.ht = flask_htables.HTables(self.app)
        with self.app.test_request_context():
            self.ht.session['person'].create_table()

    def test_commit_on_success(self):
        with self.app.test_request_context():
            self.ht.session['person'].new({'name': 'black'}).save()
            # autocommit should occur here

        with self.app.test_request_context():
            self.ht.session.rollback()
            self.assertEqual(list(self.ht.session['person'].find()),
                             [{'name': 'black'}])

    def test_rollback_on_error(self):
        with self.assertRaises(ValueError):
            with self.app.test_request_context():
                self.ht.session['person'].new({'name': 'black'}).save()
                raise ValueError # should trigger rollback

        with self.app.test_request_context():
            self.assertEqual(list(self.ht.session['person'].find()), [])
