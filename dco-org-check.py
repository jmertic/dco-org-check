#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import re
import csv
import io
import os
import sys
import base64
import shutil
import time
import socket
from argparse import ArgumentParser
from datetime import datetime

# third party modules
import yaml
import git
from github import Github, GithubException, RateLimitExceededException

class Config():
    token = ''
    org = ''
    csvfile = ''
    dco_signoffs_directories = ["dco-signoffs"]
    create_prior_commits_file = 0
    create_prior_commits_dir = 'dco-signoffs'
    skip_archives = 0
    ignore_repos = []
    only_repos = []
    temp_dir = 'tmp'
    signoffs = []

    def __init__(self, config_file = ''):

        if config_file != '' and os.path.isfile(config_file):
            try:
                with open(config_file, 'r') as stream:
                    data_loaded = yaml.safe_load(stream)
            except:
                sys.exit(config_file+" config file is not defined")

            if not 'token' in data_loaded:
                if 'GITHUB_TOKEN' in os.environ:
                    self.token = os.environ['GITHUB_TOKEN']
                else:
                    raise Exception('Github token is not defined. Set \'token\' in '+config_file+' or set GITHUB_TOKEN environment variable to a valid Github token')
            else:
                self.token = data_loaded['token']
            if not 'org' in data_loaded:
                raise Exception('\'org\' is not defined')
            else:
                self.org = data_loaded['org']

            if 'csvfile' in data_loaded:
                self.csvfile = data_loaded['csvfile']
            if 'dco_signoffs_directories' in data_loaded:
                self.dco_signoffs_directories = data_loaded['dco_signoffs_directories']
            if 'create_prior_commits_file' in data_loaded:
                self.create_prior_commits_file = data_loaded['create_prior_commits_file']
            if 'create_prior_commits_dir' in data_loaded:
                self.create_prior_commits_dir = data_loaded['create_prior_commits_dir']
            if 'skip_archives' in data_loaded:
                self.skip_archives = data_loaded['skip_archives']
            if 'temp_dir' in data_loaded:
                self.temp_dir = data_loaded['temp_dir']
            if 'ignore_repos' in data_loaded:
                self.ignore_repos = data_loaded['ignore_repos']
            if 'only_repos' in data_loaded:
                self.only_repos = data_loaded['only_repos']

    def __del__(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir,1)

    def cleanupPreviousRun(self):
        if os.path.isfile(self.csvfile):
            os.remove(self.csvfile)
        if self.create_prior_commits_file:
            shutil.rmtree(self.create_prior_commits_file,1)
        if os.path.exists(self.create_prior_commits_dir):
            shutil.rmtree(self.create_prior_commits_dir,1)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir,1)

    def scanRepo(self, reponame, is_archived):
        if len(self.only_repos) > 0:
            if not reponame in self.only_repos:
                return False
        # Check if there are ignore repos defined
        if len(self.ignore_repos) > 0:
            if reponame in self.ignore_repos:
                return False
        if self.skip_archives and is_archived:
            return False

        return True

    def getRepos(self):
        repos = []

        g = Github(login_or_token=self.token, per_page=1000)
        try:
            gh_repos = g.get_organization(self.org).get_repos()
            for gh_repo in gh_repos:
                repos.append(
                    Repo(
                        gh_repo.name,
                        gh_repo.html_url,
                        gh_repo.archived,
                        self.dco_signoffs_directories,
                        self.temp_dir
                    )
                )
        except RateLimitExceededException:
            print("Sleeping until we get past the API rate limit....")
            time.sleep(g.rate_limiting_resettime-now())
        except GithubException as e:
            if e.status == 502:
                print("Server error - retrying...")
            else:
                print(e.data)
        except socket.timeout:
            print("Server error - retrying...")

        return repos

class Commit():
    sha = ''
    html_url = ''
    commit_message = ''
    author_name = ''
    author_email = ''
    author_date = ''
    is_merge_commit = False
    repo_name = ''
    org_name = ''

    def __init__(self, commitObject = None, repo_html_url = ''):
        if ( commitObject and str(type(commitObject)) ==  "<class 'git.objects.commit.Commit'>" ):
            self.sha = commitObject.hexsha
            self.html_url = repo_html_url+'/commit/'+commitObject.hexsha
            self.commit_message = commitObject.message
            self.author_name = commitObject.author.name
            self.author_email = commitObject.author.email
            self.author_date = commitObject.authored_datetime
            self.is_merge_commit = len(commitObject.parents) > 1

        url_search = re.search("https://github.com/(.*)/(.*)/commit/.*",self.html_url)
        if url_search:
            self.repo_name = url_search.group(2)
            self.org_name = url_search.group(1)

    def hasSignOff(self):
        return re.search("Signed-off-by: (.+)",self.commit_message)

    def hasPastSignoff(self,signoffs):
        url_search = re.search("https://github.com/.*/(.*)/commit/(.*)",self.html_url)
        repo = url_search.group(1)
        sha = url_search.group(2)

        for signoff in signoffs:
            if not signoff[1].find(sha.encode()) == -1:
                return 1

        return 0;

