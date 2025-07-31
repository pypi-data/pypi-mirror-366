import configparser
import json
import os
import unittest

import click

from delta.cli.utils import Utils


class TestDeltaUtils(unittest.TestCase):

    def test_retrieve_conf(self):
        self.assertEqual(Utils.retrieve_conf(None),
                         os.path.expanduser('~') + '/.deltatwin/conf.ini')
        self.assertEqual(Utils.retrieve_conf('conf.ini'), 'conf.ini')

    def test_retrieve_token(self):
        with self.assertRaises(click.exceptions.UsageError) as cm:
            Utils.retrieve_token("conf.ini")

        self.assertEqual(cm.exception.exit_code, 2)

        self.assertEqual({}, dict(Utils.read_config('conf.ini')['DEFAULT']))
        Utils.save_config('conf.ini', 'DEFAULT', {})

        with self.assertRaises(click.exceptions.UsageError) as cm:
            Utils.retrieve_token("conf.ini")

        self.assertEqual(cm.exception.exit_code, 2)

        self.assertEqual({}, dict(Utils.read_config('conf.ini')['DEFAULT']))
        Utils.save_config('conf.ini', 'SERVICES', {})

        with self.assertRaises(click.exceptions.UsageError) as cm:
            Utils.retrieve_token("conf.ini")

        self.assertEqual(cm.exception.exit_code, 2)

        data = {
            "token": "my_token"
        }
        Utils.save_config(path='conf.ini', context='SERVICES', config=data)

        self.assertEqual(
            'my_token',
            Utils.retrieve_token("conf.ini"))

        os.remove("conf.ini")

    def test_fasle_conftoken(self):
        with self.assertRaises(click.UsageError) as cm:
            Utils.retrieve_token("wrong")

        self.assertEqual(cm.exception.exit_code, 2)

    def test_output_json(self):
        data = "{}"
        self.assertTrue(Utils.output_as_json('json', data))
        self.assertTrue(Utils.output_as_json('JSON', data))
        self.assertTrue(Utils.output_as_json('Json', data))
        data = "www.my_delta_service.com/json"
        self.assertTrue(Utils.output_as_json('json', data))
        data = "{}"
        self.assertFalse(Utils.output_as_json('xml', data))
        data = "www.my_delta_service.com/json"
        self.assertFalse(Utils.output_as_json('yaml', data))
