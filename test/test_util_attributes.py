# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import unittest

from taskgraph.util.attributes import (
    attrmatch,
    match_run_on_git_branches,
    match_run_on_projects,
)


class Attrmatch(unittest.TestCase):
    def test_trivial_match(self):
        """Given no conditions, anything matches"""
        self.assertTrue(attrmatch({}))

    def test_missing_attribute(self):
        """If a filtering attribute is not present, no match"""
        self.assertFalse(attrmatch({}, someattr=10))

    def test_literal_attribute(self):
        """Literal attributes must match exactly"""
        self.assertTrue(attrmatch({"att": 10}, att=10))
        self.assertFalse(attrmatch({"att": 10}, att=20))

    def test_set_attribute(self):
        """Set attributes require set membership"""
        self.assertTrue(attrmatch({"att": 10}, att={9, 10}))
        self.assertFalse(attrmatch({"att": 10}, att={19, 20}))

    def test_callable_attribute(self):
        """Callable attributes are called and any False causes the match to fail"""
        self.assertTrue(attrmatch({"att": 10}, att=lambda val: True))
        self.assertFalse(attrmatch({"att": 10}, att=lambda val: False))

        def even(val):
            return val % 2 == 0

        self.assertTrue(attrmatch({"att": 10}, att=even))
        self.assertFalse(attrmatch({"att": 11}, att=even))

    def test_all_matches_required(self):
        """If only one attribute does not match, the result is False"""
        self.assertFalse(attrmatch({"a": 1}, a=1, b=2, c=3))
        self.assertFalse(attrmatch({"a": 1, "b": 2}, a=1, b=2, c=3))
        self.assertTrue(attrmatch({"a": 1, "b": 2, "c": 3}, a=1, b=2, c=3))


class MatchRunOnProjects(unittest.TestCase):
    def test_empty(self):
        self.assertFalse(match_run_on_projects("try", []))

    def test_all(self):
        self.assertTrue(match_run_on_projects("try", ["all"]))
        self.assertTrue(match_run_on_projects("larch", ["all"]))
        self.assertTrue(match_run_on_projects("autoland", ["all"]))
        self.assertTrue(match_run_on_projects("mozilla-inbound", ["all"]))
        self.assertTrue(match_run_on_projects("mozilla-central", ["all"]))
        self.assertTrue(match_run_on_projects("mozilla-beta", ["all"]))
        self.assertTrue(match_run_on_projects("mozilla-release", ["all"]))


class MatchRunOnGitBranches(unittest.TestCase):
    def test_empty(self):
        self.assertFalse(match_run_on_git_branches("master", []))

    def test_all(self):
        self.assertTrue(match_run_on_git_branches("master", ["all"]))
        self.assertTrue(match_run_on_git_branches("release/v1.0", ["all"]))
        self.assertTrue(match_run_on_git_branches("release_v2.0", ["all"]))
        self.assertTrue(match_run_on_git_branches("arbitrary-branch", ["all"]))

    def test_regex(self):
        self.assertTrue(match_run_on_git_branches("master", ["master"]))
        self.assertFalse(match_run_on_git_branches("master", ["main"]))
        self.assertTrue(match_run_on_git_branches("main", ["main"]))
        self.assertFalse(match_run_on_git_branches("master", ["main"]))
        self.assertFalse(match_run_on_git_branches("master", ["^release/.+$"]))
        self.assertTrue(match_run_on_git_branches("release/v1.0", ["^release/.+$"]))
        self.assertFalse(match_run_on_git_branches("release_v2.0", ["^release/.+$"]))
        self.assertFalse(match_run_on_git_branches("release_v2.0", ["^release/.+$"]))
