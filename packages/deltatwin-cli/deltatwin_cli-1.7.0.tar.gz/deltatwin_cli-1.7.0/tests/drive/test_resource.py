import json
import os
import unittest
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import requests
from click.testing import CliRunner

from delta.cli import delta_cli
from delta.cli.utils import API
from tests.utils import remove_conf


class TestDriveResource(unittest.TestCase):
    service_url = 'https://delta_api'
    resource_dir = os.path.join(
        os.path.dirname(__file__), "../resources/drive"
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()
        remove_conf()

    @classmethod
    def tearDownClass(cls) -> None:
        remove_conf()

    @patch.object(API, "create_resource")
    def test_add_resource(self, mock_api: MagicMock):
        path = "path/to/resource/resource.txt"
        filename = "my_resource"
        description = "Awesome description"
        topic_a = "topics_a"
        topic_b = "topics_b"
        visibility = "public"
        false_visibility = "publique"
        result = self.runner.invoke(
            delta_cli,
            [
                "drive",
                "resource",
                "add",
                path,
                filename,
                '-d', 'desc',
                '-t', 'topic'
            ],
        )
        self.assertEqual(result.exit_code, 0)
        mock_api.assert_called_once_with(
            None, path, filename, 'desc', 'private', 'topic'
        )
        mock_api.reset_mock()
        result = self.runner.invoke(
            delta_cli,
            [
                "drive",
                "resource",
                "add",
                path,
                filename,
                "-v",
                visibility,
                "-d",
                description,
                "-t",
                topic_a,
                "-t",
                topic_b,
            ],
        )
        self.assertEqual(result.exit_code, 0)
        mock_api.assert_called_once_with(
            None,
            path,
            filename,
            description,
            visibility,
            f"{topic_a},{topic_b}",
        )
        mock_api.reset_mock()
        result = self.runner.invoke(
            delta_cli,
            [
                "drive",
                "resource",
                "add",
                "-v",
                false_visibility,
                path,
                filename,
            ],
        )
        self.assertEqual(result.exit_code, 2)  # Click usage error return code
        mock_api.assert_not_called()

    @patch.object(API, "download_resource")
    @patch.object(API, "get_resource")
    def test_get_resource_without_download(
            self, mock_get_resource: MagicMock,
            mock_download_resource: MagicMock
    ):
        filename = "my_resource.txt"
        resource_id = "my_resource_id"
        resource = {
            "resource_id": resource_id,
            "name": filename,
            "size": "42",
            "visibility": "private",
            "description": "",
            "owner": "",
            "topics": [
                "test"

            ]
        }
        mock_get_resource.return_value = resource
        result = self.runner.invoke(
            delta_cli,
            ["drive", "resource", "get", resource_id, "-f", "json"],
        )
        self.assertEqual(result.exit_code, 0)
        mock_download_resource.assert_not_called()
        mock_get_resource.assert_called_once_with(None, resource_id)
        with open(os.path.join(self.resource_dir, "get_result.json")) as f:
            data = json.load(f)
        self.assertEqual(data, json.loads(result.output))

    @patch.object(API, "download_resource")
    @patch.object(API, "get_resource")
    def test_get_resource_with_download(
            self, mock_get_resource: AsyncMock,
            mock_download_resource: AsyncMock
    ):
        def mock_response():
            r = requests.Response()
            r.status_code = 200
            r.headers["Content-Disposition"] = (
                'attachment; filename="my_resource.txt"'
            )

            r.raw = BytesIO(b"my content")
            return r

        filename = "my_resource.txt"
        resource_id = "my_resource_id"
        mock_download_resource.return_value = mock_response()
        result = self.runner.invoke(
            delta_cli,
            ["drive", "resource", "download", resource_id],
        )
        self.assertEqual(result.exit_code, 0)
        mock_get_resource.assert_not_called()
        mock_download_resource.assert_called_once_with(None, resource_id)
        self.assertIn(
            f'Resource "{resource_id}" successfully downloaded in',
            result.output,
        )
        os.remove(filename)

    @patch.object(API, "list_resource")
    def test_list_resources(self, mock_list_resource: MagicMock):
        with open(os.path.join(self.resource_dir, "list_result.json")) as f:
            all_resources = json.load(f)
        with open(
                os.path.join(self.resource_dir, "list_private_result.json")
        ) as f:
            private_resources = json.load(f)
        with open(
                os.path.join(self.resource_dir, "list_public_result.json")
        ) as f:
            public_resources = json.load(f)

        def side_effect(*args):
            match args[1]:
                case "private":
                    return private_resources
                case "public":
                    return public_resources

        mock_list_resource.side_effect = side_effect
        result = self.runner.invoke(
            delta_cli,
            ["drive", "resource", "list", "-f", "json"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(all_resources, json.loads(result.output))

        result = self.runner.invoke(
            delta_cli,
            ["drive", "resource", "list", "-v", "public", "-f", "json"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(public_resources, json.loads(result.output))

        result = self.runner.invoke(
            delta_cli,
            ["drive", "resource", "list", "-v", "private", "-f", "json"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(private_resources, json.loads(result.output))
