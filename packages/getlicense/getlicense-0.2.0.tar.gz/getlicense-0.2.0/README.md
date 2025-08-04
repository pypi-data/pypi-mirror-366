# GetLicense

<p align="center"><em>📖 A tool to quickly generate software license files with customizable project details</em>
    <br>
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/ashkanfeyzollahi/getlicense">
    <img alt="GitHub License" src="https://img.shields.io/github/license/ashkanfeyzollahi/getlicense">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/getlicense">
</p>

**getlicense** is a command-line tool that helps you easily choose and generate a license for your software project. It fetches license templates from an online repository, fills in basic project information (like organization name, project name, and copyright year), and saves the result as a LICENSE file. You can also cache templates for offline use and list available options directly from the terminal.

```
usage: getlicense [-h] [-L] [-l] [-n] [-c]
                  [--organization ORGANIZATION] [-o OUTPUT]
                  [--project PROJECT] [--year YEAR]
                  [license_name]

A tool to quickly generate software license files with customizable project details

positional arguments:
  license_name          Name of license template to fetch (e.g.,
                        mit, gpl3 and etc.)

options:
  -h, --help            show this help message and exit
  -L, --list-cached-templates
                        List cached license templates
  -l, --list-templates  List available license templates
  -n, --no-cache        Don't cache the license template file when
                        downloaded
  -c, --offline         Get the cached license template instead of
                        downloading
  --organization ORGANIZATION
                        The name of the organization or individual
                        who holds the copyright to the software
  -o, --output OUTPUT   Where to write the license template content
                        to
  --project PROJECT     The name of the software project
  --year YEAR           The year of the software's copyright
```

## Features

* Automatically fills in organization, project name, and year
* Caches license templates for offline use
* Can list available and cached license templates
* Customizable output location for the license file
* Interactive prompts with smart defaults

## Installation

- You can install it from `pypi` using `pip` (for Microsoft Windows):

```bash
pip install getlicense
```

- Or install it using `pipx` (recommended, for all):

```bash
pipx install getlicense 
```

- Or even build it from source!

```
git clone https://github.com/ashkanfeyzollahi/getlicense.git
cd getlicense
python -m build
pipx install dist/*
```