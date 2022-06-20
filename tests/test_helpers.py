# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# Unit test file
# tests/test_helpers.py

# Importacion de librerias necesarias
import unittest
import logging
from http import HTTPStatus

# Importacion del archivo principal
import app_server
from src import helpers


class HelpersTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = app_server.app
        app.logger.setLevel(logging.CRITICAL)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        print("Starting testing helper methods of the app server...")

    @classmethod
    def tearDownClass(cls):
        print("Finished testing helper methods of the app server!")

    def test_config_log_should_return_0(self):
        r = helpers.config_log()
        self.assertEqual(0, r)

    def test_handle_database_error_should_return_service_unavailable(self):
        r = helpers.handleDatabasebError("test")
        self.assertEqual(HTTPStatus.SERVICE_UNAVAILABLE, r[1])
        self.assertEqual(-1, r[0]["code"])


if __name__ == '__main__':
    unittest.main()
