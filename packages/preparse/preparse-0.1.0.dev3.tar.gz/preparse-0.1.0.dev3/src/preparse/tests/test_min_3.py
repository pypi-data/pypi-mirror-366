import unittest

from preparse.core import Group, Order, PreParser


class TestMixedArgScenarios(unittest.TestCase):

    def parse(self, *, optdict, query, order):
        p = PreParser(order=order, group=Group.MINIMIZE, optdict=optdict)
        ans = p.parse_args(query)
        self.assertEqual(list(ans), list(p.parse_args(ans)))
        return ans

    def test_mix_positional_long_short_optional_args_permute(self):
        optdict = {"-a": 0, "-b": 1, "-c": 2, "--log": 1, "--debug": 0, "--config": 2}
        query = ["input.txt", "--log=logfile", "-acextra", "--debug", "file.csv"]
        solution = [
            "--log=logfile",
            "-a",
            "-cextra",
            "--debug",
            "input.txt",
            "file.csv",
        ]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_mix_positional_long_short_optional_args_posix(self):
        optdict = {"-a": 0, "-b": 1, "-c": 2, "--log": 1, "--debug": 0, "--config": 2}
        query = [
            "--debug",
            "-acextra",
            "--log=logfile",
            "input.txt",
            "--config",
            "settings",
        ]
        solution = [
            "--debug",
            "-a",
            "-cextra",
            "--log=logfile",
            "input.txt",
            "--config",
            "settings",
        ]
        answer = self.parse(optdict=optdict, query=query, order=Order.POSIX)
        self.assertEqual(solution, answer)

    def test_optional_and_required_arg_mixed(self):
        optdict = {"-x": 2, "-y": 1, "--mode": 2, "--file": 1}
        query = ["-xyval", "--mode=fast", "--file", "out.txt", "input.dat"]
        solution = ["-xyval", "--mode=fast", "--file", "out.txt", "input.dat"]
        answer = self.parse(optdict=optdict, query=query, order=Order.GIVEN)
        self.assertEqual(solution, answer)

    def test_long_equals_and_space_combination(self):
        optdict = {"--alpha": 1, "--beta": 1, "-a": 0, "-b": 1}
        query = ["--alpha=one", "--beta", "two", "-a", "-bthree", "final"]
        solution = ["--alpha=one", "--beta", "two", "-a", "-bthree", "final"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_mix_grouped_and_non_grouped(self):
        optdict = {"-a": 0, "-b": 0, "-c": 1, "--set": 2}
        query = ["-abcval", "--set", "x", "y", "arg1"]
        solution = ["-a", "-b", "-cval", "--set", "x", "y", "arg1"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)


if __name__ == "__main__":
    unittest.main()
