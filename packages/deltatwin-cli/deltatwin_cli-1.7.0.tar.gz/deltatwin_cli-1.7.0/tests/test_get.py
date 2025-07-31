import json
import os
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from delta.cli import delta_cli
from delta.cli.utils import API
from tests.utils import remove_conf


class TestGet(unittest.TestCase):
    service_url = 'https://delta_api'
    resource_dir = os.path.join(os.path.dirname(__file__), 'resources', 'get')
    runner = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()
        remove_conf()

    @classmethod
    def tearDownClass(cls) -> None:
        remove_conf()

    def test_get_without_conf(self):
        result = self.runner.invoke(
            delta_cli,
            ["component", "get", 'Toto', "-c", "conf.ini"],
            catch_exceptions=False
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "No config find please use deltatwin login "
            "before using this command",
            result.output)

    def test_get(self):
        with open(os.path.join(self.resource_dir, 'get.json')) as f:
            data = json.load(f)

        with open(os.path.join(self.resource_dir, 'version.json')) as f:
            version = json.load(f)

        with patch.object(API, 'get_dt_version',
                          return_value=version
                          ):
            with patch.object(API, 'get_dt',
                              return_value=data
                              ):
                with patch.object(API, 'get_dt_manifest',
                                  return_value=data
                                  ):
                    result = self.runner.invoke(
                        delta_cli,
                        ["component", "get", "Toto", "-c", "conf.ini"],
                        catch_exceptions=False
                    )

        self.assertEqual(result.exit_code, 0)

    def test_get_json(self):
        with open(os.path.join(self.resource_dir, 'get.json')) as f:
            data = json.load(f)

        with open(os.path.join(self.resource_dir, 'version.json')) as f:
            version = json.load(f)

        with patch.object(API, 'get_dt_version',
                          return_value=version
                          ):
            with patch.object(API, 'get_dt',
                              return_value=data
                              ):
                result = self.runner.invoke(
                    delta_cli,
                    ["component", "get", "deltatwin1", "-f", "json",
                     "-c", "conf.ini"],
                    catch_exceptions=False
                )
        with open(os.path.join(self.resource_dir, 'get_resp.json')) as f:
            data = json.loads(f.read())
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(data, json.loads(result.output))

    def test_get_malformed_response(self):
        with open(os.path.join(self.resource_dir, 'wrong_get.json')) as f:
            data = json.load(f)

        with open(os.path.join(self.resource_dir, 'version.json')) as f:
            version = json.load(f)

        with patch.object(API, 'get_dt_version',
                          return_value=version
                          ):
            with patch.object(API, 'get_dt',
                              return_value=data
                              ):
                result = self.runner.invoke(
                    delta_cli,
                    ["component", "get", "Toto", "-c", "conf.ini"],
                    catch_exceptions=False
                )

        self.assertEqual(result.exit_code, 1)
        self.assertIn(
            'ERROR: The response does not respect the DeltaTwin format.',
            result.output
        )
