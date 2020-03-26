#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import unittest

target = __import__("dco-org-check")
Config = target.Config
Commit = target.Commit
DCOOutput = target.DCOOutput
Repo = target.Repo

class TestCommit(unittest.TestCase):

    # test for not having a signoff
    def testHasNoSignOff(self):
        commit = Commit()
        commit.commit_message = "has no signoff"
        self.assertFalse(commit.hasSignOff(), "Commit message didn't have a signoff")

    # test for having a signoff
    def testHasSignOff(self):
        commit = Commit()
        commit.commit_message = "has a signoff  Signed-off-by: John Mertic <jmertic@linuxfoundation.org>"
        self.assertTrue(commit.hasSignOff(), "Commit message had a signoff")

    def testFoundPastSignoff(self):
        commit = Commit()
        commit.html_url = 'https://github.com/testorg/testrepo/commit/11ac960e1070eacc2fe92ac9a3d1753400e1fd4b'

        signoffs = [
            ['dco-signoffs',"I, personname hereby sign-off-by all of my past commits to this repo subject to the Developer Certificate of Origin (DCO), Version 1.1. In the past I have used emails: [personname@domain.com]\n\n11ac960e1070eacc2fe92ac9a3d1753400e1fd4b This is a commit".encode() ]
        ]

        self.assertTrue(commit.hasPastSignoff(signoffs), "Commit message had a past signoff")

    def testFoundNoPastSignoff(self):
        commit = Commit()
        commit.html_url = 'https://github.com/testorg/testrepo/commit/c1d322dfba0ed7a770d74074990ac51a9efedcd0'

        signoffs = [
            ['dco-signoffs',"I, personname hereby sign-off-by all of my past commits to this repo subject to the Developer Certificate of Origin (DCO), Version 1.1. In the past I have used emails: [personname@domain.com]\n\n11ac960e1070eacc2fe92ac9a3d1753400e1fd4b This is a commit".encode() ]
        ]

        self.assertFalse(commit.hasPastSignoff(signoffs), "Commit message had a past signoff")

if __name__ == '__main__':
    unittest.main()