class DCOOutput():
    csv_writer = None
    create_prior_commits_file = False
    create_prior_commits_dir = ''

    def __init__(self, csvfile, create_prior_commits_file = False, create_prior_commits_dir = ''):
        self.create_prior_commits_file = create_prior_commits_file
        self.create_prior_commits_dir = create_prior_commits_dir

        csvfile = open(csvfile, mode='w')
        self.csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    def writeCommit(self, commit):
        self.csv_writer.writerow([
            commit.html_url,
            commit.commit_message,
            commit.author_name,
            commit.author_email,
            commit.author_date
            ])

        if ( self.create_prior_commits_file ):
            self.writePriorCommitsFile(commit)

    def writePriorCommitsFile(self, commit):
        if not os.path.exists(self.create_prior_commits_dir):
            os.mkdir(self.create_prior_commits_dir)
        if not os.path.exists(self.create_prior_commits_dir+'/'+commit.repo_name):
            os.mkdir(self.create_prior_commits_dir+'/'+commit.repo_name)

        commitfilename = self.create_prior_commits_dir+'/'+commit.repo_name+'/'+commit.author_name+'-'+commit.repo_name+'.txt'

        if not os.path.isfile(commitfilename):
            fh = open(commitfilename,  mode='w+')
            fh.write("I, "+commit.author_name+" hereby sign-off-by all of my past commits to this repo subject to the Developer Certificate of Origin (DCO), Version 1.1. In the past I have used emails: "+commit.author_email+"\n\n")
        else:
            fh = open(commitfilename,  mode='a')

        fh.write(commit.sha+" "+commit.commit_message+"\n")
        fh.close()

class Repo():
    name = ''
    html_url = ''
    archived = False
    dco_signoffs_directories = ["dco-signoffs"]
    temp_dir = 'tmp'
    past_signoffs = []

    def __init__(self, name, html_url, archived = False, dco_signoffs_directories = ["dco-signoffs"], temp_dir = 'tmp'):
        self.name = name
        self.html_url = html_url
        self.archived = archived
        self.dco_signoffs_directories = dco_signoffs_directories
        self.temp_dir = temp_dir

    def getCommits(self, loadPastCommits = True):
        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)
        gitrepo = git.Repo.clone_from(self.html_url,self.temp_dir+'/'+self.name)

        # lazy load in the past commits
        if loadPastCommits:
            for entry in gitrepo.heads.master.commit.tree:
                if entry.type == 'tree' and entry.name in self.dco_signoffs_directories:
                    for file in entry.blobs:
                        with open(self.temp_dir+'/'+self.name+'/'+file.path, 'rb') as content_file:
                            content = content_file.read()
                        self.past_signoffs.append([file.path,content])

        return gitrepo.iter_commits()

def main():

    startTime = datetime.now()

    parser = ArgumentParser()
    parser.add_argument("-c", "--config", dest="configfile", default="dco_org_check.yaml", help="name of YAML config file (defaults to dco_org_check.yaml)")
    args = parser.parse_args()

    config = Config(args.configfile)
    config.cleanupPreviousRun()

    dcoOut = DCOOutput(config.csvfile, config.create_prior_commits_file, config.create_prior_commits_dir)

    for repo in config.getRepos():
        # Check if we are only looking at certain repos
        if ( not config.scanRepo(repo.name, repo.archived) ):
            continue

        print("Searching repo {}...".format(repo.name))
        # Parse commits
        for commitObject in repo.getCommits():
            commit = Commit(commitObject,repo.html_url)
            if commit.hasSignOff():
                continue
            if commit.is_merge_commit:
                continue
            if commit.hasPastSignoff(repo.past_signoffs):
                continue

            dcoOut.writeCommit(commit)

    print("This took "+str(datetime.now() - startTime))

if __name__ == '__main__':
    main()
