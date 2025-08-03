import math
import unittest

import click
from click.testing import CliRunner

from preparse.core import *


class expit:

    def function(x: float):
        try:
            p = math.exp(-x)
        except OverflowError:
            p = float("+inf")
        return 1 / (1 + p)

    @PreParser(order=Order.PERMUTE).click()
    @click.command(add_help_option=False)
    @click.help_option("-h", "--help")
    @click.version_option("1.2.3", "-V", "--version")
    @click.argument("x", type=float)
    def main(x: float):
        """applies the expit function to x"""
        click.echo(expit.function(x))


class TestPreparse(unittest.TestCase):

    def test_runner(self):
        runner = CliRunner()
        result = runner.invoke(expit.main, ["0"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "0.5\n")
        runner = CliRunner()
        result = runner.invoke(expit.main, ["1"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "0.7310585786300049\n")
        runner = CliRunner()
        result = runner.invoke(expit.main, ["--", "-1"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "0.2689414213699951\n")
        runner = CliRunner()
        result = runner.invoke(expit.main, ["-1"])
        self.assertEqual(result.exit_code, 2)


class TestMainFunction(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_main_function_valid_input(self):
        result = self.runner.invoke(expit.main, ["0.5"])
        self.assertEqual(result.exit_code, 0)
        self.assertAlmostEqual(float(result.output.strip()), expit.function(0.5))

    def test_main_function_help_option(self):
        result = self.runner.invoke(expit.main, ["-h"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("applies the expit function to x", result.output)

    def test_main_function_version_option(self):
        result = self.runner.invoke(expit.main, ["-V"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("1.2.3", result.output)

    def test_main_function_invalid_argument(self):
        result = self.runner.invoke(expit.main, ["invalid"])
        self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
