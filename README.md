# DCO org check

Script to check a GitHub org for commits without a DCO signoff that should have one.

## Installation

```
git clone https://github.com/jmertic/dco-org-check
cd dco-org-check
chmod +x dco-org-check.py
pip install -r requirements.txt
```

## Usage

```
usage: dco-org-check.py [-h] [-c CONFIGFILE]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --config CONFIGFILE
                        name of YAML config file (defaults to
                        dco_org_check.yaml)
```

### Config file options ( set argument is the default if not specified )

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
# temp directory ( removed after run )
temp_dir: 'tmp'
```

## Contributing

Feel free to send [issues](/issues) or [pull requests](/pulls) ( with a DCO signoff of course :-) ) in accordance with the [contribution guidelines](CONTRIBUTING.md)

## Useful tools to make doing DCO signoffs easier

There are a number of great tools out there to manage DCO signoffs for developers to make it much easier to do signoffs.

- DCO command line tool, which let's you do a single signoff for an entire repo ( https://github.com/coderanger/dco )
- GitHub UI integrations for adding the signoff automatically ( https://github.com/scottrigby/dco-gh-ui )
  - Chrome - https://chrome.google.com/webstore/detail/dco-github-ui/onhgmjhnaeipfgacbglaphlmllkpoijo
  - Firefox - https://addons.mozilla.org/en-US/firefox/addon/scott-rigby/?src=search

SPDX-License-Identifier: Apache-2.0
