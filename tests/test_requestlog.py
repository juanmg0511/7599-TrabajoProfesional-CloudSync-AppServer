# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# Unit test file
# tests/test_requestlog.py

# Basado en:
# https://dev.classmethod.jp/articles/mocking-around-with-python-and-unittest/

# Importacion de librerias necesarias
import unittest
from unittest import TestCase
from unittest import mock
import logging
from http import HTTPStatus
from datetime import datetime

# Importacion del archivo principal
import app_server
from tests import aux_functions


class RequestLogTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        app = app_server.app
        app.logger.setLevel(logging.ERROR)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        print("Starting testing path \"/requestlog\" of the app server...")
        # Generamos un par de requests a la api para generar estadisticas
        aux_functions.createRequestLogEntry("/api/v1/gameprogress",
                                            "testunituser")
        aux_functions.createRequestLogEntry("/api/v1/gameprogress",
                                            "testunituser")

    @classmethod
    def tearDownClass(cls):
        print("Finished testing path \"/requestlog\" of the app server!")

    @mock.patch("src.authserver_client.requests.get")
    def test_private_endpoints_no_token_should_return_unauth(self,
                                                             mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        res = self.app.get('/api/v1/requestlog?' +
                           'startdate=2022-05-01&enddate=2010-05-01')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_ok(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        today = str(datetime.utcnow().date())
        r = self.app.get('/api/v1/requestlog?startdate=' + today +
                         '&enddate=' + today,
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_ok_sort(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        today = str(datetime.utcnow().date())
        r = self.app.get('/api/v1/requestlog?startdate=' + today +
                         '&enddate=' + today + '&sortascending=True',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_ok_filter_in(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        today = str(datetime.utcnow().date())
        r = self.app.get('/api/v1/requestlog?startdate=' + today +
                         '&enddate=' + today +
                         '&filter={"comparator":"in","field":"status",' +
                         '"value":"200"}',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_bad_request_filter(self,
                                                         mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        today = str(datetime.utcnow().date())
        r = self.app.get('/api/v1/requestlog?startdate=' + today +
                         '&enddate=' + today +
                         '&filter={"c":"in","f":"status",' +
                         '"v":"200"}',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_ok_filter_eq(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        today = str(datetime.utcnow().date())
        r = self.app.get('/api/v1/requestlog?startdate=' + today +
                         '&enddate=' + today +
                         '&filter={"comparator":"eq","field":"status",' +
                         '"value":"200"}',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_bad_request(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/requestlog?' +
                         'startdate=invaliddate&enddate=2022-05-01',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-1, r.json['code'])

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_bad_request_2(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/requestlog?' +
                         'startdate=2022-05-01&enddate=2010-05-01',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-2, r.json['code'])

    @mock.patch("src.authserver_client.requests.get")
    def test_requestlog_should_return_bad_request_3(self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/requestlog?' +
                         'startdate=2022-05-01&enddate=2010-05-01&' +
                         'filter={"invalid_filter"}',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-2, r.json['code'])


if __name__ == '__main__':
    unittest.main()
