"""Ignored tests in targets no daily shard builds must have a policy row."""
import unittest

from tools.ci import check_ignored_test_rows as rows


class RowlessTargetTests(unittest.TestCase):
    def test_an_example_or_bench_test_is_not_excused_by_its_packages_shard(self):
        functions = [
            ('crates/horizon-client/examples/e.rs', 3, 'boots_game', frozenset({'horizon-client'}), 'example', False),
            ('crates/horizon-client/benches/b.rs', 3, 'boots_bench', frozenset({'horizon-client'}), 'bench', False),
            ('crates/horizon-client/tests/t.rs', 3, 'covered', frozenset({'horizon-client'}), 'test', False),
            ('crates/horizon-client/src/lib.rs', 3, 'lib_covered', frozenset({'horizon-client'}), 'lib', False),
        ]
        problems = rows.rowless_problems([], functions)
        self.assertEqual(len(problems), 2, problems)
        self.assertTrue(all('boots_' in problem for problem in problems), problems)
        self.assertFalse(any('covered' in problem for problem in problems), problems)
