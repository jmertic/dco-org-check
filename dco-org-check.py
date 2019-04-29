#!/usr/bin/env python3
#
# Script to check a GitHub org for commits without a DCO signoff that should have one.
#
# Loads config file ( dco_org_check.yaml ) for credentials
# token - GitHub access token
# org - Github org name
# csvfile - name of csvfile ( defaults to dco_issues.csv )
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import re
import csv
import yaml
import io

from github import Github

def loadconfig():
    with open("dco_org_check.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    if not data_loaded['token']:
        raise Exception('\'token\' is not defined')
    if not data_loaded['org']:
        raise Exception('\'org\' is not defined')
    if not data_loaded['csvfile']:
        data_loaded['csvfile'] = "dco_issues.csv"

    return data_loaded

def has_sign_off(commit):
    return re.search("Signed-off-by: (.+)",commit.commit.message)

def is_merge_commit(commit):
    if len(commit.parents) > 1 :
        return 1
    else:
        return 0

config = loadconfig();
csvfile = open(config['csvfile'], mode='w')
csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
g = Github(config['token'])

for repo in g.get_organization(config['org']).get_repos():
    for commit in repo.get_commits():
        if has_sign_off(commit):
            continue
        if is_merge_commit(commit):
            continue

        try:
            csv_writer.writerow([commit.commit.html_url,commit.commit.message,commit.commit.author.name,commit.commit.author.email,commit.commit.author.date])
        except GithubException as e:
            if e.status == 502:
                 csv_writer.writerow([commit.commit.html_url,commit.commit.message,commit.commit.author.name,commit.commit.author.email,commit.commit.author.date])
