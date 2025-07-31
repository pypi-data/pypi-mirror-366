import json
import os
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from delta.cli import delta_cli
from delta.cli.utils import API
from tests.utils import remove_conf


class TestDelete(unittest.TestCase):
    service_url = 'https://delta_api'
    runner = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()
        remove_conf()

    @classmethod
    def tearDownClass(cls) -> None:
        remove_conf()

    def test_without_conf(self):
        result = self.runner.invoke(
            delta_cli,
            ["schedule", "delete",
             'toto', "-c", "conf.ini", '-y'],
            catch_exceptions=False
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "No config find please use deltatwin "
            "login before using this command",
            result.output)

    def test_delete_json(self):
        with patch.object(API, 'delete_scheduled_run',
                          return_value=None
                          ):
            result = self.runner.invoke(
                delta_cli,
                ["schedule", "delete", "-c",
                 "conf.ini", 'toto', '-y'],
                catch_exceptions=False
            )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual('', result.output)
