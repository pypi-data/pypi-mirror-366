import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch

import requests
from click.testing import CliRunner
from requests.models import Response, Request

from delta.cli import delta_cli
from delta.cli.utils import API
from tests.utils import remove_conf


class TestLogin(unittest.TestCase):
    service_url = 'https://delta_api'
    resource_dir = os.path.join(os.path.dirname(__file__),
                                'resources', 'login')

    runner = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()
        remove_conf()

    @classmethod
    def tearDownClass(cls) -> None:
        remove_conf()

    def test_login_no_api(self):
        result = self.runner.invoke(
            delta_cli,
            ["login", "-c", "conf.ini"],
            catch_exceptions=True)

        self.assertEqual(result.exit_code, 2)
        remove_conf()

    def test_login_ok(self):
        with open(os.path.join(self.resource_dir, 'login_resp.json')) as f:
            data = json.load(f)

        with patch.object(API, 'log_to_api',
                          return_value=data
                          ):
            result = self.runner.invoke(
                delta_cli,
                ["login",
                 "-c", "conf.ini",
                 "toto",
                 "tata",
                 '-a', self.service_url],
                catch_exceptions=False
            )
        self.assertEqual(result.exit_code, 0)

        remove_conf()

    def test_unauthorized_login(self):
        unauthoried_response = Response()
        unauthoried_response.status_code = 404
        unauthoried_response.reason = 'Unauthorized'
        unauthoried_response.raw = BytesIO(b"{\"error\": \"error\"}")
        unauthoried_response.request = Request('POST', self.service_url)

        with patch.object(requests, 'post',
                          return_value=unauthoried_response
                          ):
            result = self.runner.invoke(
                delta_cli,
                ["login",
                 "-c", "conf.ini",
                 "wrong",
                 "wrong",
                 '-a', self.service_url],
                catch_exceptions=False
            )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: Unauthorized at https://delta_api",
                      result.output)
        remove_conf()

    def test_connection_error_login(self):
        result = self.runner.invoke(
            delta_cli,
            ["login",
             "-c", "conf.ini",
             "wrong",
             "wrong",
             '-a', "http://my_api.com"],
            catch_exceptions=False
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: Connection error "
                      "to the service http://my_api.com",
                      result.output)

        remove_conf()
