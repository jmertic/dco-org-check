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
getCommits = target.getCommits

class TestCommit(unittest.TestCase):

    # test for not having a signoff
    def testhasNoSignOff(self):
        commit = Commit()
        commit.commit_message = "has no signoff"
        self.assertFalse(commit.hasSignOff(), "Commit message didn't have a signoff")

    # test for having a signoff
    def testhasSignOff(self):
        commit = Commit()
        commit.commit_message = "has a signoff  Signed-off-by: John Mertic <jmertic@linuxfoundation.org>"
        self.assertTrue(commit.hasSignOff(), "Commit message had a signoff")

if __name__ == '__main__':
    unittest.main()
