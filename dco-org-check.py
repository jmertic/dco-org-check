#!/usr/bin/env python3
#
# Script to check a GitHub org for commits without a DCO signoff that should have one.
#
# Loads config file ( dco_org_check.yaml ) for credentials
# token - GitHub access token
# org - Github org name
# csvfile - name of csvfile ( defaults to dco_issues.csv )
# dco_signoffs_directory - directory where previous commit signoffs are in the repo
# create_prior_commits_file - 1 if you want to have the script create the previous commits signoff files ( puts in directory named 'dco-signoffs')
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import re
import csv
import yaml
import io
import os
import sys
import base64

from github import Github

def loadconfig():
    try:
        with open("dco_org_check.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
    except:
        sys.exit("dco_org_check.yaml config file is not defined")


    if not 'token' in data_loaded:
        raise Exception('\'token\' is not defined')
    if not 'org' in data_loaded:
        raise Exception('\'org\' is not defined')
    if not 'csvfile' in data_loaded:
        data_loaded['csvfile'] = "dco_issues.csv"
    if not 'dco_signoffs_directory' in data_loaded:
        data_loaded['dco_signoffs_directory'] = "dco-signoffs"
    if not 'create_prior_commits_file' in data_loaded:
        data_loaded['create_prior_commits_file'] = 0

    return data_loaded

def has_sign_off(commit):
    return re.search("Signed-off-by: (.+)",commit.commit.message)

def get_past_signoffs(org,signoff_dir,g):
    results = g.search_code("org:"+org+" path:"+signoff_dir)

    signoffs = []
    for result in results:
        signoffs.append((result.repository.name,result.path,base64.b64decode(result.content)))

    return signoffs

def has_past_signoff(commit_url,signoffs):
    url_search = re.search("https://github.com/.*/(.*)/commit/(.*)",commit_url)
    repo = url_search.group(1)
    sha = url_search.group(2)

    for signoff in signoffs:
        if signoff[0] == repo:
            if not signoff[2].find(sha.encode()) == -1:
                return 1

    return 0;

def is_merge_commit(commit):
    if len(commit.parents) > 1 :
        return 1
    else:
        return 0

config = loadconfig();
csvfile = open(config['csvfile'], mode='w')
csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
g = Github(config['token'])

past_signoffs = get_past_signoffs(config['org'],config['dco_signoffs_directory'],g)

for repo in g.get_organization(config['org']).get_repos():
    for commit in repo.get_commits():
        if has_sign_off(commit):
            continue
        if is_merge_commit(commit):
            continue
        if has_past_signoff(commit.commit.html_url,past_signoffs):
            continue
        try:
            csv_writer.writerow([commit.commit.html_url,commit.commit.message,commit.commit.author.name,commit.commit.author.email,commit.commit.author.date])
        except GithubException as e:
            if e.status == 502:
                 csv_writer.writerow([commit.commit.html_url,commit.commit.message,commit.commit.author.name,commit.commit.author.email,commit.commit.author.date])

        if config['create_prior_commits_file']:
            if not os.path.exists('dco-signoffs'):
                os.mkdir('dco-signoffs')

            username = commit.commit.author.name
            email = commit.commit.author.email
            url_search = re.search("https://github.com/"+config['org']+"/(.*)/commit/(.*)",commit.commit.html_url)
            repo = url_search.group(1)
            sha = url_search.group(2)
            commitfilename = 'dco-signoffs/'+username+'-'+repo+'.txt'

            if not os.path.isfile(commitfilename):
                fh = open(commitfilename,  mode='w+')
                fh.write("I, "+username+" hereby sign-off-by all of my past commits to this repo subject to the Developer Certificate of Origin (DCO), Version 1.1. In the past I have used emails: "+email+"\n\n")
            else:
                fh = open(commitfilename,  mode='a')

            fh.write(sha+" "+commit.commit.message+"\n")
            fh.close()
