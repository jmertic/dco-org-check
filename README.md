# DCO org check

Script to check a GitHub org for commits without a DCO signoff that should have one.

Loads config file ( defaults to dco_org_check.yaml, or specify at the command line after -c ) for credentials

## Config file options ( set argument is the default if not specified )

```yaml
# GitHub access token ( required )
token:
# Github org name ( required )
org:
# name of csvfile
csvfile: dco_issues.csv
# list of directory names where previous commit signoffs are in the repo
dco_signoffs_directories:
  - dco-signoffs
# set to 1 if you want to have the script create the previous commits signoff files
create_prior_commits_file: 1
# directory where to store the prior commits files
create_prior_commits_dir: dco-signoffs
# list of repos to ignore when scanning
ignore_repos:
  - repo1
  - repo2
  - ...
# list of repos to only look at when scanning
only_repos:
  - repo1
  - repo2
  - ...
```

## Useful tools to make doing DCO signoffs easier

- DCO command line tool, which let's you do a single signoff for an entire repo ( https://github.com/coderanger/dco )
- GitHub UI integrations for adding the signoff Automatically
  - Chrome - https://chrome.google.com/webstore/detail/dco-github-ui/onhgmjhnaeipfgacbglaphlmllkpoijo
  - Firefox - https://addons.mozilla.org/en-US/firefox/addon/scott-rigby/?src=search

SPDX-License-Identifier: Apache-2.0
