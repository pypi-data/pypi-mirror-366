import os.path
import unittest

from tests import *
from umu_commander import configuration
from umu_commander.configuration import Configuration as config


class Config(unittest.TestCase):
    def setUp(self):
        configuration.CONFIG_DIR = TESTING_DIR
        configuration.DB_DIR = TESTING_DIR
        setup()

    def tearDown(self):
        teardown()

    def test_missing_config(self):
        config.load()
        self.assertTrue(
            os.path.exists(os.path.join(TESTING_DIR, configuration.CONFIG_NAME))
        )
        config.load()
