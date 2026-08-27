import unittest
import check


class TestColour(unittest.TestCase):
    def test_finds_hex_literals(self):
        self.assertEqual(check.colour_literals("a{color:#FEFEFE}"), ["#FEFEFE"])

    def test_tinted_grey_is_a_violation(self):
        self.assertEqual(check.bad_greys("--x:#EDEDEE;"), ["#EDEDEE"])

    def test_true_grey_passes(self):
        self.assertEqual(check.bad_greys("--x:#EDEDED;--y:#0D0D0D;"), [])

    def test_short_hex_is_expanded(self):
        self.assertEqual(check.bad_greys("--x:#ccc;"), [])
        self.assertEqual(check.bad_greys("--x:#cc0;"), ["#cc0"])

    def test_tinted_rgb_function_is_a_violation(self):
        self.assertEqual(check.bad_greys("color:rgb(13,13,20)"), ["rgb(13,13,20)"])


class TestRadius(unittest.TestCase):
    def test_pill_is_a_violation(self):
        self.assertEqual(check.bad_radii("a{border-radius:999px}"), ["999px"])

    def test_allowed_radii_pass(self):
        self.assertEqual(check.bad_radii("a{border-radius:11px}b{border-radius:5px}"), [])

    def test_percent_allowed_only_on_circle(self):
        self.assertEqual(check.bad_radii(".circle{border-radius:50%}"), [])
        self.assertEqual(check.bad_radii(".card{border-radius:50%}"), ["50%"])


class TestHosts(unittest.TestCase):
    def test_third_party_host_is_a_violation(self):
        self.assertEqual(
            check.foreign_hosts('<link href="https://fonts.googleapis.com/x">'),
            ["https://fonts.googleapis.com/x"],
        )

    def test_github_hosts_pass(self):
        self.assertEqual(check.foreign_hosts('a href="https://github.com/x/y"'), [])
        self.assertEqual(check.foreign_hosts('fetch("https://api.github.com/z")'), [])


class TestLangParity(unittest.TestCase):
    def test_missing_pair_is_a_violation(self):
        html = '<p data-lang="en" data-key="k1">A</p>'
        self.assertEqual(check.lang_parity(html), ["k1: en without ru"])

    def test_matched_pair_passes(self):
        html = '<p data-lang="en" data-key="k1">A</p><p data-lang="ru" data-key="k1">Б</p>'
        self.assertEqual(check.lang_parity(html), [])


if __name__ == "__main__":
    unittest.main()
