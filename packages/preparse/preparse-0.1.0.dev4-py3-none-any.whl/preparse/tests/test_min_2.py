import unittest

from preparse.core import Group, Order, PreParser


class TestPermuteAndPosixParsing(unittest.TestCase):

    def parse(self, *, optdict, query, order):
        p = PreParser(order=order, group=Group.MINIMIZE, optdict=optdict)
        ans = p.parse_args(query)
        self.assertEqual(list(ans), list(p.parse_args(ans)))
        return ans

    # --- PERMUTE ---

    def test_permute_all_positionals_moved(self):
        optdict = {"-a": 0, "-b": 1}
        query = ["input.txt", "-a", "-bvalue", "config.json"]
        solution = ["-a", "-bvalue", "input.txt", "config.json"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_permute_with_mixed_options(self):
        optdict = {"-x": 0, "-y": 2, "-z": 0}
        query = ["-x", "file1", "-yextra", "file2", "-z"]
        solution = ["-x", "-yextra", "-z", "file1", "file2"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_permute_grouped_flags_and_positionals(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0}
        query = ["data.csv", "-abc"]
        solution = ["-a", "-b", "-c", "data.csv"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_permute_with_double_dash(self):
        optdict = {"-v": 0, "-o": 1}
        query = ["-v", "file1", "--", "-oout.txt"]
        solution = ["-v", "--", "file1", "-oout.txt"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    # --- POSIX ---

    def test_posix_stops_at_first_positional(self):
        optdict = {"-x": 0, "-y": 0}
        query = ["-x", "main.py", "-y"]
        solution = ["-x", "main.py", "-y"]
        answer = self.parse(optdict=optdict, query=query, order=Order.POSIX)
        self.assertEqual(solution, answer)

    def test_posix_multiple_positionals(self):
        optdict = {"-a": 0, "-b": 1}
        query = ["-a", "input.txt", "-bval", "config.yaml"]
        solution = ["-a", "input.txt", "-bval", "config.yaml"]
        answer = self.parse(optdict=optdict, query=query, order=Order.POSIX)
        self.assertEqual(solution, answer)

    def test_posix_double_dash_preserves_options_after(self):
        optdict = {"-v": 0, "-d": 1}
        query = ["file.txt", "--", "-v", "-dlog.txt"]
        solution = ["file.txt", "--", "-v", "-dlog.txt"]
        answer = self.parse(optdict=optdict, query=query, order=Order.POSIX)
        self.assertEqual(solution, answer)

    def test_posix_with_grouped_options_then_positionals(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0}
        query = ["-abc", "file.txt", "-d"]
        solution = ["-a", "-b", "-c", "file.txt", "-d"]
        answer = self.parse(optdict=optdict, query=query, order=Order.POSIX)
        self.assertEqual(solution, answer)

    def test_posix_optional_arg_ignored_after_positional(self):
        optdict = {"-o": 2, "-v": 0}
        query = ["-o", "input.txt", "file.txt", "-v"]
        solution = ["-o", "input.txt", "file.txt", "-v"]
        answer = self.parse(optdict=optdict, query=query, order=Order.POSIX)
        self.assertEqual(solution, answer)


if __name__ == "__main__":
    unittest.main()
