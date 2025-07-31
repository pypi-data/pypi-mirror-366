import json
import os
import unittest
from unittest import mock

from click import UsageError

from delta.cli.components.publish import prepare_publish


class TestDrivePublish(unittest.TestCase):
    service_url = 'https://delta_api'
    resource_dir = os.path.join(os.path.dirname(__file__), '../resources')
    conf = {}

    @classmethod
    def setUpClass(cls) -> None:
        with open(os.path.join(cls.resource_dir,
                               'drive/manifest_example.json')) as exp:
            with open('manifest.json', 'w') as f:
                json.dump(json.loads(exp.read()), f)
        with open('workflow.yml', 'w'):
            pass

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists("manifest.json"):
            os.remove("manifest.json")
        if os.path.exists("workflow.yml"):
            os.remove("workflow.yml")

    @mock.patch("delta.cli.components.publish.prepare_publish_to_harbor")
    @mock.patch("delta.cli.utils.API.check_dt_exists")
    def test_prepare_publish_version(self, mock_harbor, mock_api):
        version = ''
        visibility = ''
        topic = ''
        change_log = ''
        manifest = ''
        path_delta_twin = ''
        mock_harbor.return_value = None
        mock_api.return_value = False
        no_cache = False

        with self.assertRaises(UsageError):
            prepare_publish(
                self.conf, version, visibility,
                topic, change_log, manifest, path_delta_twin, no_cache
            )

        version = "1.0.0"

        data_version = prepare_publish(
            self.conf,
            version,
            visibility,
            topic,
            change_log,
            manifest,
            path_delta_twin,
            no_cache)['version']

        self.assertEqual(version, data_version)

        version = "1.0.0.dev2"

        data_version = prepare_publish(
            self.conf,
            version,
            visibility,
            topic,
            change_log,
            manifest, path_delta_twin, no_cache)['version']

        self.assertEqual(version, data_version)
