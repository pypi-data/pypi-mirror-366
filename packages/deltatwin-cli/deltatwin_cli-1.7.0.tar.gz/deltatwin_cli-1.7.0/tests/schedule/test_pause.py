import json
import os
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from delta.cli import delta_cli
from delta.cli.utils import API
from tests.utils import remove_conf


class TestPause(unittest.TestCase):
    service_url = 'https://delta_api'
    resource_dir = os.path.join(os.path.dirname(__file__),
                                '../resources', 'schedule')
    runner = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()
        remove_conf()

    @classmethod
    def tearDownClass(cls) -> None:
        remove_conf()

    def test_pause_without_conf(self):
        result = self.runner.invoke(
            delta_cli,
            ["schedule", "pause", 'toto',
             "-c", "conf.ini"],
            catch_exceptions=False
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "No config find please use deltatwin "
            "login before using this command",
            result.output)

    def test_pause(self):
        with open(os.path.join(self.resource_dir, 'pause.json')) as f:
            data = json.load(f)

        with patch.object(API, 'pause_scheduled_run',
                          return_value=data
                          ):
            result = self.runner.invoke(
                delta_cli,
                ["schedule", "pause", 'toto',
                 "-c", "conf.ini"],
                catch_exceptions=False
            )
        self.assertEqual(result.exit_code, 0)

    def test_pause_json(self):
        with open(os.path.join(self.resource_dir, 'pause.json')) as f:
            data = json.load(f)

        with patch.object(API, 'pause_scheduled_run',
                          return_value=data
                          ):
            result = self.runner.invoke(
                delta_cli,
                ["schedule", "pause", 'toto',
                 "-c", "conf.ini", "-f", "json"],
                catch_exceptions=False
            )

        with open(os.path.join(self.resource_dir, 'pause.json')) as f:
            data = json.loads(f.read())

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(data, json.loads(result.output))
