# Kabinet

[![codecov](https://codecov.io/gh/jhnnsrs/kabinet/branch/main/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/kabinet)
[![PyPI version](https://badge.fury.io/py/kabinet.svg)](https://pypi.org/project/kabinet/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/kabinet/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/kabinet.svg)](https://pypi.python.org/pypi/kabinet/)
[![PyPI status](https://img.shields.io/pypi/status/kabinet.svg)](https://pypi.python.org/pypi/kabinet/)
[![PyPI download month](https://img.shields.io/pypi/dm/kabinet.svg)](https://pypi.python.org/pypi/kabinet/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/jhnnsrs/kabinet)


## Kabinet

Kabinet is a tool for managing and deploying applications installable applications for the arkitekt framework. It is the
successto to the port spec.

## Installation

You can install Kabinet via pip:

```bash
pip install kabinet
```


## Usage

This client can be use to manage and retrive defintions of applications on the arkitekt server. Currently, its mainly
tide to the arkitekt platform and we wouldn't recommend using it outside of its orignal scope just yet.

```python
from arkitekt_next import easy
from kabient.api.schema import create_github_repo

with easy():

    repo = create_github_repo(
        name=" A new repo",
        identifier="jhnnsrs/kabinet:main", 
    )

    print(repo) # will print the repo with all appimages that are in the repo


```

