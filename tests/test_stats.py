# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# Unit test file
# tests/test_stats.py

# Importacion de librerias necesarias
import unittest
from unittest import mock
import logging
from http import HTTPStatus

# Importacion del archivo principal
import app_server
from tests import aux_functions


class StatsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = app_server.app
        app.logger.setLevel(logging.ERROR)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        print("Starting testing path \"/stats\" of the app server...")

    @classmethod
    def tearDownClass(cls):
        print("Finished testing path \"/stats\" of the app server!")

    def test_private_endpoints_no_api_key_should_return_unauthorized(self):
        res = self.app.get('/api/v1/stats')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_stats_should_return_ok(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/stats',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_stats_sort_should_return_ok(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/stats?sort_ascending=true',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)


if __name__ == '__main__':
    unittest.main()
