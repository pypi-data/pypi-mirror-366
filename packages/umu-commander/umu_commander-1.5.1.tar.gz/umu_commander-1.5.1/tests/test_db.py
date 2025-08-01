import unittest
from json import JSONDecodeError

from tests import *
from umu_commander.configuration import Configuration as config
from umu_commander.database import Database as db


class Database(unittest.TestCase):
    def setUp(self):
        config.DB_DIR = TESTING_DIR
        setup()

    def tearDown(self):
        teardown()

    def test_missing_db(self):
        db.load()
        self.assertEqual(db.get(), {})

    def test_malformed_db(self):
        with open(os.path.join(config.DB_DIR, config.DB_NAME), "tw") as db_file:
            db_file.write("{")

        with self.assertRaises(JSONDecodeError):
            db.load()

    def test_addition_removal(self):
        db.load()
        db.get(PROTON_DIR_1, PROTON_BIG).append(USER_DIR)

        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertIn(USER_DIR, db.get(PROTON_DIR_1, PROTON_BIG))

        db.get(PROTON_DIR_1, PROTON_BIG).remove(USER_DIR)

        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertNotIn(USER_DIR, db.get(PROTON_DIR_1, PROTON_BIG))

        del db.get(PROTON_DIR_1)[PROTON_BIG]
        self.assertNotIn(PROTON_BIG, db.get(PROTON_DIR_1))
