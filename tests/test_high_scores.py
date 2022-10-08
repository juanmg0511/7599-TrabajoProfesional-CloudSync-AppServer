# CloudSync - App Server
# Flask + MongoDB - on Gunicorn
# Unit test file
# tests/test_high_scores.py

# Basado en:
# https://dev.classmethod.jp/articles/mocking-around-with-python-and-unittest/

# Importacion de librerias necesarias
import unittest
from unittest import TestCase
from unittest import mock
from http import HTTPStatus
import logging

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
        print("Starting testing path \"/highscores\" of the app server...")
        # Creamos los highscores a ser utilizados durante los tests
        aux_functions.createHighScore("testunituser_usr_get")
        aux_functions.createHighScore("testunituser_usr_put")
        aux_functions.createHighScore("testunituser_usr_del")
        aux_functions.createHighScore("testunituser_usr_existing_post")

    @classmethod
    def tearDownClass(cls):
        # Borramos los highscores generados para los tests
        aux_functions.deleteHighScores("testunituser_post_1")
        aux_functions.deleteHighScores("testunituser_id_get_1")
        aux_functions.deleteHighScores("testunituser_id_put_1")
        aux_functions.deleteHighScores("testunituser_id_put_2")
        aux_functions.deleteHighScores("testunituser_id_del_1")
        aux_functions.deleteHighScores("testunituser_usr_new")
        aux_functions.deleteHighScores("testunituser_usr_get")
        aux_functions.deleteHighScores("testunituser_usr_put")
        aux_functions.deleteHighScores("testunituser_usr_del")
        aux_functions.deleteHighScores("testunituser_usr_existing_post")
        print("Finished testing path \"/highscores\" of the app server!")

    def test_private_endpoints_no_token_should_return_unauthorized(self):
        res = self.app.get('/api/v1/highscores')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.post('/api/v1/highscores')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/highscores/id')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.put('/api/v1/highscores/id')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.delete('/api/v1/highscores/id')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.get('/api/v1/users/usr/highscores')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.post('/api/v1/users/usr/highscores')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)
        res = self.app.delete('/api/v1/users/usr/highscores')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, res.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_highscores_should_return_ok(self,
                                                 mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/highscores',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_highscores_paging_should_return_ok(self,
                                                        mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/highscores?start=1&limit=1',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_highscores_paging_inv_should_return_ok(self,
                                                            mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/highscores?start=-1&limit=-1',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_all_highscores_pag_inv_should_return_bad_req(
      self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/highscores?start=a&limit=b',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_post_valid_highscore_should_return_created(self,
                                                        mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.post('/api/v1/highscores',
                          headers={'Content-Type': 'application/json',
                                   'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            username="testunituser_post_1",
                            achieved_level=5,
                            difficulty_level=5,
                            time_elapsed="20:10:40.045",
                            gold_collected=5000,
                            high_score=1000000
                          ))
        self.assertEqual(HTTPStatus.CREATED, r.status_code)
        self.assertEqual("testunituser_post_1", r.json["username"])

    @mock.patch("src.authserver_client.requests.get")
    def test_existing_post_invalid_highscore_should_return_400(
      self, mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.post('/api/v1/highscores',
                          headers={'Content-Type': 'application/json',
                                   'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            gold_collected=5000
                          ))
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_get_id_highscores_should_return_ok(self,
                                                mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        testunituser_id = aux_functions.\
            createHighScore("testunituser_id_get_1")
        r = self.app.get('/api/v1/highscores/' + str(testunituser_id),
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_get_id_highscores_should_return_not_found(self,
                                                       mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/highscores/id_invalid',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.NOT_FOUND, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_put_valid_highscore_id_should_return_ok(self,
                                                     mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        testunituser_id = aux_functions.\
            createHighScore("testunituser_id_put_1")
        r = self.app.put('/api/v1/highscores/' + str(testunituser_id),
                         headers={'Content-Type': 'application/json',
                                  'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           username="testunituser",
                           achieved_level=5,
                           difficulty_level=5,
                           time_elapsed="20:10:40.045",
                           gold_collected=5000,
                           high_score=1000000
                         ))
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual("testunituser", r.json["username"])

    @mock.patch("src.authserver_client.requests.get")
    def test_put_highscore_invalid_id_should_return_404(self,
                                                        mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.put('/api/v1/highscores/invalid-id',
                         headers={'Content-Type': 'application/json',
                                  'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           username="testunituser",
                           achieved_level=5,
                           difficulty_level=5,
                           time_elapsed="20:10:40.045",
                           gold_collected=5000,
                           high_score=1000000
                         ))
        self.assertEqual(HTTPStatus.NOT_FOUND, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_put_invalid_highscore_id_should_return_bad_req(self,
                                                            mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        testunituser_id = aux_functions.\
            createHighScore("testunituser_id_put_2")
        r = self.app.put('/api/v1/highscores/' + str(testunituser_id),
                         headers={'Content-Type': 'application/json',
                                  'X-Auth-Token': 'AuthServer is mocked'},
                         json=dict(
                           difficulty_level=5
                         ))
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_delete_non_existin_id_should_return_not_found(self,
                                                           mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.delete('/api/v1/highscores/fake-id',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.NOT_FOUND, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_delete_existing_id_should_return_ok(self,
                                                 mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        testunituser_id = aux_functions.\
            createHighScore("testunituser_id_del_1")
        r = self.app.delete('/api/v1/highscores/' + str(testunituser_id),
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(0, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_get_usr_highscores_should_return_ok(self,
                                                 mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/users/testunituser_usr_get/highscores',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(True, len(r.json) > 0)

    @mock.patch("src.authserver_client.requests.get")
    def test_post_new_highscore_should_return_created(self,
                                                      mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.post('/api/v1/users/testunituser_usr_new/highscores',
                          headers={'Content-Type': 'application/json',
                                   'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            achieved_level=5,
                            difficulty_level=5,
                            time_elapsed="20:10:40.045",
                            gold_collected=5000,
                            high_score=1000000
                          ))
        self.assertEqual(HTTPStatus.CREATED, r.status_code)
        self.assertEqual("testunituser_usr_new", r.json["username"])

    @mock.patch("src.authserver_client.requests.get")
    def test_post_invalid_highscore_should_return_bad_req(self,
                                                          mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.post('/api/v1/users/testunituser_usr_put/highscores',
                          headers={'Content-Type': 'application/json',
                                   'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            difficulty_level=5
                          ))
        self.assertEqual(HTTPStatus.BAD_REQUEST, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_get_existing_user_should_return_ok(self,
                                                mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.get('/api/v1/users/testunituser_usr_get/highscores',
                         headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)

    @mock.patch("src.authserver_client.requests.get")
    def test_delete_non_existin_user_should_return_not_found(self,
                                                             mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.delete('/api/v1/users/testunituser_invalid/highscores',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.NOT_FOUND, r.status_code)
        self.assertEqual(-1, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_delete_existing_user_should_return_ok(self,
                                                   mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionAdmin(
                                            "testunituser_admin")

        r = self.app.delete('/api/v1/users/testunituser_usr_del/highscores',
                            headers={'X-Auth-Token': 'AuthServer is mocked'})
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(0, r.json["code"])

    @mock.patch("src.authserver_client.requests.get")
    def test_post_highscore_other_user_should_return_unauth(self,
                                                            mock_get_session):
        mock_get_session.return_value = aux_functions.\
                                        mockCheckSessionUser(
                                            "testunituser_other")

        r = self.app.post('/api/v1/users/testunituser/highscores',
                          headers={'Content-Type': 'application/json',
                                   'X-Auth-Token': 'AuthServer is mocked'},
                          json=dict(
                            next_level=5,
                            difficulty_level=5
                          ))
        self.assertEqual(HTTPStatus.UNAUTHORIZED, r.status_code)
        self.assertEqual(-1, r.json["code"])


if __name__ == '__main__':
    unittest.main()
