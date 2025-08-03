import unittest

from preparse.core import Group, Order, PreParser


class TestMinimizeGroupParsing(unittest.TestCase):

    def parse(self, *, optdict, query):
        p = PreParser(order=Order.GIVEN, group=Group.MINIMIZE, optdict=optdict)
        ans = p.parse_args(query)
        self.assertEqual(list(ans), list(p.parse_args(ans)))  # round-trip check
        return ans

    def test_simple_grouped_flags(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0}
        query = ["-abc"]
        solution = ["-a", "-b", "-c"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouped_with_argument_at_end(self):
        optdict = {"-a": 0, "-b": 0, "-c": 1}
        query = ["-abcvalue"]
        solution = ["-a", "-b", "-cvalue"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouped_with_argument_middle(self):
        optdict = {"-a": 0, "-b": 1, "-c": 0}
        query = ["-abvaluec"]
        solution = ["-a", "-bvaluec"]  # because -b consumes "valuec"
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_multiple_grouped_chunks(self):
        optdict = {"-x": 0, "-y": 0, "-z": 1}
        query = ["-xy", "-zabc"]
        solution = ["-x", "-y", "-zabc"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouped_with_nonexistent_flag(self):
        optdict = {"-a": 0, "-b": 0}
        query = ["-abc"]
        # assume unknown option "-c" is preserved as-is
        solution = ["-a", "-b", "-c"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouped_with_equals_sign(self):
        optdict = {"-a": 0, "-b": 0, "-c": 1}
        query = ["-abc=foo"]
        solution = ["-a", "-b", "-c=foo"]  # assuming `=foo` binds to last opt
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_mixed_with_normal_args(self):
        optdict = {"-v": 0, "-f": 1, "-o": 2}
        query = ["-v", "-fooutput.txt", "log.txt", "--", "file1"]
        solution = ["-v", "-fooutput.txt", "log.txt", "--", "file1"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_double_dash_preserved(self):
        optdict = {"-a": 0, "-b": 0}
        query = ["-ab", "--", "-c"]
        solution = ["-a", "-b", "--", "-c"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_repeated_grouped_options(self):
        optdict = {"-x": 0, "-y": 0}
        query = ["-xy", "-yx"]
        solution = ["-x", "-y", "-y", "-x"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)


if __name__ == "__main__":
    unittest.main()
