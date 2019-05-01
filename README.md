Script to check a GitHub org for commits without a DCO signoff that should have one.

Loads config file ( defaults to dco_org_check.yaml, or specify at the command line after -c ) for credentials

* token - GitHub access token
* org - Github org name
* csvfile - name of csvfile ( defaults to dco_issues.csv )
* dco_signoffs_directory - directory where previous commit signoffs are in the repo
* create_prior_commits_file - 1 if you want to have the script create the previous commits signoff files ( puts in directory named 'dco-signoffs')
* ignore_repos - list of repos to ignore when scanning
* only_repos - list of repos to only look at when scanning

SPDX-License-Identifier: Apache-2.0
