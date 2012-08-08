import unittest
import flask


class DatabaseAccessTest(unittest.TestCase):

    def test_new_record_is_found(self):
        import flask_htables
        app = flask.Flask(__name__)
        def connect():
            import sqlite3
            return sqlite3.connect(':memory:')
        ht = flask_htables.HTables(app, [], connect)
        with app.test_request_context():
            table = ht.session['person']
            table.create_table()
            person = table.new(hello="world")
            person.save()
            self.assertEqual(table.find_first(), {"hello": "world"})
