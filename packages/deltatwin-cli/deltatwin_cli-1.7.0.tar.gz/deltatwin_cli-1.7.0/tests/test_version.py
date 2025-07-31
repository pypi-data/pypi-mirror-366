import unittest

from delta.cli import delta_cli
from delta.cli._version import __version__
from click.testing import CliRunner


class TestDeltaVersion(unittest.TestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(delta_cli, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            f"INFO: DeltaTwin® CLI version : {__version__}\n",
            result.output)
